"""
Phase 3 Pydantic Schemas - Tactical, xT, Events
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Tuple
from datetime import datetime


# ============================================================================
# Tactical Schemas
# ============================================================================

class TeamTacticalSnapshotResponse(BaseModel):
    """Response model for a single tactical snapshot"""
    timestamp: float
    team_side: str
    
    # Formation
    formation: str
    formation_confidence: float
    
    # Positioning
    centroid_x: float
    centroid_y: float
    spread_x: float
    spread_y: float
    compactness: float
    
    # Lines
    defensive_line_y: float
    midfield_line_y: float
    attacking_line_y: float
    line_spacing_def_mid: float
    line_spacing_mid_att: float
    
    # Defensive metrics
    defensive_line_height: float
    block_type: str
    
    # Pressing
    pressing_intensity: float
    
    # Player positions
    player_positions: List[Tuple[float, float]]
    
    class Config:
        from_attributes = True


class MatchTacticsResponse(BaseModel):
    """Response containing tactical analysis for both teams"""
    match_id: str
    home_snapshots: List[TeamTacticalSnapshotResponse]
    away_snapshots: List[TeamTacticalSnapshotResponse]
    
    class Config:
        from_attributes = True


class TransitionEventResponse(BaseModel):
    """Response model for a transition event"""
    start_time: float
    end_time: float
    duration: float
    transition_type: str
    distance_covered: float
    avg_speed: float
    
    class Config:
        from_attributes = True


class TeamTransitionsResponse(BaseModel):
    """Response containing transitions for a team"""
    match_id: str
    team_side: str
    transitions: List[TransitionEventResponse]
    
    # Summary stats
    avg_defense_to_attack_time: Optional[float] = None
    avg_attack_to_defense_time: Optional[float] = None
    num_transitions: int = 0
    
    class Config:
        from_attributes = True


class FormationTimelineItem(BaseModel):
    """Formation at a specific timestamp"""
    timestamp: float
    formation: str
    confidence: float


class TacticalTimelineResponse(BaseModel):
    """Timeline of tactical changes"""
    match_id: str
    team_side: str
    formation_timeline: List[FormationTimelineItem]
    avg_pressing_intensity: float
    avg_compactness: float
    avg_defensive_line_height: float
    
    class Config:
        from_attributes = True


# ============================================================================
# xT (Expected Threat) Schemas
# ============================================================================

class XTEventResponse(BaseModel):
    """Response model for an xT event"""
    event_id: str
    player_id: str
    match_id: str
    timestamp: float
    event_type: str
    
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    
    start_cell: Tuple[int, int]
    end_cell: Tuple[int, int]
    
    xt_start: float
    xt_end: float
    xt_gain: float
    
    metadata: Dict
    
    class Config:
        from_attributes = True


class PlayerXTSummaryResponse(BaseModel):
    """Response model for player xT summary"""
    player_id: str
    match_id: str
    
    total_xt_gain: float
    danger_score: float
    
    pass_xt: float
    carry_xt: float
    shot_xt: float
    
    num_passes: int
    num_carries: int
    num_shots: int
    
    avg_xt_per_action: float
    
    class Config:
        from_attributes = True


class TeamXTSummaryResponse(BaseModel):
    """Response model for team xT summary"""
    team_side: str
    total_xt: float
    player_summaries: List[PlayerXTSummaryResponse]
    
    class Config:
        from_attributes = True


class MatchXTAnalysisResponse(BaseModel):
    """Complete xT analysis for a match"""
    match_id: str
    home: TeamXTSummaryResponse
    away: TeamXTSummaryResponse
    
    class Config:
        from_attributes = True


class XTGridResponse(BaseModel):
    """xT grid data for visualization"""
    grid_width: int
    grid_height: int
    cell_width: float
    cell_height: float
    pitch_length: float
    pitch_width: float
    values: List[List[float]]
    
    class Config:
        from_attributes = True


class PlayerXTDetailResponse(BaseModel):
    """Detailed xT response for a player"""
    summary: PlayerXTSummaryResponse
    events: List[XTEventResponse]
    
    class Config:
        from_attributes = True


class MatchXTEventsResponse(BaseModel):
    """All xT events for a match"""
    match_id: str
    home_events: List[XTEventResponse]
    away_events: List[XTEventResponse]
    
    class Config:
        from_attributes = True


# ============================================================================
# Event Schemas
# ============================================================================

class FootballEventResponse(BaseModel):
    """Response model for a football event"""
    id: str
    match_id: str
    player_id: str
    team_side: str
    
    event_type: str
    timestamp: float
    frame_number: Optional[int] = None
    
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    
    distance: float
    duration: float
    velocity: float
    
    xt_value: Optional[float] = None
    
    metadata: Optional[Dict] = None
    
    class Config:
        from_attributes = True


class MatchEventsResponse(BaseModel):
    """All events for a match"""
    match_id: str
    events: List[FootballEventResponse]
    
    # Summary stats
    num_passes: int = 0
    num_carries: int = 0
    num_shots: int = 0
    total_events: int = 0
    
    class Config:
        from_attributes = True


class PlayerEventsResponse(BaseModel):
    """Events for a specific player"""
    player_id: str
    match_id: str
    team_side: str
    events: List[FootballEventResponse]
    
    # Summary
    num_passes: int = 0
    num_carries: int = 0
    num_shots: int = 0
    total_xt_from_events: float = 0.0
    
    class Config:
        from_attributes = True


class EventTypeStatsResponse(BaseModel):
    """Statistics for a specific event type"""
    event_type: str
    count: int
    avg_distance: float
    avg_velocity: float
    avg_xt_gain: Optional[float] = None
    
    class Config:
        from_attributes = True


class TeamEventStatsResponse(BaseModel):
    """Event statistics for a team"""
    team_side: str
    match_id: str
    
    total_events: int
    event_type_breakdown: List[EventTypeStatsResponse]
    
    total_passes: int
    total_carries: int
    total_shots: int
    
    avg_pass_distance: float
    avg_carry_distance: float
    
    class Config:
        from_attributes = True


# ============================================================================
# Combined Analytics Schemas
# ============================================================================

class MatchAnalyticsOverview(BaseModel):
    """High-level analytics overview for a match"""
    match_id: str
    
    # Phase 2 metrics
    total_players: int
    total_distance_km: float
    avg_top_speed: float
    total_sprints: int
    
    # Phase 3 metrics
    home_formation: Optional[str] = None
    away_formation: Optional[str] = None
    home_xt: float = 0.0
    away_xt: float = 0.0
    total_events: int = 0
    
    class Config:
        from_attributes = True


class PlayerCompleteAnalytics(BaseModel):
    """Complete analytics for a single player"""
    player_id: str
    match_id: str
    team_side: str
    
    # Phase 2 physical metrics
    total_distance_km: Optional[float] = None
    top_speed_kmh: Optional[float] = None
    sprint_count: Optional[int] = None
    stamina_index: Optional[float] = None
    
    # Phase 3 tactical/xT
    xt_summary: Optional[PlayerXTSummaryResponse] = None
    events_summary: Optional[PlayerEventsResponse] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Request Models (if needed for POST/PUT)
# ============================================================================

class ComputeTacticsRequest(BaseModel):
    """Request to trigger tactical analysis computation"""
    match_id: str
    window_size: Optional[float] = 60.0  # seconds
    
    class Config:
        from_attributes = True


class ComputeXTRequest(BaseModel):
    """Request to trigger xT computation"""
    match_id: str
    
    class Config:
        from_attributes = True


# ============================================================================
# Status Response
# ============================================================================

class Phase3StatusResponse(BaseModel):
    """Status of Phase 3 computations"""
    match_id: str
    
    tactical_analysis_complete: bool = False
    tactical_snapshots_count: int = 0
    
    xt_analysis_complete: bool = False
    xt_metrics_count: int = 0
    
    events_detected: bool = False
    events_count: int = 0
    
    last_updated: Optional[datetime] = None
    
    class Config:
        from_attributes = True
