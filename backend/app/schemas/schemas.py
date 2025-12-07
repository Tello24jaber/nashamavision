"""
Pydantic Schemas for API Request/Response validation
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

from app.models.models import ProcessingStatus, ObjectClass, TeamSide


# ============= Match Schemas =============

class MatchBase(BaseModel):
    """Base match schema"""
    name: str = Field(..., min_length=1, max_length=255)
    home_team: str = Field(..., min_length=1, max_length=255)
    away_team: str = Field(..., min_length=1, max_length=255)
    match_date: Optional[datetime] = None
    venue: Optional[str] = None
    competition: Optional[str] = None
    season: Optional[str] = None


class MatchCreate(MatchBase):
    """Schema for creating a match"""
    pass


class MatchUpdate(BaseModel):
    """Schema for updating a match"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    home_team: Optional[str] = Field(None, min_length=1, max_length=255)
    away_team: Optional[str] = Field(None, min_length=1, max_length=255)
    match_date: Optional[datetime] = None
    venue: Optional[str] = None
    competition: Optional[str] = None
    season: Optional[str] = None


class MatchResponse(MatchBase):
    """Schema for match response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ============= Video Schemas =============

class VideoMetadata(BaseModel):
    """Video metadata extracted from file"""
    duration: float
    fps: float
    width: int
    height: int
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    total_frames: Optional[int] = None


class VideoBase(BaseModel):
    """Base video schema"""
    filename: str
    file_size: int
    file_extension: str


class VideoUploadResponse(BaseModel):
    """Response after video upload"""
    video_id: UUID
    match_id: UUID
    filename: str
    file_size: int
    storage_path: str
    metadata: VideoMetadata
    status: ProcessingStatus
    message: str


class VideoResponse(BaseModel):
    """Schema for video response"""
    id: UUID
    match_id: UUID
    filename: str
    file_size: int
    file_extension: str
    storage_path: str
    duration: float
    fps: float
    width: int
    height: int
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    total_frames: Optional[int] = None
    status: ProcessingStatus
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    processed_video_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class VideoListResponse(BaseModel):
    """Schema for listing videos"""
    videos: List[VideoResponse]
    total: int


# ============= Track Schemas =============

class TrackPointResponse(BaseModel):
    """Schema for track point response"""
    id: UUID
    frame_number: int
    timestamp: float
    bbox_x1: int
    bbox_y1: int
    bbox_x2: int
    bbox_y2: int
    confidence: float
    x_px: float
    y_px: float
    x_m: Optional[float] = None
    y_m: Optional[float] = None
    
    model_config = {"from_attributes": True}


class TrackResponse(BaseModel):
    """Schema for track response"""
    id: UUID
    video_id: UUID
    track_id: int
    object_class: ObjectClass
    team_side: Optional[TeamSide] = None
    player_number: Optional[int] = None
    player_name: Optional[str] = None
    first_frame: int
    last_frame: int
    total_detections: int
    
    model_config = {"from_attributes": True}


class TrackDetailResponse(TrackResponse):
    """Schema for detailed track response with points"""
    track_points: List[TrackPointResponse]
    
    model_config = {"from_attributes": True}


# ============= Calibration Schemas =============

class CalibrationMatrixCreate(BaseModel):
    """Schema for creating calibration matrix"""
    matrix: List[List[float]] = Field(..., description="3x3 homography matrix")
    source_points: List[List[float]] = Field(..., description="Source pixel coordinates")
    target_points: List[List[float]] = Field(..., description="Target real-world coordinates")
    pitch_length: float = Field(default=105.0, gt=0)
    pitch_width: float = Field(default=68.0, gt=0)
    reprojection_error: Optional[float] = None
    
    @field_validator("matrix")
    @classmethod
    def validate_matrix(cls, v):
        if len(v) != 3 or any(len(row) != 3 for row in v):
            raise ValueError("Matrix must be 3x3")
        return v


class CalibrationMatrixResponse(BaseModel):
    """Schema for calibration matrix response"""
    id: UUID
    match_id: UUID
    matrix: List[List[float]]
    source_points: List[List[float]]
    target_points: List[List[float]]
    pitch_length: float
    pitch_width: float
    reprojection_error: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ============= Team Color Schemas =============

class TeamColorCreate(BaseModel):
    """Schema for creating team color"""
    team_side: TeamSide
    team_name: str
    primary_color_rgb: List[int] = Field(..., min_length=3, max_length=3)
    secondary_color_rgb: Optional[List[int]] = Field(None, min_length=3, max_length=3)
    
    @field_validator("primary_color_rgb", "secondary_color_rgb")
    @classmethod
    def validate_rgb(cls, v):
        if v and any(c < 0 or c > 255 for c in v):
            raise ValueError("RGB values must be between 0 and 255")
        return v


class TeamColorResponse(BaseModel):
    """Schema for team color response"""
    id: UUID
    match_id: UUID
    team_side: TeamSide
    team_name: str
    primary_color_rgb: List[int]
    secondary_color_rgb: Optional[List[int]] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ============= Processing Schemas =============

class ProcessingJobResponse(BaseModel):
    """Response for processing job submission"""
    job_id: str
    video_id: UUID
    status: str
    message: str


class ProcessingStatusResponse(BaseModel):
    """Response for processing status check"""
    job_id: str
    status: str
    progress: Optional[float] = None
    error: Optional[str] = None
    result: Optional[dict] = None


# ============= Error Schemas =============

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    status_code: int
