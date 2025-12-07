"""
Tracking Engine
Multi-object tracking using DeepSORT/ByteTrack
"""
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Track:
    """Represents a tracked object"""
    
    def __init__(self, track_id: int, bbox: List[int], class_name: str):
        self.track_id = track_id
        self.bbox = bbox  # [x1, y1, x2, y2]
        self.class_name = class_name
        self.age = 0
        self.hits = 0
        self.time_since_update = 0
    
    @property
    def center(self) -> tuple[float, float]:
        """Get center point"""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def update(self, bbox: List[int]):
        """Update track with new detection"""
        self.bbox = bbox
        self.hits += 1
        self.time_since_update = 0
    
    def predict(self):
        """Predict next position (placeholder for Kalman filter)"""
        self.age += 1
        self.time_since_update += 1
    
    def __repr__(self):
        return f"Track(id={self.track_id}, class={self.class_name}, bbox={self.bbox})"


class TrackingEngine:
    """
    Multi-object tracking engine
    Maintains stable IDs across frames using DeepSORT/ByteTrack algorithms
    """
    
    def __init__(
        self,
        max_age: int = 30,
        min_hits: int = 3,
        iou_threshold: float = 0.3,
        method: str = "deepsort"
    ):
        """
        Initialize tracking engine
        
        Args:
            max_age: Maximum frames to keep alive a track without detections
            min_hits: Minimum detections before track is confirmed
            iou_threshold: Minimum IoU for matching detections to tracks
            method: Tracking method ('deepsort' or 'bytetrack')
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.method = method
        
        self.tracks: List[Track] = []
        self.next_id = 1
        self.frame_count = 0
        
        logger.info(
            f"TrackingEngine initialized: method={method}, "
            f"max_age={max_age}, min_hits={min_hits}"
        )
    
    def update(self, detections: List) -> List[Track]:
        """
        Update tracks with new detections
        
        Args:
            detections: List of Detection objects from detection engine
            
        Returns:
            List of confirmed tracks
        """
        self.frame_count += 1
        
        # Predict next positions for existing tracks
        for track in self.tracks:
            track.predict()
        
        # Match detections to existing tracks
        matched_tracks, unmatched_detections = self._match_detections_to_tracks(detections)
        
        # Update matched tracks
        for track, detection in matched_tracks:
            track.update(detection.bbox)
        
        # Create new tracks for unmatched detections
        for detection in unmatched_detections:
            new_track = Track(
                track_id=self.next_id,
                bbox=detection.bbox,
                class_name=detection.class_name
            )
            self.tracks.append(new_track)
            self.next_id += 1
        
        # Remove dead tracks
        self.tracks = [
            track for track in self.tracks
            if track.time_since_update < self.max_age
        ]
        
        # Return only confirmed tracks
        confirmed_tracks = [
            track for track in self.tracks
            if track.hits >= self.min_hits
        ]
        
        return confirmed_tracks
    
    def _match_detections_to_tracks(
        self,
        detections: List
    ) -> tuple[List[tuple[Track, any]], List]:
        """
        Match detections to existing tracks using IoU
        
        Returns:
            Tuple of (matched_pairs, unmatched_detections)
        """
        if len(self.tracks) == 0:
            return [], detections
        
        if len(detections) == 0:
            return [], []
        
        # Compute IoU matrix
        iou_matrix = np.zeros((len(detections), len(self.tracks)))
        
        for d, detection in enumerate(detections):
            for t, track in enumerate(self.tracks):
                iou_matrix[d, t] = self._compute_iou(detection.bbox, track.bbox)
        
        # Greedy matching (simple approach)
        matched_pairs = []
        unmatched_detections = list(detections)
        matched_detection_indices = set()
        matched_track_indices = set()
        
        # Find best matches
        while iou_matrix.size > 0:
            # Find maximum IoU
            max_iou_idx = np.unravel_index(iou_matrix.argmax(), iou_matrix.shape)
            max_iou = iou_matrix[max_iou_idx]
            
            if max_iou < self.iou_threshold:
                break
            
            d_idx, t_idx = max_iou_idx
            
            matched_pairs.append((self.tracks[t_idx], detections[d_idx]))
            matched_detection_indices.add(d_idx)
            matched_track_indices.add(t_idx)
            
            # Remove matched items from matrix
            iou_matrix[d_idx, :] = 0
            iou_matrix[:, t_idx] = 0
        
        # Get unmatched detections
        unmatched_detections = [
            det for i, det in enumerate(detections)
            if i not in matched_detection_indices
        ]
        
        return matched_pairs, unmatched_detections
    
    def _compute_iou(self, bbox1: List[int], bbox2: List[int]) -> float:
        """
        Compute Intersection over Union between two bounding boxes
        
        Args:
            bbox1: [x1, y1, x2, y2]
            bbox2: [x1, y1, x2, y2]
            
        Returns:
            IoU value
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Compute intersection
        x_left = max(x1_1, x1_2)
        y_top = max(y1_1, y1_2)
        x_right = min(x2_1, x2_2)
        y_bottom = min(y2_1, y2_2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Compute union
        bbox1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        bbox2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        union_area = bbox1_area + bbox2_area - intersection_area
        
        iou = intersection_area / union_area if union_area > 0 else 0
        
        return iou
    
    def reset(self):
        """Reset tracker state"""
        self.tracks = []
        self.next_id = 1
        self.frame_count = 0
        logger.info("Tracker reset")
    
    def __repr__(self):
        return (
            f"TrackingEngine(method={self.method}, "
            f"tracks={len(self.tracks)}, frame={self.frame_count})"
        )
