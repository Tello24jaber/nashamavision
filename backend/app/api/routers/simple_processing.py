"""
Simple Processing Router
Manual video processing without Celery/Redis requirement
Processes video to detect players and generate 2D pitch visualization
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID
import logging
import tempfile
import json
import time
import gc
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import cv2
import numpy as np

from app.db.session import get_db
from app.models.models import Video, Track as TrackModel, TrackPoint, ObjectClass, TeamSide
from app.schemas.schemas import ProcessingStatusResponse
from app.storage.storage_interface import get_storage

# Import for SORT tracker
from filterpy.kalman import KalmanFilter
from scipy.optimize import linear_sum_assignment

router = APIRouter()
logger = logging.getLogger(__name__)

# Global processing status tracker (in-memory for simplicity)
processing_status: Dict[str, Dict[str, Any]] = {}


class SimpleDetector:
    """
    Enhanced YOLO-based player detector with color analysis.
    - Extracts dominant shirt color for team classification
    - Filters out referees (black shirts)
    - Provides consistent color features for better tracking
    """
    
    def __init__(self):
        self.model = None
        self.use_yolo = False
        self._load_model()
    
    def _load_model(self):
        """Try to load YOLO model"""
        try:
            from ultralytics import YOLO
            # Use pre-trained YOLOv8 model - it will auto-download
            self.model = YOLO("yolov8n.pt")  # nano model for speed
            self.use_yolo = True
            logger.info("YOLO model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load YOLO model: {e}. Using fallback detection.")
            self.use_yolo = False
    
    def _get_dominant_color(self, frame: np.ndarray, bbox: List[int]) -> Dict:
        """
        Extract dominant color from upper body (shirt area).
        Returns color info for team classification.
        """
        x1, y1, x2, y2 = bbox
        h = y2 - y1
        w = x2 - x1
        
        # Focus on upper body (shirt area) - top 40% of detection
        shirt_y1 = y1 + int(h * 0.15)  # Skip head
        shirt_y2 = y1 + int(h * 0.5)   # Upper body only
        shirt_x1 = x1 + int(w * 0.2)   # Skip arms
        shirt_x2 = x2 - int(w * 0.2)
        
        # Ensure bounds are valid
        shirt_y1 = max(0, shirt_y1)
        shirt_y2 = min(frame.shape[0], shirt_y2)
        shirt_x1 = max(0, shirt_x1)
        shirt_x2 = min(frame.shape[1], shirt_x2)
        
        if shirt_y2 <= shirt_y1 or shirt_x2 <= shirt_x1:
            return {'rgb': (128, 128, 128), 'hsv': (0, 0, 128), 'is_dark': False, 'team': 'unknown'}
        
        # Extract shirt region
        shirt_region = frame[shirt_y1:shirt_y2, shirt_x1:shirt_x2]
        
        if shirt_region.size == 0:
            return {'rgb': (128, 128, 128), 'hsv': (0, 0, 128), 'is_dark': False, 'team': 'unknown'}
        
        # Convert to HSV for better color analysis
        hsv_region = cv2.cvtColor(shirt_region, cv2.COLOR_BGR2HSV)
        
        # Calculate average color
        avg_bgr = np.mean(shirt_region, axis=(0, 1))
        avg_hsv = np.mean(hsv_region, axis=(0, 1))
        
        avg_rgb = (int(avg_bgr[2]), int(avg_bgr[1]), int(avg_bgr[0]))  # BGR to RGB
        
        # Check if it's a dark color (referee detection)
        brightness = avg_hsv[2]  # V in HSV
        saturation = avg_hsv[1]  # S in HSV
        is_dark = brightness < 60 and saturation < 80  # Dark and desaturated = black/dark gray
        
        # Classify team based on dominant hue
        hue = avg_hsv[0]
        team = 'unknown'
        
        if is_dark:
            team = 'referee'
        elif saturation < 50:
            # Low saturation = white or gray
            if brightness > 180:
                team = 'team_white'
            else:
                team = 'unknown'
        else:
            # Color-based classification
            # Red: hue 0-10 or 170-180
            # Green: hue 35-85  
            # Blue: hue 100-130
            # Yellow: hue 20-35
            if hue < 10 or hue > 170:
                team = 'team_red'
            elif 35 <= hue <= 85:
                team = 'team_green'
            elif 100 <= hue <= 130:
                team = 'team_blue'
            elif 20 <= hue < 35:
                team = 'team_yellow'
            else:
                team = 'team_other'
        
        return {
            'rgb': avg_rgb,
            'hsv': (int(avg_hsv[0]), int(avg_hsv[1]), int(avg_hsv[2])),
            'is_dark': is_dark,
            'team': team,
            'brightness': int(brightness),
            'saturation': int(saturation)
        }
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect players in a frame.
        Lower confidence threshold to catch more players.
        Returns list of detections with bbox and confidence.
        """
        detections = []
        
        if self.use_yolo and self.model:
            try:
                # Very low confidence to detect all players including far/occluded ones
                results = self.model.predict(frame, conf=0.15, verbose=False)
                
                for result in results:
                    boxes = result.boxes
                    for i in range(len(boxes)):
                        class_id = int(boxes.cls[i].cpu().numpy())
                        # Class 0 = person in COCO dataset
                        if class_id == 0:
                            box = boxes.xyxy[i].cpu().numpy()
                            x1, y1, x2, y2 = map(int, box)
                            confidence = float(boxes.conf[i].cpu().numpy())
                            
                            # Don't filter - detect all people and let tracker handle it
                            # The tracker will naturally keep consistent players
                            
                            detections.append({
                                'bbox': [x1, y1, x2, y2],
                                'confidence': confidence,
                                'class': 'player',
                                'center_x': (x1 + x2) / 2,
                                'center_y': (y1 + y2) / 2
                            })
                
            except Exception as e:
                logger.error(f"YOLO detection error: {e}")
        
        return detections


class KalmanBoxTracker:
    """
    Single object tracker using Kalman Filter.
    Tracks a bounding box in format [x1, y1, x2, y2].
    
    State vector: [x_center, y_center, scale, aspect_ratio, vx, vy, vs]
    - x_center, y_center: center of bbox
    - scale: area of bbox  
    - aspect_ratio: width/height ratio
    - vx, vy, vs: velocities
    """
    count = 0
    
    def __init__(self, bbox):
        """
        Initialize tracker with bounding box [x1, y1, x2, y2]
        """
        # Kalman filter with 7 state variables and 4 measurements
        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        
        # State transition matrix (constant velocity model)
        self.kf.F = np.array([
            [1, 0, 0, 0, 1, 0, 0],  # x = x + vx
            [0, 1, 0, 0, 0, 1, 0],  # y = y + vy
            [0, 0, 1, 0, 0, 0, 1],  # s = s + vs
            [0, 0, 0, 1, 0, 0, 0],  # r = r (aspect ratio constant)
            [0, 0, 0, 0, 1, 0, 0],  # vx = vx
            [0, 0, 0, 0, 0, 1, 0],  # vy = vy
            [0, 0, 0, 0, 0, 0, 1]   # vs = vs
        ])
        
        # Measurement matrix (we observe x, y, s, r)
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]
        ])
        
        # Measurement noise - reduced for more stable tracking
        self.kf.R[2:, 2:] *= 5.0
        
        # Initial covariance - trust initial position more
        self.kf.P[4:, 4:] *= 500.0  # Moderate uncertainty for velocities
        self.kf.P *= 5.0
        
        # Process noise - very low for smooth predictions
        self.kf.Q[-1, -1] *= 0.001
        self.kf.Q[4:, 4:] *= 0.001
        
        # Initialize state from bbox
        self.kf.x[:4] = self._bbox_to_z(bbox)
        
        self.time_since_update = 0
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.history = []
        self.hits = 0
        self.hit_streak = 0
        self.age = 0
        self.first_frame = 0
        self.points = []  # Store detection history
    
    def _bbox_to_z(self, bbox):
        """Convert [x1, y1, x2, y2] to [x_center, y_center, scale, aspect_ratio]"""
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = bbox[0] + w / 2.0
        y = bbox[1] + h / 2.0
        s = w * h  # scale = area
        r = w / float(h) if h > 0 else 1.0
        return np.array([x, y, s, r]).reshape((4, 1))
    
    def _z_to_bbox(self, z):
        """Convert [x_center, y_center, scale, aspect_ratio] to [x1, y1, x2, y2]"""
        w = np.sqrt(z[2] * z[3])
        h = z[2] / w if w > 0 else 0
        return np.array([
            z[0] - w / 2.0,
            z[1] - h / 2.0,
            z[0] + w / 2.0,
            z[1] + h / 2.0
        ]).flatten()
    
    def update(self, bbox):
        """Update state with observed bbox"""
        self.time_since_update = 0
        self.history = []
        self.hits += 1
        self.hit_streak += 1
        self.kf.update(self._bbox_to_z(bbox))
    
    def predict(self):
        """Predict next state and return predicted bbox"""
        # Prevent negative scale
        if self.kf.x[6] + self.kf.x[2] <= 0:
            self.kf.x[6] = 0.0
        
        self.kf.predict()
        self.age += 1
        
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1
        
        self.history.append(self._z_to_bbox(self.kf.x[:4]))
        return self.history[-1]
    
    def get_state(self):
        """Get current bbox estimate"""
        return self._z_to_bbox(self.kf.x[:4])


def iou_batch(bb_test, bb_gt):
    """
    Compute IoU between all pairs of boxes.
    bb_test: (N, 4) array of bboxes
    bb_gt: (M, 4) array of bboxes
    Returns: (N, M) array of IoU values
    """
    bb_gt = np.expand_dims(bb_gt, 0)
    bb_test = np.expand_dims(bb_test, 1)
    
    xx1 = np.maximum(bb_test[..., 0], bb_gt[..., 0])
    yy1 = np.maximum(bb_test[..., 1], bb_gt[..., 1])
    xx2 = np.minimum(bb_test[..., 2], bb_gt[..., 2])
    yy2 = np.minimum(bb_test[..., 3], bb_gt[..., 3])
    
    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)
    wh = w * h
    
    area_test = (bb_test[..., 2] - bb_test[..., 0]) * (bb_test[..., 3] - bb_test[..., 1])
    area_gt = (bb_gt[..., 2] - bb_gt[..., 0]) * (bb_gt[..., 3] - bb_gt[..., 1])
    
    iou = wh / (area_test + area_gt - wh + 1e-6)
    return iou


def associate_detections_to_trackers(detections, trackers, iou_threshold=0.3):
    """
    Assign detections to tracked objects using Hungarian algorithm.
    Returns 3 lists: matches, unmatched_detections, unmatched_trackers
    """
    if len(trackers) == 0:
        return np.empty((0, 2), dtype=int), np.arange(len(detections)), np.empty((0,), dtype=int)
    
    if len(detections) == 0:
        return np.empty((0, 2), dtype=int), np.empty((0,), dtype=int), np.arange(len(trackers))
    
    # Compute IoU matrix
    iou_matrix = iou_batch(detections, trackers)
    
    # Use Hungarian algorithm to find optimal assignment
    if min(iou_matrix.shape) > 0:
        # Convert to cost matrix (1 - IoU)
        cost_matrix = 1 - iou_matrix
        row_indices, col_indices = linear_sum_assignment(cost_matrix)
        matched_indices = np.array(list(zip(row_indices, col_indices)))
    else:
        matched_indices = np.empty((0, 2), dtype=int)
    
    # Filter matches with low IoU
    unmatched_detections = []
    for d in range(len(detections)):
        if d not in matched_indices[:, 0]:
            unmatched_detections.append(d)
    
    unmatched_trackers = []
    for t in range(len(trackers)):
        if t not in matched_indices[:, 1]:
            unmatched_trackers.append(t)
    
    # Filter out matched with low IoU
    matches = []
    for m in matched_indices:
        if iou_matrix[m[0], m[1]] < iou_threshold:
            unmatched_detections.append(m[0])
            unmatched_trackers.append(m[1])
        else:
            matches.append(m.reshape(1, 2))
    
    if len(matches) == 0:
        matches = np.empty((0, 2), dtype=int)
    else:
        matches = np.concatenate(matches, axis=0)
    
    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)


class Sort:
    """
    SORT: Simple Online and Realtime Tracking
    
    A proper multi-object tracker that:
    - Uses Kalman Filter for motion prediction
    - Uses Hungarian algorithm for optimal detection-to-track assignment
    - Maintains consistent IDs throughout the video
    """
    
    def __init__(self, max_age=150, min_hits=1, iou_threshold=0.15):
        """
        Args:
            max_age: Maximum frames to keep track without detection (150 = 5 seconds @ 30fps)
            min_hits: Minimum detections before track is confirmed (1 = immediate tracking)
            iou_threshold: Minimum IoU for match (0.15 = very permissive for occluded players)
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers: List[KalmanBoxTracker] = []
        self.frame_count = 0
        self.all_tracks_history: Dict[int, Dict] = {}  # Store complete track history
    
    def update(self, detections: List[Dict], frame_num: int) -> List[Dict]:
        """
        Update tracker with detections for current frame.
        
        Args:
            detections: List of detections with 'bbox' key
            frame_num: Current frame number
            
        Returns:
            List of tracked objects with track_id
        """
        self.frame_count = frame_num
        
        # Get predicted locations from existing trackers
        trks = np.zeros((len(self.trackers), 4))
        to_del = []
        
        for t, trk in enumerate(self.trackers):
            pos = trk.predict()
            trks[t] = pos
            if np.any(np.isnan(pos)):
                to_del.append(t)
        
        # Remove invalid trackers
        for t in reversed(to_del):
            self.trackers.pop(t)
        trks = np.ma.compress_rows(np.ma.masked_invalid(trks))
        
        # Convert detections to numpy array
        if len(detections) > 0:
            dets = np.array([d['bbox'] for d in detections])
        else:
            dets = np.empty((0, 4))
        
        # Associate detections to trackers
        matched, unmatched_dets, unmatched_trks = associate_detections_to_trackers(
            dets, trks, self.iou_threshold
        )
        
        # Update matched trackers with assigned detections
        for m in matched:
            det_idx, trk_idx = m[0], m[1]
            det = detections[det_idx]
            self.trackers[trk_idx].update(det['bbox'])
            
            # Store point in history
            track_id = self.trackers[trk_idx].id
            if track_id not in self.all_tracks_history:
                self.all_tracks_history[track_id] = {
                    'first_frame': frame_num,
                    'last_frame': frame_num,
                    'points': []
                }
            
            bbox = self.trackers[trk_idx].get_state()
            self.all_tracks_history[track_id]['points'].append({
                'frame': frame_num,
                'bbox': bbox.tolist(),
                'center_x': (bbox[0] + bbox[2]) / 2,
                'center_y': (bbox[1] + bbox[3]) / 2,
                'confidence': det['confidence']
            })
            self.all_tracks_history[track_id]['last_frame'] = frame_num
        
        # Create new trackers for unmatched detections
        for i in unmatched_dets:
            det = detections[i]
            trk = KalmanBoxTracker(det['bbox'])
            trk.first_frame = frame_num
            self.trackers.append(trk)
            
            # Initialize history for new track
            track_id = trk.id
            bbox = trk.get_state()
            self.all_tracks_history[track_id] = {
                'first_frame': frame_num,
                'last_frame': frame_num,
                'points': [{
                    'frame': frame_num,
                    'bbox': bbox.tolist(),
                    'center_x': (bbox[0] + bbox[2]) / 2,
                    'center_y': (bbox[1] + bbox[3]) / 2,
                    'confidence': det['confidence']
                }]
            }
        
        # Build output - return confirmed tracks
        ret = []
        for trk in self.trackers:
            if trk.time_since_update <= 1 and (trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits):
                bbox = trk.get_state()
                ret.append({
                    'track_id': trk.id,
                    'bbox': bbox.tolist(),
                    'center_x': (bbox[0] + bbox[2]) / 2,
                    'center_y': (bbox[1] + bbox[3]) / 2,
                    'confidence': 1.0
                })
        
        # Remove dead trackers
        self.trackers = [trk for trk in self.trackers if trk.time_since_update <= self.max_age]
        
        return ret
    
    def get_all_tracks(self) -> List[Dict]:
        """
        Get all valid tracks with their complete history.
        """
        valid_tracks = []
        
        # Log all tracks for debugging
        logger.info(f"Total tracks in history: {len(self.all_tracks_history)}")
        for track_id, track_data in self.all_tracks_history.items():
            num_points = len(track_data['points'])
            track_duration = track_data['last_frame'] - track_data['first_frame']
            logger.info(f"Track {track_id}: {num_points} points, duration {track_duration} frames")
        
        for track_id, track_data in self.all_tracks_history.items():
            num_points = len(track_data['points'])
            track_duration = track_data['last_frame'] - track_data['first_frame']
            
            # VERY permissive: at least 3 detections (down from 10)
            # This will keep almost all tracks for debugging
            if num_points >= 3:
                valid_tracks.append({
                    'track_id': track_id,
                    'first_frame': track_data['first_frame'],
                    'last_frame': track_data['last_frame'],
                    'points': track_data['points'],
                    'avg_confidence': sum(p['confidence'] for p in track_data['points']) / num_points
                })
                logger.info(f"✓ Keeping track {track_id} with {num_points} points")
            else:
                logger.info(f"✗ Rejecting track {track_id} with only {num_points} points")
        
        # Sort by first appearance and assign sequential display IDs
        valid_tracks.sort(key=lambda t: t['first_frame'])
        for i, track in enumerate(valid_tracks):
            track['display_id'] = i + 1
        
        logger.info(f"SORT generated {len(valid_tracks)} valid tracks from {len(self.all_tracks_history)} total")
        return valid_tracks


# Alias for backward compatibility
SimpleTracker = Sort


def process_video_sync(video_id: str, db_session_factory):
    """
    Synchronous video processing function
    Runs in background task
    """
    from app.db.session import SessionLocal
    import time
    import shutil
    import gc
    
    db = SessionLocal()
    local_video_path = None
    temp_dir = None
    cap = None
    
    try:
        video = db.query(Video).filter(Video.id == UUID(video_id)).first()
        if not video:
            logger.error(f"Video {video_id} not found")
            processing_status[video_id] = {'status': 'failed', 'progress': 0, 'error': 'Video not found'}
            return
        
        # Update status to processing
        video.status = 'processing'
        video.processing_started_at = datetime.utcnow()
        db.commit()
        
        processing_status[video_id] = {'status': 'processing', 'progress': 5, 'error': None}
        logger.info(f"Starting processing for video {video_id}")
        
        # Download video from storage - use manual temp directory
        storage = get_storage()
        temp_dir = Path(tempfile.gettempdir()) / f"nashama_{video_id}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        local_video_path = temp_dir / f"{video_id}.mp4"
        
        processing_status[video_id] = {'status': 'processing', 'progress': 10, 'error': None, 'step': 'Downloading video'}
        logger.info(f"Downloading video from storage: {video.storage_path}")
        storage.download_file(video.storage_path, str(local_video_path))
        
        # Open video
        cap = cv2.VideoCapture(str(local_video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {local_video_path}")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        logger.info(f"Video: {width}x{height} @ {fps}fps, {total_frames} frames")
        
        # Initialize detector and tracker
        processing_status[video_id] = {'status': 'processing', 'progress': 15, 'error': None, 'step': 'Loading AI model'}
        detector = SimpleDetector()
        tracker = SimpleTracker()
        
        # Process ALL frames of the video for complete tracking
        # Sample at higher rate for continuous tracking
        sample_interval = max(1, int(fps / 15))  # ~15 frames per second for continuous tracking
        max_frames_to_process = total_frames  # Process entire video
        
        frame_num = 0
        processed_frames = 0
        all_frame_data = []
        
        processing_status[video_id] = {'status': 'processing', 'progress': 20, 'error': None, 'step': 'Detecting players'}
        
        total_detections = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_num % sample_interval == 0 and processed_frames < max_frames_to_process:
                # Detect players
                detections = detector.detect(frame)
                total_detections += len(detections)
                
                # Log first few frames for debugging
                if processed_frames < 5:
                    logger.info(f"Frame {frame_num}: {len(detections)} detections")
                
                # Track players
                tracked = tracker.update(detections, frame_num)
                
                if processed_frames < 5:
                    logger.info(f"Frame {frame_num}: {len(tracked)} active tracks")
                
                # Store frame data
                all_frame_data.append({
                    'frame': frame_num,
                    'timestamp': frame_num / fps,
                    'detections': tracked
                })
                
                processed_frames += 1
                
                # Update progress (20-80% range for detection)
                progress = 20 + int(60 * (processed_frames / max_frames_to_process))
                processing_status[video_id] = {
                    'status': 'processing', 
                    'progress': progress, 
                    'error': None,
                    'step': f'Processing frame {processed_frames}/{max_frames_to_process}'
                }
            
            frame_num += 1
            
            if processed_frames >= max_frames_to_process:
                break
        
        # Release video capture properly
        cap.release()
        cap = None
        gc.collect()  # Force garbage collection
        time.sleep(1)  # Wait for file handle to release (Windows)
        
        logger.info(f"Processed {processed_frames} frames")
        logger.info(f"Total detections across all frames: {total_detections}")
        logger.info(f"Raw tracks in history: {len(tracker.all_tracks_history)} tracks")
        
        # Save tracks to database
        processing_status[video_id] = {'status': 'processing', 'progress': 85, 'error': None, 'step': 'Saving to database'}
        
        tracks = tracker.get_all_tracks()
        logger.info(f"Filtered to {len(tracks)} valid player tracks")
        
        # Delete existing tracks for this video - do it properly
        existing_tracks = db.query(TrackModel).filter(TrackModel.video_id == UUID(video_id)).all()
        for existing_track in existing_tracks:
            # Delete track points first
            db.query(TrackPoint).filter(TrackPoint.track_id == existing_track.id).delete()
        # Now delete the tracks
        db.query(TrackModel).filter(TrackModel.video_id == UUID(video_id)).delete()
        db.commit()  # Commit the deletions before inserting new ones
        
        # Save tracks to database
        for track_data in tracks:
            track = TrackModel(
                video_id=UUID(video_id),
                track_id=track_data['display_id'],  # Use display_id (1, 2, 3...)
                object_class='player',
                team_side='unknown',
                first_frame=track_data['first_frame'],
                last_frame=track_data['last_frame'],
                total_detections=len(track_data['points'])
            )
            db.add(track)
            db.flush()
            
            # Add track points
            for point in track_data['points']:
                track_point = TrackPoint(
                    track_id=track.id,
                    frame_number=int(point['frame']),
                    timestamp=float(point['frame']) / fps,
                    bbox_x1=float(point['bbox'][0]),
                    bbox_y1=float(point['bbox'][1]),
                    bbox_x2=float(point['bbox'][2]),
                    bbox_y2=float(point['bbox'][3]),
                    confidence=float(point['confidence']),
                    x_px=float(point['center_x']),
                    y_px=float(point['center_y'])
                )
                db.add(track_point)
        
        db.commit()
        logger.info(f"Saved {len(tracks)} tracks to database")
        
        # Update video status to completed
        video.status = 'completed'
        video.processing_completed_at = datetime.utcnow()
        db.commit()
        
        processing_status[video_id] = {
            'status': 'completed', 
            'progress': 100, 
            'error': None,
            'result': {
                'tracks_found': len(tracks),
                'frames_processed': processed_frames,
                'total_detections': sum(len(t['points']) for t in tracks)
            }
        }
        
        logger.info(f"Successfully completed processing for video {video_id}")
            
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {e}", exc_info=True)
        processing_status[video_id] = {'status': 'failed', 'progress': 0, 'error': str(e)}
        
        # Update video status to failed
        try:
            video = db.query(Video).filter(Video.id == UUID(video_id)).first()
            if video:
                video.status = 'failed'
                video.processing_error = str(e)
                db.commit()
        except:
            pass
    finally:
        # Clean up video capture if still open
        if cap is not None:
            try:
                cap.release()
            except:
                pass
        
        # Clean up temp directory
        if temp_dir and temp_dir.exists():
            try:
                time.sleep(1)  # Extra wait on Windows
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as cleanup_err:
                logger.warning(f"Could not clean up temp directory: {cleanup_err}")
        
        db.close()


@router.post("/process/{video_id}", response_model=ProcessingStatusResponse)
async def process_video_simple(
    video_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start simple video processing (no Redis/Celery required)
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )
    
    vid_str = str(video_id)
    if vid_str in processing_status and processing_status[vid_str].get('status') == 'processing':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video is already being processed"
        )
    
    if video.status == 'completed':
        return ProcessingStatusResponse(
            job_id=vid_str,
            status="completed",
            progress=100,
            error=None,
            result={"message": "Video has already been processed"}
        )
    
    # Initialize status
    processing_status[vid_str] = {'status': 'queued', 'progress': 0, 'error': None}
    
    # Add processing to background tasks
    background_tasks.add_task(process_video_sync, vid_str, None)
    
    logger.info(f"Queued simple processing for video {video_id}")
    
    return ProcessingStatusResponse(
        job_id=vid_str,
        status="processing",
        progress=0,
        error=None,
        result={"message": "Video processing started in background"}
    )


@router.get("/status/{video_id}", response_model=ProcessingStatusResponse)
async def get_video_processing_status(
    video_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get the processing status of a video
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )
    
    vid_str = str(video_id)
    
    # Check in-memory status first (for live updates)
    if vid_str in processing_status:
        mem_status = processing_status[vid_str]
        return ProcessingStatusResponse(
            job_id=vid_str,
            status=mem_status.get('status', video.status),
            progress=mem_status.get('progress', 0),
            error=mem_status.get('error'),
            result=mem_status.get('result', {
                'step': mem_status.get('step', ''),
                'processing_started_at': video.processing_started_at.isoformat() if video.processing_started_at else None,
            })
        )
    
    # Fall back to database status
    progress = 0
    if video.status == 'processing':
        progress = 50
    elif video.status == 'completed':
        progress = 100
    
    return ProcessingStatusResponse(
        job_id=vid_str,
        status=video.status,
        progress=progress,
        error=video.processing_error,
        result={
            "processing_started_at": video.processing_started_at.isoformat() if video.processing_started_at else None,
            "processing_completed_at": video.processing_completed_at.isoformat() if video.processing_completed_at else None,
        }
    )


@router.get("/tracks/{video_id}")
async def get_video_tracks(
    video_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all tracks for a processed video
    Returns track data for 2D visualization
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )
    
    if video.status != 'completed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Video has not been processed yet. Status: {video.status}"
        )
    
    # Get all tracks with their points
    tracks = db.query(TrackModel).filter(TrackModel.video_id == video_id).all()
    
    result = []
    for track in tracks:
        points = db.query(TrackPoint).filter(TrackPoint.track_id == track.id).order_by(TrackPoint.frame_number).all()
        result.append({
            'track_id': track.track_id,
            'object_class': track.object_class.value if hasattr(track.object_class, 'value') else str(track.object_class),
            'team_side': track.team_side.value if hasattr(track.team_side, 'value') else str(track.team_side),
            'first_frame': track.first_frame,
            'last_frame': track.last_frame,
            'total_detections': track.total_detections,
            'points': [
                {
                    'frame': p.frame_number,
                    'timestamp': p.timestamp,
                    'x': p.x_px,
                    'y': p.y_px,
                    'bbox': [p.bbox_x1, p.bbox_y1, p.bbox_x2, p.bbox_y2],
                    'confidence': p.confidence
                }
                for p in points
            ]
        })
    
    return {
        'video_id': str(video_id),
        'video_info': {
            'width': video.width,
            'height': video.height,
            'fps': video.fps,
            'duration': video.duration,
            'total_frames': video.total_frames
        },
        'tracks': result
    }
