"""
Celery Tasks
Background processing tasks for video processing and analytics
"""
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from uuid import UUID

from celery import Task
from sqlalchemy.orm import Session

from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.models import Video, Track, TrackPoint, ProcessingStatus, ObjectClass
from app.storage.storage_interface import get_storage
from app.cv_pipeline.frame_extractor import FrameExtractor
from app.cv_pipeline.detection.detection_engine import DetectionEngine
from app.cv_pipeline.tracking.tracking_engine import TrackingEngine
from app.cv_pipeline.classification.team_classifier import TeamClassifier
from app.cv_pipeline.calibration.pitch_calibrator import PitchCalibrator
from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""
    
    _db: Session = None
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(bind=True, base=DatabaseTask, name="app.workers.tasks.process_video_task")
def process_video_task(self, video_id: str):
    """
    Process video through complete CV pipeline
    
    Steps:
    1. Download video from storage
    2. Extract frames
    3. Run object detection
    4. Perform multi-object tracking
    5. Classify teams (stub)
    6. Calibrate pitch (stub)
    7. Save tracking data to database
    
    Args:
        video_id: UUID of the video to process
    """
    logger.info(f"Starting video processing for video_id: {video_id}")
    
    try:
        # Get video from database
        video = self.db.query(Video).filter(Video.id == UUID(video_id)).first()
        
        if not video:
            raise ValueError(f"Video not found: {video_id}")
        
        # Update status to processing
        video.status = ProcessingStatus.PROCESSING
        video.processing_started_at = datetime.utcnow()
        self.db.commit()
        
        # Initialize storage
        storage = get_storage()
        
        # Download video to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(video.filename).suffix) as tmp_file:
            tmp_video_path = tmp_file.name
        
        logger.info(f"Downloading video from storage: {video.storage_path}")
        storage.download_file(video.storage_path, tmp_video_path)
        
        # Initialize CV pipeline components
        detector = DetectionEngine(
            model_path=settings.yolo_model_path,
            confidence_threshold=settings.yolo_confidence_threshold,
            iou_threshold=settings.yolo_iou_threshold,
            device="cuda" if settings.is_production else "cpu"
        )
        
        tracker = TrackingEngine(
            max_age=settings.max_age,
            min_hits=settings.min_hits,
            method=settings.tracking_method
        )
        
        # Process video
        logger.info("Starting frame processing...")
        
        with FrameExtractor(tmp_video_path, target_fps=settings.frame_extraction_fps) as extractor:
            frame_count = 0
            tracks_data = {}  # Store tracks by ID
            
            for frame_number, frame in extractor.extract_frames():
                # Run detection
                detections = detector.detect(frame)
                
                # Update tracker
                tracks = tracker.update(detections)
                
                # Store track data
                timestamp = frame_number / extractor.video_fps
                
                for track in tracks:
                    if track.track_id not in tracks_data:
                        tracks_data[track.track_id] = {
                            "class": track.class_name,
                            "points": []
                        }
                    
                    x1, y1, x2, y2 = track.bbox
                    center_x, center_y = track.center
                    
                    tracks_data[track.track_id]["points"].append({
                        "frame_number": frame_number,
                        "timestamp": timestamp,
                        "bbox": [x1, y1, x2, y2],
                        "x_px": center_x,
                        "y_px": center_y,
                        "confidence": 0.9  # Placeholder
                    })
                
                frame_count += 1
                
                # Update progress every 100 frames
                if frame_count % 100 == 0:
                    logger.info(f"Processed {frame_count} frames...")
        
        logger.info(f"Frame processing complete. Total frames: {frame_count}")
        logger.info(f"Total tracks: {len(tracks_data)}")
        
        # Save tracks to database
        logger.info("Saving tracks to database...")
        
        for track_id, track_data in tracks_data.items():
            points = track_data["points"]
            
            if len(points) == 0:
                continue
            
            # Determine object class
            class_name = track_data["class"]
            if "ball" in class_name.lower():
                object_class = 'ball'
            else:
                object_class = 'player'
            
            # Create Track record
            track = Track(
                video_id=video.id,
                track_id=track_id,
                object_class=object_class,
                team_side=None,  # Will be set by team classifier
                first_frame=points[0]["frame_number"],
                last_frame=points[-1]["frame_number"],
                total_detections=len(points)
            )
            
            self.db.add(track)
            self.db.flush()  # Get track.id
            
            # Create TrackPoint records
            for point in points:
                track_point = TrackPoint(
                    track_id=track.id,
                    frame_number=point["frame_number"],
                    timestamp=point["timestamp"],
                    bbox_x1=point["bbox"][0],
                    bbox_y1=point["bbox"][1],
                    bbox_x2=point["bbox"][2],
                    bbox_y2=point["bbox"][3],
                    confidence=point["confidence"],
                    x_px=point["x_px"],
                    y_px=point["y_px"],
                    x_m=None,  # Will be set after calibration
                    y_m=None
                )
                self.db.add(track_point)
        
        # Update video status
        video.status = ProcessingStatus.COMPLETED
        video.processing_completed_at = datetime.utcnow()
        self.db.commit()
        
        # Clean up temporary file
        Path(tmp_video_path).unlink(missing_ok=True)
        
        logger.info(f"Video processing completed successfully for video_id: {video_id}")
        
        return {
            "video_id": video_id,
            "status": "completed",
            "frames_processed": frame_count,
            "tracks_created": len(tracks_data)
        }
        
    except Exception as e:
        logger.error(f"Video processing failed: {e}", exc_info=True)
        
        # Update video status to failed
        try:
            video = self.db.query(Video).filter(Video.id == UUID(video_id)).first()
            if video:
                video.status = ProcessingStatus.FAILED
                video.processing_error = str(e)
                self.db.commit()
        except:
            pass
        
        raise


@celery_app.task(bind=True, base=DatabaseTask, name="app.workers.tasks.analytics_computation_task")
def analytics_computation_task(self, video_id: str):
    """
    Compute analytics metrics for a processed video
    
    Phase 2 Implementation:
    - Physical metrics (speed, distance, acceleration, sprints)
    - Heatmap generation
    - Team-level metrics
    
    Args:
        video_id: UUID of the video
    """
    logger.info(f"Starting analytics computation for video_id: {video_id}")
    
    try:
        from app.analytics.physical import PhysicalMetricsEngine, TeamMetricsEngine, TrackPointData
        from app.analytics.heatmap import HeatmapEngine, HeatmapConfig
        from app.analytics.models import (
            PlayerMetric, PlayerMetricTimeSeries, PlayerHeatmap,
            TeamMetric, MetricType, TimeSeriesMetricType
        )
        
        # Get video from database
        video = self.db.query(Video).filter(Video.id == UUID(video_id)).first()
        
        if not video:
            raise ValueError(f"Video not found: {video_id}")
        
        if video.status != ProcessingStatus.COMPLETED:
            raise ValueError(f"Video processing not completed: {video_id}")
        
        logger.info(f"Computing analytics for video: {video_id}, match: {video.match_id}")
        
        # Get all tracks for this video
        tracks = self.db.query(Track).filter(Track.video_id == video.id).all()
        
        if len(tracks) == 0:
            logger.warning(f"No tracks found for video: {video_id}")
            return {
                "video_id": video_id,
                "status": "completed",
                "message": "No tracks to analyze"
            }
        
        # Initialize engines
        physical_engine = PhysicalMetricsEngine()
        heatmap_engine = HeatmapEngine(HeatmapConfig())
        team_engine = TeamMetricsEngine()
        
        player_tracks = [t for t in tracks if t.object_class == 'player']
        
        logger.info(f"Processing {len(player_tracks)} player tracks")
        
        metrics_computed = 0
        heatmaps_created = 0
        
        # Process each player track
        for track in player_tracks:
            # Get all track points ordered by timestamp
            track_points = (
                self.db.query(TrackPoint)
                .filter(TrackPoint.track_id == track.id)
                .order_by(TrackPoint.timestamp)
                .all()
            )
            
            if len(track_points) < 2:
                continue
            
            # Check if metric coordinates are available
            has_metric_coords = all(tp.x_m is not None and tp.y_m is not None for tp in track_points)
            
            if not has_metric_coords:
                logger.warning(f"Track {track.id} missing metric coordinates, skipping")
                continue
            
            # Convert to TrackPointData
            track_point_data = [
                TrackPointData(
                    timestamp=tp.timestamp,
                    frame_number=tp.frame_number,
                    x_m=tp.x_m,
                    y_m=tp.y_m,
                    x_px=tp.x_px,
                    y_px=tp.y_px
                )
                for tp in track_points
            ]
            
            # Compute physical metrics
            physical_metrics = physical_engine.compute_metrics(track_point_data)
            
            if physical_metrics is None:
                logger.warning(f"Failed to compute metrics for track {track.id}")
                continue
            
            # Save aggregate metrics to database
            aggregate_metrics = [
                (MetricType.TOTAL_DISTANCE, physical_metrics.total_distance_m, "m"),
                (MetricType.TOP_SPEED, physical_metrics.top_speed_mps, "m/s"),
                (MetricType.AVG_SPEED, physical_metrics.avg_speed_mps, "m/s"),
                (MetricType.HIGH_INTENSITY_DISTANCE, physical_metrics.high_intensity_distance_m, "m"),
                (MetricType.SPRINT_COUNT, physical_metrics.sprint_count, "count"),
                (MetricType.MAX_ACCELERATION, physical_metrics.max_acceleration_mps2, "m/s²"),
                (MetricType.MAX_DECELERATION, physical_metrics.max_deceleration_mps2, "m/s²"),
                (MetricType.STAMINA_INDEX, physical_metrics.stamina_index, "index"),
            ]
            
            for metric_name, value, unit in aggregate_metrics:
                player_metric = PlayerMetric(
                    player_id=track.id,
                    match_id=video.match_id,
                    video_id=video.id,
                    metric_name=metric_name,
                    numeric_value=value,
                    unit=unit
                )
                self.db.add(player_metric)
            
            # Save time series data (speed and acceleration)
            for timestamp, speed in physical_metrics.speed_timeseries:
                ts_record = PlayerMetricTimeSeries(
                    player_id=track.id,
                    match_id=video.match_id,
                    video_id=video.id,
                    timestamp=timestamp,
                    metric_type=TimeSeriesMetricType.SPEED,
                    value=speed,
                    unit="m/s"
                )
                self.db.add(ts_record)
            
            for timestamp, accel in physical_metrics.acceleration_timeseries:
                ts_record = PlayerMetricTimeSeries(
                    player_id=track.id,
                    match_id=video.match_id,
                    video_id=video.id,
                    timestamp=timestamp,
                    metric_type=TimeSeriesMetricType.ACCELERATION,
                    value=accel,
                    unit="m/s²"
                )
                self.db.add(ts_record)
            
            for timestamp, stamina in physical_metrics.stamina_curve:
                ts_record = PlayerMetricTimeSeries(
                    player_id=track.id,
                    match_id=video.match_id,
                    video_id=video.id,
                    timestamp=timestamp,
                    metric_type=TimeSeriesMetricType.STAMINA,
                    value=stamina,
                    unit="m/s"
                )
                self.db.add(ts_record)
            
            metrics_computed += 1
            
            # Generate heatmap
            positions = [(tp.x_m, tp.y_m) for tp in track_points if tp.x_m is not None]
            
            if len(positions) > 0:
                heatmap = heatmap_engine.generate_heatmap(positions, normalize=True)
                
                if heatmap:
                    heatmap_record = PlayerHeatmap(
                        player_id=track.id,
                        match_id=video.match_id,
                        video_id=video.id,
                        grid_width=heatmap.grid_width,
                        grid_height=heatmap.grid_height,
                        heatmap_data=heatmap.to_dict()["data"],
                        pitch_length=heatmap.pitch_length,
                        pitch_width=heatmap.pitch_width,
                        total_positions=heatmap.total_positions,
                        max_intensity=heatmap.max_intensity
                    )
                    self.db.add(heatmap_record)
                    heatmaps_created += 1
        
        # Commit all changes
        self.db.commit()
        
        logger.info(f"Analytics computation completed for video {video_id}")
        logger.info(f"Metrics computed for {metrics_computed} players")
        logger.info(f"Heatmaps created for {heatmaps_created} players")
        
        # Trigger Phase 3 analysis
        try:
            compute_tactical_analysis_task.delay(str(video.match_id))
        except Exception as e:
            logger.warning(f"Failed to trigger tactical analysis: {e}")
        
        return {
            "video_id": video_id,
            "status": "completed",
            "metrics_computed": metrics_computed,
            "heatmaps_created": heatmaps_created
        }
        
    except Exception as e:
        logger.error(f"Analytics computation failed: {e}", exc_info=True)
        self.db.rollback()
        raise


# ============================================================================
# PHASE 3 TASKS - Tactical Analysis, xT, Events
# ============================================================================

@celery_app.task(bind=True, base=DatabaseTask, name="app.workers.tasks.compute_tactical_analysis_task")
def compute_tactical_analysis_task(self, match_id: str):
    """
    Compute tactical analysis for a match
    
    Args:
        match_id: Match UUID
        
    Returns:
        Dict with tactical analysis results
    """
    from app.analytics.tactical import TacticalAnalysisEngine
    from app.analytics.models import TacticalSnapshot, TransitionMetric
    from app.models.models import Match
    
    logger.info(f"Starting tactical analysis for match {match_id}")
    
    try:
        # Get match
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise ValueError(f"Match {match_id} not found")
        
        # Compute tactical analysis
        engine = TacticalAnalysisEngine(self.db)
        tactical_data = engine.analyze_match_tactics(match_id)
        
        # Save tactical snapshots
        snapshots_created = 0
        for team_side in ["home", "away"]:
            for snapshot in tactical_data[team_side]:
                # Check if already exists
                existing = self.db.query(TacticalSnapshot).filter(
                    TacticalSnapshot.match_id == match_id,
                    TacticalSnapshot.team_side == snapshot.team_side,
                    TacticalSnapshot.timestamp == snapshot.timestamp
                ).first()
                
                if not existing:
                    tactical_record = TacticalSnapshot(
                        match_id=match_id,
                        video_id=match.videos[0].id if match.videos else None,
                        team_side=snapshot.team_side,
                        timestamp=snapshot.timestamp,
                        formation=snapshot.formation,
                        formation_confidence=snapshot.formation_confidence,
                        centroid_x=snapshot.centroid_x,
                        centroid_y=snapshot.centroid_y,
                        spread_x=snapshot.spread_x,
                        spread_y=snapshot.spread_y,
                        compactness=snapshot.compactness,
                        defensive_line_y=snapshot.defensive_line_y,
                        midfield_line_y=snapshot.midfield_line_y,
                        attacking_line_y=snapshot.attacking_line_y,
                        line_spacing_def_mid=snapshot.line_spacing_def_mid,
                        line_spacing_mid_att=snapshot.line_spacing_mid_att,
                        defensive_line_height=snapshot.defensive_line_height,
                        block_type=snapshot.block_type,
                        pressing_intensity=snapshot.pressing_intensity,
                        player_positions=snapshot.player_positions
                    )
                    self.db.add(tactical_record)
                    snapshots_created += 1
        
        # Compute and save transitions
        transitions_created = 0
        for team_side in ["home", "away"]:
            transitions = engine.detect_transitions(match_id, team_side)
            
            for transition in transitions:
                transition_record = TransitionMetric(
                    match_id=match_id,
                    team_side=team_side,
                    transition_type=transition.transition_type,
                    start_time=transition.start_time,
                    end_time=transition.end_time,
                    duration=transition.duration,
                    distance_covered=transition.distance_covered,
                    avg_speed=transition.avg_speed
                )
                self.db.add(transition_record)
                transitions_created += 1
        
        self.db.commit()
        
        logger.info(f"Tactical analysis completed for match {match_id}")
        logger.info(f"Created {snapshots_created} tactical snapshots")
        logger.info(f"Created {transitions_created} transition events")
        
        # Trigger xT analysis
        try:
            compute_xt_analysis_task.delay(match_id)
        except Exception as e:
            logger.warning(f"Failed to trigger xT analysis: {e}")
        
        return {
            "match_id": match_id,
            "status": "completed",
            "snapshots_created": snapshots_created,
            "transitions_created": transitions_created
        }
        
    except Exception as e:
        logger.error(f"Tactical analysis failed: {e}", exc_info=True)
        self.db.rollback()
        raise


@celery_app.task(bind=True, base=DatabaseTask, name="app.workers.tasks.compute_xt_analysis_task")
def compute_xt_analysis_task(self, match_id: str):
    """
    Compute Expected Threat (xT) analysis for a match
    
    Args:
        match_id: Match UUID
        
    Returns:
        Dict with xT analysis results
    """
    from app.analytics.xt import ExpectedThreatEngine
    from app.analytics.events import EventDetectionEngine
    from app.analytics.models import XTMetric, Event as EventModel, EventType
    from app.models.models import Match
    
    logger.info(f"Starting xT analysis for match {match_id}")
    
    try:
        # Get match
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise ValueError(f"Match {match_id} not found")
        
        # Compute xT analysis
        xt_engine = ExpectedThreatEngine(self.db)
        xt_data = xt_engine.analyze_match_xt(match_id)
        
        # Save xT metrics
        xt_metrics_created = 0
        for team_side in ["home", "away"]:
            for player_summary in xt_data[team_side]["player_summaries"]:
                # Check if already exists
                existing = self.db.query(XTMetric).filter(
                    XTMetric.match_id == match_id,
                    XTMetric.player_id == player_summary.player_id
                ).first()
                
                if existing:
                    # Update existing
                    existing.total_xt_gain = player_summary.total_xt_gain
                    existing.danger_score = player_summary.danger_score
                    existing.pass_xt = player_summary.pass_xt
                    existing.carry_xt = player_summary.carry_xt
                    existing.shot_xt = player_summary.shot_xt
                    existing.num_passes = player_summary.num_passes
                    existing.num_carries = player_summary.num_carries
                    existing.num_shots = player_summary.num_shots
                    existing.avg_xt_per_action = player_summary.avg_xt_per_action
                else:
                    # Create new
                    xt_record = XTMetric(
                        match_id=match_id,
                        player_id=player_summary.player_id,
                        team_side=team_side,
                        total_xt_gain=player_summary.total_xt_gain,
                        danger_score=player_summary.danger_score,
                        pass_xt=player_summary.pass_xt,
                        carry_xt=player_summary.carry_xt,
                        shot_xt=player_summary.shot_xt,
                        num_passes=player_summary.num_passes,
                        num_carries=player_summary.num_carries,
                        num_shots=player_summary.num_shots,
                        avg_xt_per_action=player_summary.avg_xt_per_action
                    )
                    self.db.add(xt_record)
                xt_metrics_created += 1
        
        # Detect and save events
        event_engine = EventDetectionEngine(self.db)
        all_events = event_engine.detect_all_events(match_id)
        
        # Annotate with xT
        all_events = event_engine.annotate_events_with_xt(all_events, xt_engine)
        
        events_created = 0
        for event in all_events:
            # Check if already exists
            existing = self.db.query(EventModel).filter(
                EventModel.match_id == match_id,
                EventModel.player_id == event.player_id,
                EventModel.timestamp == event.timestamp,
                EventModel.event_type == EventType[event.event_type.upper()]
            ).first()
            
            if not existing:
                event_record = EventModel(
                    match_id=match_id,
                    player_id=event.player_id,
                    team_side=event.team_side,
                    event_type=EventType[event.event_type.upper()],
                    timestamp=event.timestamp,
                    frame_number=event.frame_number,
                    start_x=event.start_x,
                    start_y=event.start_y,
                    end_x=event.end_x,
                    end_y=event.end_y,
                    distance=event.distance,
                    duration=event.duration,
                    velocity=event.velocity,
                    xt_value=event.xt_value,
                    metadata=event.metadata
                )
                self.db.add(event_record)
                events_created += 1
        
        self.db.commit()
        
        logger.info(f"xT analysis completed for match {match_id}")
        logger.info(f"Created/updated {xt_metrics_created} xT metrics")
        logger.info(f"Created {events_created} events")
        
        return {
            "match_id": match_id,
            "status": "completed",
            "xt_metrics_created": xt_metrics_created,
            "events_created": events_created
        }
        
    except Exception as e:
        logger.error(f"xT analysis failed: {e}", exc_info=True)
        self.db.rollback()
        raise
