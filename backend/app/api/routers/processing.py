"""
Processing Router
Handles background processing job management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from app.db.session import get_db
from app.models.models import Video
from app.schemas.schemas import ProcessingJobResponse, ProcessingStatusResponse
from app.workers.tasks import process_video_task

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/start/{video_id}", response_model=ProcessingJobResponse)
async def start_video_processing(
    video_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Start video processing job
    
    Dispatches a Celery task to:
    - Extract frames
    - Run object detection
    - Perform tracking
    - Classify teams
    - Calibrate pitch
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )
    
    if video.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video is already being processed"
        )
    
    if video.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video has already been processed"
        )
    
    try:
        # Dispatch Celery task
        task = process_video_task.delay(str(video_id))
        
        logger.info(f"Started processing for video {video_id}, task_id: {task.id}")
        
        return ProcessingJobResponse(
            job_id=task.id,
            video_id=video_id,
            status="queued",
            message="Video processing job has been queued"
        )
        
    except Exception as e:
        logger.error(f"Failed to start processing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start video processing"
        )


@router.get("/status/{job_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(job_id: str):
    """
    Get the status of a processing job
    """
    from app.workers.celery_app import celery_app
    
    try:
        task = celery_app.AsyncResult(job_id)
        
        response = ProcessingStatusResponse(
            job_id=job_id,
            status=task.state.lower(),
            progress=None,
            error=None,
            result=None
        )
        
        if task.state == "PENDING":
            response.status = "pending"
        elif task.state == "STARTED":
            response.status = "processing"
        elif task.state == "SUCCESS":
            response.status = "completed"
            response.result = task.result
        elif task.state == "FAILURE":
            response.status = "failed"
            response.error = str(task.info)
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to get task status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve processing status"
        )


@router.post("/retry/{video_id}", response_model=ProcessingJobResponse)
async def retry_video_processing(
    video_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retry video processing for a failed job
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )
    
    if video.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only retry failed videos. Current status: {video.status}"
        )
    
    try:
        # Reset status and retry
        video.status = "pending"
        video.processing_error = None
        db.commit()
        
        task = process_video_task.delay(str(video_id))
        
        logger.info(f"Retrying processing for video {video_id}, task_id: {task.id}")
        
        return ProcessingJobResponse(
            job_id=task.id,
            video_id=video_id,
            status="queued",
            message="Video processing job has been requeued"
        )
        
    except Exception as e:
        logger.error(f"Failed to retry processing: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retry video processing"
        )
