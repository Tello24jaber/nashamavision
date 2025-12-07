"""
Pydantic Schemas for Analytics API
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


# ============= Player Metrics Schemas =============

class PlayerMetricResponse(BaseModel):
    """Response schema for a single player metric"""
    id: UUID
    player_id: UUID
    match_id: UUID
    video_id: UUID
    metric_name: str
    numeric_value: float
    unit: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class PlayerMetricsSummary(BaseModel):
    """Summary of all metrics for a player"""
    player_id: UUID
    track_id: int
    object_class: str
    team_side: Optional[str] = None
    
    # Distance metrics
    total_distance_km: float
    
    # Speed metrics
    avg_speed_kmh: float
    top_speed_kmh: float
    
    # Intensity metrics
    high_intensity_distance_m: float
    sprint_count: int
    
    # Acceleration
    max_acceleration_mps2: float
    max_deceleration_mps2: float
    
    # Stamina
    stamina_index: float


class TimeSeriesDataPoint(BaseModel):
    """Single time series data point"""
    timestamp: float
    value: float
    unit: Optional[str] = None


class PlayerTimeSeriesResponse(BaseModel):
    """Time series data for a player metric"""
    player_id: UUID
    match_id: UUID
    metric_type: str
    data_points: List[TimeSeriesDataPoint]
    
    model_config = {"from_attributes": True}


# ============= Heatmap Schemas =============

class HeatmapResponse(BaseModel):
    """Response schema for player heatmap"""
    id: UUID
    player_id: UUID
    match_id: UUID
    video_id: UUID
    grid_width: int
    grid_height: int
    heatmap_data: List[List[float]]
    pitch_length: float
    pitch_width: float
    total_positions: int
    max_intensity: float
    created_at: datetime
    
    model_config = {"from_attributes": True}


class HeatmapRequest(BaseModel):
    """Request schema for heatmap generation"""
    player_id: UUID
    match_id: Optional[UUID] = None
    normalize: bool = True
    grid_width: int = Field(default=40, ge=10, le=100)
    grid_height: int = Field(default=25, ge=10, le=100)


# ============= Match Analytics Schemas =============

class MatchAnalyticsSummary(BaseModel):
    """Summary of analytics for an entire match"""
    match_id: UUID
    match_name: str
    video_id: UUID
    
    # Player counts
    total_players: int
    home_players: int
    away_players: int
    
    # Aggregate statistics
    total_distance_covered_km: float
    avg_speed_kmh: float
    max_speed_kmh: float
    total_sprints: int
    
    # Top performers
    top_distance_player_id: Optional[UUID] = None
    top_speed_player_id: Optional[UUID] = None


class TeamMetricResponse(BaseModel):
    """Response schema for team metric"""
    id: UUID
    match_id: UUID
    video_id: UUID
    team_side: str
    metric_name: str
    numeric_value: float
    unit: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    model_config = {"from_attributes": True}


# ============= Player List Schemas =============

class PlayerInMatch(BaseModel):
    """Player information in a match"""
    player_id: UUID  # Track ID
    track_id: int
    object_class: str
    team_side: Optional[str] = None
    player_number: Optional[int] = None
    player_name: Optional[str] = None
    first_frame: int
    last_frame: int
    total_detections: int


class PlayerListResponse(BaseModel):
    """List of players in a match"""
    match_id: UUID
    video_id: UUID
    players: List[PlayerInMatch]


# ============= Analytics Computation Schemas =============

class AnalyticsComputationStatus(BaseModel):
    """Status of analytics computation"""
    video_id: UUID
    status: str
    metrics_computed: Optional[int] = None
    heatmaps_created: Optional[int] = None
    message: Optional[str] = None


# ============= Zone Analysis Schemas =============

class ZoneOccupancy(BaseModel):
    """Zone occupancy data"""
    zone_name: str
    occupancy_percentage: float


class ZoneAnalysisResponse(BaseModel):
    """Zone analysis for a player"""
    player_id: UUID
    match_id: UUID
    zones: List[ZoneOccupancy]
