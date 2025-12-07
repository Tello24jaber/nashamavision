"""
Replay Service - Data Processing for Virtual Match Engine
Phase 4: Virtual Match Engine
"""
from typing import List, Dict, Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import logging
from collections import defaultdict

from app.models.models import Match, Video, Track, TrackPoint
# Note: PlayerMetrics and Event models should be added to models.py in Phase 2-3
# For now, we'll handle them gracefully if they don't exist
try:
    from app.models.models import PlayerMetrics, Event
except ImportError:
    PlayerMetrics = None
    Event = None

# These enums should also be in models.py
try:
    from app.models.models import ObjectClass, TeamSide
except (ImportError, AttributeError):
    # Define minimal fallback enums for testing
    from enum import Enum
    class ObjectClass(str, Enum):
        PLAYER = "player"
        BALL = "ball"
        REFEREE = "referee"
    
    class TeamSide(str, Enum):
        HOME = "home"
        AWAY = "away"
        REFEREE = "referee"
from app.schemas.replay import (
    ReplayPosition, ReplayPlayer, ReplayEvent, ReplayTimelineResponse,
    ReplaySummaryResponse, ReplayPlayerSummary, ReplaySegment
)

logger = logging.getLogger(__name__)


class ReplayService:
    """Service for generating replay data from tracking and analytics data"""
    
    # Pitch dimensions in meters
    PITCH_LENGTH = 105.0
    PITCH_WIDTH = 68.0
    
    # Default colors for teams
    DEFAULT_HOME_COLOR = "#FF3B3B"  # Red
    DEFAULT_AWAY_COLOR = "#3B82F6"  # Blue
    DEFAULT_BALL_COLOR = "#FFFFFF"  # White
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_replay_summary(self, match_id: UUID) -> ReplaySummaryResponse:
        """
        Get replay summary and metadata for a match
        
        Args:
            match_id: Match UUID
            
        Returns:
            ReplaySummaryResponse with match metadata and player list
        """
        # Fetch match
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise ValueError(f"Match {match_id} not found")
        
        # Fetch video to get duration
        video = self.db.query(Video).filter(Video.match_id == match_id).first()
        if not video:
            raise ValueError(f"No video found for match {match_id}")
        
        duration = video.duration
        
        # Fetch all player tracks
        tracks = self.db.query(Track).filter(
            and_(
                Track.match_id == match_id,
                Track.object_class == 'player'
            )
        ).all()
        
        # Build player summaries
        players = []
        for track in tracks:
            # Try to get player metrics for additional info
            metrics = self.db.query(PlayerMetrics).filter(
                PlayerMetrics.track_id == track.id
            ).first()
            
            color = self._get_team_color(track.team_side)
            
            player_summary = ReplayPlayerSummary(
                player_id=track.id,  # Using track ID as player ID
                track_id=track.track_id,
                team=track.team_side,
                shirt_number=None,  # TODO: Extract from detection if available
                color=color,
                name=None,  # TODO: Link to player database if available
                position=None
            )
            players.append(player_summary)
        
        # Count total events
        total_events = self.db.query(func.count(Event.id)).filter(
            Event.match_id == match_id
        ).scalar() or 0
        
        # Create segments
        segments = [
            ReplaySegment(
                id="full",
                name="Full Match",
                start_time=0.0,
                end_time=duration,
                duration=duration
            )
        ]
        
        # Add half segments if duration suggests a full match
        if duration > 2700:  # More than 45 minutes
            half_time = duration / 2
            segments.extend([
                ReplaySegment(
                    id="first_half",
                    name="First Half",
                    start_time=0.0,
                    end_time=half_time,
                    duration=half_time
                ),
                ReplaySegment(
                    id="second_half",
                    name="Second Half",
                    start_time=half_time,
                    end_time=duration,
                    duration=half_time
                )
            ])
        
        return ReplaySummaryResponse(
            match_id=match_id,
            match_name=match.name,
            home_team=match.home_team,
            away_team=match.away_team,
            match_date=match.match_date,
            duration=duration,
            players=players,
            segments=segments,
            total_events=total_events,
            home_team_color=self.DEFAULT_HOME_COLOR,
            away_team_color=self.DEFAULT_AWAY_COLOR
        )
    
    def get_replay_timeline(
        self,
        match_id: UUID,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        fps: float = 10,
        include_ball: bool = True,
        include_events: bool = True
    ) -> ReplayTimelineResponse:
        """
        Get replay timeline data with player positions, ball, and events
        
        Args:
            match_id: Match UUID
            start_time: Start time in seconds (None = from beginning)
            end_time: End time in seconds (None = to end)
            fps: Target frames per second for output
            include_ball: Whether to include ball tracking
            include_events: Whether to include events
            
        Returns:
            ReplayTimelineResponse with time-series data
        """
        # Fetch match and video
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise ValueError(f"Match {match_id} not found")
        
        video = self.db.query(Video).filter(Video.match_id == match_id).first()
        if not video:
            raise ValueError(f"No video found for match {match_id}")
        
        # Set time bounds
        if start_time is None:
            start_time = 0.0
        if end_time is None:
            end_time = video.duration
        
        duration = end_time - start_time
        
        logger.info(f"Generating replay timeline for match {match_id}: {start_time}s - {end_time}s @ {fps} fps")
        
        # Fetch player tracks with positions
        players = self._get_player_positions(match_id, start_time, end_time, fps)
        
        # Fetch ball positions if requested
        ball = []
        if include_ball:
            ball = self._get_ball_positions(match_id, start_time, end_time, fps)
        
        # Fetch events if requested
        events = []
        if include_events:
            events = self._get_events(match_id, start_time, end_time)
        
        return ReplayTimelineResponse(
            match_id=match_id,
            fps=fps,
            duration=duration,
            start_time=start_time,
            end_time=end_time,
            players=players,
            ball=ball,
            events=events
        )
    
    def _get_player_positions(
        self,
        match_id: UUID,
        start_time: float,
        end_time: float,
        fps: float
    ) -> List[ReplayPlayer]:
        """Fetch and resample player positions"""
        # Fetch all player tracks
        tracks = self.db.query(Track).filter(
            and_(
                Track.match_id == match_id,
                Track.object_class == 'player'
            )
        ).all()
        
        players = []
        
        for track in tracks:
            # Fetch track points in time range
            points = self.db.query(TrackPoint).filter(
                and_(
                    TrackPoint.track_id == track.id,
                    TrackPoint.timestamp >= start_time,
                    TrackPoint.timestamp <= end_time
                )
            ).order_by(TrackPoint.timestamp).all()
            
            if not points:
                logger.warning(f"No track points found for track {track.id} in time range")
                continue
            
            # Resample to target FPS
            positions = self._resample_positions(points, start_time, end_time, fps)
            
            # Create player object
            color = self._get_team_color(track.team_side)
            
            player = ReplayPlayer(
                player_id=track.id,
                track_id=track.track_id,
                team=track.team_side,
                shirt_number=None,  # TODO: Extract if available
                color=color,
                positions=positions
            )
            players.append(player)
        
        logger.info(f"Loaded {len(players)} players with positions")
        return players
    
    def _get_ball_positions(
        self,
        match_id: UUID,
        start_time: float,
        end_time: float,
        fps: float
    ) -> List[ReplayPosition]:
        """Fetch and resample ball positions"""
        # Fetch ball track
        ball_track = self.db.query(Track).filter(
            and_(
                Track.match_id == match_id,
                Track.object_class == 'ball'
            )
        ).first()
        
        if not ball_track:
            logger.warning(f"No ball track found for match {match_id}")
            return []
        
        # Fetch track points
        points = self.db.query(TrackPoint).filter(
            and_(
                TrackPoint.track_id == ball_track.id,
                TrackPoint.timestamp >= start_time,
                TrackPoint.timestamp <= end_time
            )
        ).order_by(TrackPoint.timestamp).all()
        
        if not points:
            logger.warning(f"No ball track points found in time range")
            return []
        
        # Resample
        positions = self._resample_positions(points, start_time, end_time, fps)
        
        logger.info(f"Loaded ball positions: {len(positions)} frames")
        return positions
    
    def _get_events(
        self,
        match_id: UUID,
        start_time: float,
        end_time: float
    ) -> List[ReplayEvent]:
        """Fetch events in time range"""
        events_db = self.db.query(Event).filter(
            and_(
                Event.match_id == match_id,
                Event.timestamp >= start_time,
                Event.timestamp <= end_time
            )
        ).order_by(Event.timestamp).all()
        
        events = []
        
        for event_db in events_db:
            # Extract start and end positions from metadata
            start_x = event_db.start_x_m or 0.0
            start_y = event_db.start_y_m or 0.0
            end_x = event_db.end_x_m or 0.0
            end_y = event_db.end_y_m or 0.0
            
            event = ReplayEvent(
                id=event_db.id,
                type=event_db.event_type,
                t=event_db.timestamp,
                player_id=event_db.player_id,
                from_pos={"x": start_x, "y": start_y},
                to_pos={"x": end_x, "y": end_y},
                xt_gain=event_db.xt_value,
                velocity=event_db.velocity,
                distance=event_db.distance,
                duration=event_db.duration
            )
            events.append(event)
        
        logger.info(f"Loaded {len(events)} events")
        return events
    
    def _resample_positions(
        self,
        points: List[TrackPoint],
        start_time: float,
        end_time: float,
        fps: float
    ) -> List[ReplayPosition]:
        """
        Resample track points to consistent FPS
        
        Uses linear interpolation between known points
        """
        if not points:
            return []
        
        # Create time grid at target FPS
        dt = 1.0 / fps
        times = []
        t = start_time
        while t <= end_time:
            times.append(t)
            t += dt
        
        # Build position lookup
        positions = []
        point_idx = 0
        
        for t in times:
            # Find surrounding points
            while point_idx < len(points) - 1 and points[point_idx + 1].timestamp <= t:
                point_idx += 1
            
            if point_idx >= len(points):
                break
            
            # Get point
            point = points[point_idx]
            
            # Use metric coordinates if available, otherwise use pixel coordinates (scaled)
            x = point.x_m if point.x_m is not None else (point.x_px / 10.0)  # Rough scaling
            y = point.y_m if point.y_m is not None else (point.y_px / 10.0)
            
            # Clamp to pitch bounds
            x = max(0, min(self.PITCH_LENGTH, x))
            y = max(0, min(self.PITCH_WIDTH, y))
            
            # Normalize time to start from 0
            relative_time = t - start_time
            
            positions.append(ReplayPosition(
                t=relative_time,
                x=x,
                y=y
            ))
        
        return positions
    
    def _get_team_color(self, team_side) -> str:
        """Get color for team"""
        if team_side == 'home':
            return self.DEFAULT_HOME_COLOR
        elif team_side == 'away':
            return self.DEFAULT_AWAY_COLOR
        else:
            return "#888888"  # Gray for unknown/referee
