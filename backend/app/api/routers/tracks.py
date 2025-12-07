"""
Tracks Router
Handles track data retrieval
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models.models import Track, TrackPoint, Video
from app.schemas.schemas import TrackResponse, TrackDetailResponse

router = APIRouter()


@router.get("/video/{video_id}", response_model=List[TrackResponse])
async def list_tracks_by_video(
    video_id: UUID,
    object_class: Optional[str] = None,
    team_side: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all tracks for a specific video
    
    Optional filters:
    - object_class: Filter by object class (player, ball, referee, goalkeeper)
    - team_side: Filter by team side (home, away, referee, unknown)
    """
    # Verify video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )
    
    query = db.query(Track).filter(Track.video_id == video_id)
    
    if object_class:
        query = query.filter(Track.object_class == object_class)
    
    if team_side:
        query = query.filter(Track.team_side == team_side)
    
    tracks = query.offset(skip).limit(limit).all()
    return tracks


@router.get("/{track_id}", response_model=TrackDetailResponse)
async def get_track_detail(
    track_id: UUID,
    include_points: bool = Query(default=True),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific track
    
    - include_points: Whether to include all track points (default: True)
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track with ID {track_id} not found"
        )
    
    if not include_points:
        # Return track without points
        return track
    
    # Load track points
    track_points = db.query(TrackPoint).filter(
        TrackPoint.track_id == track_id
    ).order_by(TrackPoint.frame_number).all()
    
    # Manually attach track_points to track object
    track_dict = {
        "id": track.id,
        "video_id": track.video_id,
        "track_id": track.track_id,
        "object_class": track.object_class,
        "team_side": track.team_side,
        "player_number": track.player_number,
        "player_name": track.player_name,
        "first_frame": track.first_frame,
        "last_frame": track.last_frame,
        "total_detections": track.total_detections,
        "track_points": track_points
    }
    
    return track_dict


@router.get("/{track_id}/points", response_model=List)
async def get_track_points(
    track_id: UUID,
    frame_start: Optional[int] = None,
    frame_end: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get track points for a specific track
    
    Optional filters:
    - frame_start: Start frame number
    - frame_end: End frame number
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track with ID {track_id} not found"
        )
    
    query = db.query(TrackPoint).filter(TrackPoint.track_id == track_id)
    
    if frame_start is not None:
        query = query.filter(TrackPoint.frame_number >= frame_start)
    
    if frame_end is not None:
        query = query.filter(TrackPoint.frame_number <= frame_end)
    
    points = query.order_by(TrackPoint.frame_number).all()
    return points
