"""
Pydantic Schemas for Replay API
Phase 4: Virtual Match Engine
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.models import TeamSide


# ============= Position & Event Schemas =============

class ReplayPosition(BaseModel):
    """Single position data point in replay timeline"""
    t: float = Field(..., description="Time in seconds from match start")
    x: float = Field(..., description="X coordinate in meters (0-105)")
    y: float = Field(..., description="Y coordinate in meters (0-68)")
    
    model_config = {"from_attributes": True}


class ReplayEvent(BaseModel):
    """Event data for replay overlay"""
    id: UUID = Field(..., description="Event ID")
    type: str = Field(..., description="Event type: pass, carry, shot")
    t: float = Field(..., description="Event time in seconds")
    player_id: UUID = Field(..., description="Player who performed the event")
    from_pos: Dict[str, float] = Field(..., alias="from", description="Start position {x, y}")
    to_pos: Dict[str, float] = Field(..., alias="to", description="End position {x, y}")
    xt_gain: Optional[float] = Field(None, description="xT gain from this event")
    velocity: Optional[float] = Field(None, description="Event velocity in m/s")
    distance: Optional[float] = Field(None, description="Event distance in meters")
    duration: Optional[float] = Field(None, description="Event duration in seconds")
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


# ============= Player Schemas =============

class ReplayPlayer(BaseModel):
    """Player information for replay"""
    player_id: UUID = Field(..., description="Player database ID")
    track_id: int = Field(..., description="Tracking ID from CV pipeline")
    team: TeamSide = Field(..., description="Team side: home or away")
    shirt_number: Optional[int] = Field(None, description="Player shirt number")
    color: str = Field(..., description="Player color in hex format #RRGGBB")
    positions: List[ReplayPosition] = Field(..., description="Time-series positions")
    
    model_config = {"from_attributes": True}


# ============= Timeline Response Schema =============

class ReplayTimelineResponse(BaseModel):
    """Complete replay timeline data for a match segment"""
    match_id: UUID = Field(..., description="Match ID")
    fps: float = Field(..., description="Target frames per second for replay")
    duration: float = Field(..., description="Total duration in seconds")
    start_time: float = Field(..., description="Start time of this segment")
    end_time: float = Field(..., description="End time of this segment")
    
    players: List[ReplayPlayer] = Field(..., description="All players with positions")
    ball: List[ReplayPosition] = Field(..., description="Ball positions over time")
    events: List[ReplayEvent] = Field(..., description="Match events in this segment")
    
    model_config = {"from_attributes": True}


# ============= Summary Schemas =============

class ReplayPlayerSummary(BaseModel):
    """Minimal player info for replay summary"""
    player_id: UUID
    track_id: int
    team: TeamSide
    shirt_number: Optional[int] = None
    color: str
    name: Optional[str] = None
    position: Optional[str] = None  # e.g., "Forward", "Midfielder"
    
    model_config = {"from_attributes": True}


class ReplaySegment(BaseModel):
    """Available replay segments (e.g., full match, first half, second half)"""
    id: str = Field(..., description="Segment ID: 'full', 'first_half', 'second_half'")
    name: str = Field(..., description="Human-readable name")
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    duration: float = Field(..., description="Duration in seconds")


class ReplaySummaryResponse(BaseModel):
    """Match replay summary and metadata"""
    match_id: UUID
    match_name: str
    home_team: str
    away_team: str
    match_date: Optional[datetime] = None
    duration: float = Field(..., description="Total match duration in seconds")
    
    players: List[ReplayPlayerSummary] = Field(..., description="All players in match")
    segments: List[ReplaySegment] = Field(..., description="Available replay segments")
    
    # Statistics
    total_events: int = Field(..., description="Total number of events")
    home_team_color: str = Field(..., description="Home team color hex")
    away_team_color: str = Field(..., description="Away team color hex")
    
    model_config = {"from_attributes": True}


# ============= Request Schemas =============

class ReplayTimelineRequest(BaseModel):
    """Query parameters for timeline request"""
    start_time: Optional[float] = Field(None, ge=0, description="Start time in seconds")
    end_time: Optional[float] = Field(None, ge=0, description="End time in seconds")
    fps: Optional[float] = Field(10, ge=1, le=60, description="Target FPS for replay (1-60)")
    include_ball: Optional[bool] = Field(True, description="Include ball tracking data")
    include_events: Optional[bool] = Field(True, description="Include event data")
    
    model_config = {"from_attributes": True}
