"""
Videos Router
Handles video upload and management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging

from app.db.session import get_db
from app.models.models import Video, Match, ProcessingStatus
from app.schemas.schemas import VideoResponse, VideoListResponse, VideoUploadResponse
from app.services.video_service import VideoService
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=VideoUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    file: UploadFile = File(...),
    home_team: str = Form(...),
    away_team: str = Form(...),
    match_date: str = Form(None),
    competition: str = Form(None),
    venue: str = Form(None),
    match_id: UUID = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a video file for a match
    
    - Validates file format and size
    - Extracts metadata (FPS, resolution, duration)
    - Stores in object storage
    - Dispatches processing job
    """
    # Create match if not provided
    if not match_id:
        from datetime import datetime
        match = Match(
            name=f"{home_team} vs {away_team}",
            home_team=home_team,
            away_team=away_team,
            match_date=datetime.fromisoformat(match_date) if match_date else datetime.now(),
            competition=competition,
            venue=venue
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        match_id = match.id
        logger.info(f"Created new match: {match_id} ({home_team} vs {away_team})")
    else:
        # Verify match exists
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match with ID {match_id} not found"
            )
    
    # Validate file extension
    file_extension = f".{file.filename.split('.')[-1].lower()}"
    if file_extension not in settings.allowed_video_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not allowed. Allowed types: {settings.allowed_video_extensions}"
        )
    
    # Initialize video service
    video_service = VideoService(db)
    
    try:
        # Process upload (saves file, extracts metadata, creates DB record)
        result = await video_service.process_video_upload(
            file=file,
            match_id=match_id,
            filename=file.filename
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error uploading video: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload video"
        )


@router.get("/", response_model=VideoListResponse)
async def list_videos(
    match_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List videos with optional filtering by match
    """
    query = db.query(Video)
    
    if match_id:
        query = query.filter(Video.match_id == match_id)
    
    total = query.count()
    videos = query.offset(skip).limit(limit).all()
    
    return VideoListResponse(videos=videos, total=total)


@router.get("/match/{match_id}", response_model=VideoListResponse)
async def get_videos_by_match(
    match_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all videos for a specific match
    """
    videos = db.query(Video).filter(Video.match_id == match_id).all()
    
    if not videos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No videos found for match {match_id}"
        )
    
    return VideoListResponse(videos=videos, total=len(videos))


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific video by ID
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )
    return video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(video_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a video and its associated data
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )
    
    # TODO: Delete from object storage as well
    
    db.delete(video)
    db.commit()
    return None


@router.get("/{video_id}/status", response_model=dict)
async def get_video_processing_status(video_id: UUID, db: Session = Depends(get_db)):
    """
    Get the processing status of a video
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )
    
    return {
        "video_id": video.id,
        "status": video.status,
        "processing_started_at": video.processing_started_at,
        "processing_completed_at": video.processing_completed_at,
        "processing_error": video.processing_error,
    }
