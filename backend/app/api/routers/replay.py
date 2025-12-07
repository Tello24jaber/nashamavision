"""
Replay API Router
Phase 4: Virtual Match Engine endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
import logging

from app.db.session import get_db
from app.replay.service import ReplayService
from app.schemas.replay import (
    ReplaySummaryResponse,
    ReplayTimelineResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/replay", tags=["Replay"])


@router.get(
    "/match/{match_id}/summary",
    response_model=ReplaySummaryResponse,
    summary="Get replay summary for a match",
    description="Returns match metadata, player list, and available replay segments"
)
async def get_replay_summary(
    match_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get replay summary and metadata
    
    Returns:
    - Match information (teams, date, duration)
    - List of all players with colors and teams
    - Available segments (full match, halves)
    - Total event count
    """
    try:
        service = ReplayService(db)
        summary = service.get_replay_summary(match_id)
        return summary
    except ValueError as e:
        logger.error(f"Error fetching replay summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_replay_summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch replay summary"
        )


@router.get(
    "/match/{match_id}/timeline",
    response_model=ReplayTimelineResponse,
    summary="Get replay timeline data",
    description="Returns time-series player positions, ball positions, and events for replay visualization"
)
async def get_replay_timeline(
    match_id: UUID,
    start_time: Optional[float] = Query(None, ge=0, description="Start time in seconds"),
    end_time: Optional[float] = Query(None, ge=0, description="End time in seconds"),
    fps: Optional[float] = Query(10, ge=1, le=60, description="Target FPS (1-60)"),
    include_ball: Optional[bool] = Query(True, description="Include ball tracking"),
    include_events: Optional[bool] = Query(True, description="Include events"),
    db: Session = Depends(get_db)
):
    """
    Get replay timeline data for visualization
    
    Query Parameters:
    - start_time: Start time in seconds (default: 0)
    - end_time: End time in seconds (default: match duration)
    - fps: Target frames per second (default: 10, max: 60)
    - include_ball: Include ball tracking data (default: true)
    - include_events: Include event data (default: true)
    
    Returns:
    - Player positions over time (resampled to target FPS)
    - Ball positions over time
    - Events with timing and spatial data
    """
    try:
        # Validate time range
        if start_time is not None and end_time is not None and start_time >= end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time must be less than end_time"
            )
        
        service = ReplayService(db)
        timeline = service.get_replay_timeline(
            match_id=match_id,
            start_time=start_time,
            end_time=end_time,
            fps=fps,
            include_ball=include_ball,
            include_events=include_events
        )
        return timeline
    except ValueError as e:
        logger.error(f"Error fetching replay timeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_replay_timeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch replay timeline"
        )


@router.get(
    "/pitch/dimensions",
    summary="Get pitch dimensions",
    description="Returns standard pitch dimensions for rendering"
)
async def get_pitch_dimensions():
    """
    Get pitch dimensions for replay rendering
    
    Returns standard football pitch dimensions in meters
    """
    return {
        "length": ReplayService.PITCH_LENGTH,
        "width": ReplayService.PITCH_WIDTH,
        "units": "meters"
    }
