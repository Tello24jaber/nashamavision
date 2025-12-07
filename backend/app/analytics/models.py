"""
Analytics Database Models
New models for Phase 2 analytics storage
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text,
    ForeignKey, Index, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid
import enum

from app.db.session import Base


class MetricType(str, enum.Enum):
    """Metric type enumeration"""
    TOTAL_DISTANCE = "total_distance"
    TOP_SPEED = "top_speed"
    AVG_SPEED = "avg_speed"
    HIGH_INTENSITY_DISTANCE = "high_intensity_distance"
    SPRINT_COUNT = "sprint_count"
    MAX_ACCELERATION = "max_acceleration"
    MAX_DECELERATION = "max_deceleration"
    STAMINA_INDEX = "stamina_index"
    AVG_HEART_RATE = "avg_heart_rate"  # Future
    DISTANCE_PER_MINUTE = "distance_per_minute"


class TimeSeriesMetricType(str, enum.Enum):
    """Time series metric types"""
    SPEED = "speed"
    ACCELERATION = "acceleration"
    STAMINA = "stamina"
    DISTANCE_ROLLING = "distance_rolling"


class PlayerMetric(Base):
    """
    PlayerMetric - Stores aggregate metrics for a player in a match
    One record per player per match per metric
    """
    __tablename__ = "player_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), nullable=False)  # References Track.id
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    
    # Metric Information
    metric_name = Column(Enum(MetricType), nullable=False)
    numeric_value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)  # e.g., "m", "m/s", "count"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_player_metric_player_match", "player_id", "match_id"),
        Index("idx_player_metric_match", "match_id"),
        Index("idx_player_metric_video", "video_id"),
        Index("idx_player_metric_type", "metric_name"),
    )
    
    def __repr__(self):
        return f"<PlayerMetric(player_id={self.player_id}, metric={self.metric_name}, value={self.numeric_value})>"


class PlayerMetricTimeSeries(Base):
    """
    PlayerMetricTimeSeries - Stores time-series data for metrics
    Multiple records per player showing metric evolution over time
    """
    __tablename__ = "player_metric_timeseries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), nullable=False)  # References Track.id
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    
    # Time Information
    timestamp = Column(Float, nullable=False)  # seconds from video start
    frame_number = Column(Integer, nullable=True)
    
    # Metric Information
    metric_type = Column(Enum(TimeSeriesMetricType), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_timeseries_player_match", "player_id", "match_id"),
        Index("idx_timeseries_player_timestamp", "player_id", "timestamp"),
        Index("idx_timeseries_match", "match_id"),
        Index("idx_timeseries_video", "video_id"),
    )
    
    def __repr__(self):
        return f"<PlayerMetricTimeSeries(player_id={self.player_id}, metric={self.metric_type}, timestamp={self.timestamp})>"


class PlayerHeatmap(Base):
    """
    PlayerHeatmap - Stores heatmap data for a player in a match
    """
    __tablename__ = "player_heatmaps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), nullable=False)  # References Track.id
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    
    # Heatmap Data
    grid_width = Column(Integer, nullable=False)  # Number of bins horizontally
    grid_height = Column(Integer, nullable=False)  # Number of bins vertically
    heatmap_data = Column(JSON, nullable=False)  # 2D array of intensity values
    
    # Pitch Dimensions (meters)
    pitch_length = Column(Float, default=105.0)
    pitch_width = Column(Float, default=68.0)
    
    # Statistics
    total_positions = Column(Integer, nullable=False)
    max_intensity = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_heatmap_player_match", "player_id", "match_id"),
        Index("idx_heatmap_match", "match_id"),
        Index("idx_heatmap_video", "video_id"),
    )
    
    def __repr__(self):
        return f"<PlayerHeatmap(player_id={self.player_id}, match_id={self.match_id})>"


class TeamMetric(Base):
    """
    TeamMetric - Stores aggregate team-level metrics
    """
    __tablename__ = "team_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    team_side = Column(String(50), nullable=False)  # "home" or "away"
    
    # Team Tactical Metrics
    metric_name = Column(String(100), nullable=False)
    numeric_value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    
    # Additional Context
    extra_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_team_metric_match", "match_id"),
        Index("idx_team_metric_video", "video_id"),
    )
    
    def __repr__(self):
        return f"<TeamMetric(match_id={self.match_id}, team={self.team_side}, metric={self.metric_name})>"


# ============================================================================
# PHASE 3 MODELS - Tactical Analysis, xT, Events
# ============================================================================

class EventType(str, enum.Enum):
    """Event type enumeration"""
    PASS = "pass"
    CARRY = "carry"
    SHOT = "shot"
    DRIBBLE = "dribble"
    TACKLE = "tackle"
    INTERCEPTION = "interception"


class TacticalSnapshot(Base):
    """
    TacticalSnapshot - Stores tactical state at a moment in time
    """
    __tablename__ = "tactical_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    team_side = Column(String(50), nullable=False)
    
    timestamp = Column(Float, nullable=False)
    
    # Formation
    formation = Column(String(20), nullable=True)
    formation_confidence = Column(Float, nullable=True)
    
    # Positioning
    centroid_x = Column(Float, nullable=True)
    centroid_y = Column(Float, nullable=True)
    spread_x = Column(Float, nullable=True)
    spread_y = Column(Float, nullable=True)
    compactness = Column(Float, nullable=True)
    
    # Lines
    defensive_line_y = Column(Float, nullable=True)
    midfield_line_y = Column(Float, nullable=True)
    attacking_line_y = Column(Float, nullable=True)
    line_spacing_def_mid = Column(Float, nullable=True)
    line_spacing_mid_att = Column(Float, nullable=True)
    
    # Defensive metrics
    defensive_line_height = Column(Float, nullable=True)
    block_type = Column(String(20), nullable=True)
    
    # Pressing
    pressing_intensity = Column(Float, nullable=True)
    
    # Player positions (JSON array)
    player_positions = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_tactical_snapshot_match", "match_id"),
        Index("idx_tactical_snapshot_match_team", "match_id", "team_side"),
        Index("idx_tactical_snapshot_timestamp", "timestamp"),
    )
    
    def __repr__(self):
        return f"<TacticalSnapshot(match_id={self.match_id}, team={self.team_side}, formation={self.formation})>"


class XTMetric(Base):
    """
    XTMetric - Stores Expected Threat metrics for players
    """
    __tablename__ = "xt_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(UUID(as_uuid=True), nullable=False)  # References Track.id
    team_side = Column(String(50), nullable=False)
    
    # xT Summary
    total_xt_gain = Column(Float, nullable=False, default=0.0)
    danger_score = Column(Float, nullable=False, default=0.0)
    
    pass_xt = Column(Float, nullable=False, default=0.0)
    carry_xt = Column(Float, nullable=False, default=0.0)
    shot_xt = Column(Float, nullable=False, default=0.0)
    
    num_passes = Column(Integer, nullable=False, default=0)
    num_carries = Column(Integer, nullable=False, default=0)
    num_shots = Column(Integer, nullable=False, default=0)
    
    avg_xt_per_action = Column(Float, nullable=False, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_xt_metric_match", "match_id"),
        Index("idx_xt_metric_player", "player_id"),
        Index("idx_xt_metric_match_player", "match_id", "player_id"),
    )
    
    def __repr__(self):
        return f"<XTMetric(player_id={self.player_id}, total_xt={self.total_xt_gain:.2f})>"


class Event(Base):
    """
    Event - Stores detected football events (passes, carries, shots)
    """
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(UUID(as_uuid=True), nullable=False)  # References Track.id
    team_side = Column(String(50), nullable=False)
    
    event_type = Column(Enum(EventType), nullable=False)
    timestamp = Column(Float, nullable=False)
    frame_number = Column(Integer, nullable=True)
    
    # Spatial data
    start_x = Column(Float, nullable=False)
    start_y = Column(Float, nullable=False)
    end_x = Column(Float, nullable=False)
    end_y = Column(Float, nullable=False)
    
    # Event metrics
    distance = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    velocity = Column(Float, nullable=False)
    
    # xT value
    xt_value = Column(Float, nullable=True)
    
    # Additional metadata
    extra_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_event_match", "match_id"),
        Index("idx_event_player", "player_id"),
        Index("idx_event_match_player", "match_id", "player_id"),
        Index("idx_event_type", "event_type"),
        Index("idx_event_timestamp", "timestamp"),
    )
    
    def __repr__(self):
        return f"<Event(type={self.event_type}, player_id={self.player_id}, timestamp={self.timestamp})>"


class TransitionMetric(Base):
    """
    TransitionMetric - Stores transition events (defense to attack, attack to defense)
    """
    __tablename__ = "transition_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    team_side = Column(String(50), nullable=False)
    
    transition_type = Column(String(50), nullable=False)  # "defense_to_attack" or "attack_to_defense"
    
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    
    distance_covered = Column(Float, nullable=False)
    avg_speed = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_transition_match", "match_id"),
        Index("idx_transition_match_team", "match_id", "team_side"),
    )
    
    def __repr__(self):
        return f"<TransitionMetric(type={self.transition_type}, duration={self.duration:.1f}s)>"
