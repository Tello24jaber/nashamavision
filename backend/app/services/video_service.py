"""
Video Service
Handles video upload, validation, and metadata extraction
"""
import cv2
import tempfile
import logging
from pathlib import Path
from uuid import UUID, uuid4
from datetime import datetime
from typing import BinaryIO
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.models import Video, ProcessingStatus
from app.schemas.schemas import VideoUploadResponse, VideoMetadata
from app.storage.storage_interface import StorageInterface, get_storage
from app.core.config import settings
from app.workers.tasks import process_video_task

logger = logging.getLogger(__name__)


class VideoService:
    """Service for handling video operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.storage: StorageInterface = get_storage()
    
    async def process_video_upload(
        self,
        file: UploadFile,
        match_id: UUID,
        filename: str
    ) -> VideoUploadResponse:
        """
        Process video upload:
        1. Validate file
        2. Extract metadata
        3. Save to storage
        4. Create database record
        5. Dispatch processing job
        """
        # Generate unique video ID
        video_id = uuid4()
        
        # Save uploaded file to temporary location for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_file:
            tmp_path = tmp_file.name
            
            # Write uploaded content to temp file
            content = await file.read()
            tmp_file.write(content)
            tmp_file.flush()
        
        try:
            # Extract video metadata
            metadata = self._extract_video_metadata(tmp_path)
            
            # Validate video duration
            if metadata.duration < settings.min_video_duration:
                raise ValueError(
                    f"Video too short. Minimum duration: {settings.min_video_duration}s"
                )
            
            if metadata.duration > settings.max_video_duration:
                raise ValueError(
                    f"Video too long. Maximum duration: {settings.max_video_duration}s"
                )
            
            # Upload to storage
            storage_path = f"videos/raw/{match_id}/{video_id}{Path(filename).suffix}"
            
            with open(tmp_path, "rb") as f:
                self.storage.upload_file(f, storage_path)
            
            logger.info(f"Uploaded video to storage: {storage_path}")
            
            # Create database record
            video = Video(
                id=video_id,
                match_id=match_id,
                filename=filename,
                file_size=len(content),
                file_extension=Path(filename).suffix,
                storage_path=storage_path,
                duration=metadata.duration,
                fps=metadata.fps,
                width=metadata.width,
                height=metadata.height,
                codec=metadata.codec,
                bitrate=metadata.bitrate,
                total_frames=metadata.total_frames,
                status=ProcessingStatus.PENDING,
            )
            
            self.db.add(video)
            self.db.commit()
            self.db.refresh(video)
            
            logger.info(f"Created video record: {video_id}")
            
            # Dispatch processing job (optional - skip if Redis not available)
            try:
                task = process_video_task.delay(str(video_id))
                logger.info(f"Dispatched processing task: {task.id}")
            except Exception as e:
                logger.warning(f"Could not dispatch processing task (Redis unavailable): {e}")
                logger.info("Video uploaded successfully but processing will need to be triggered manually")
            
            return VideoUploadResponse(
                video_id=video_id,
                match_id=match_id,
                filename=filename,
                file_size=len(content),
                storage_path=storage_path,
                metadata=metadata,
                status=ProcessingStatus.PENDING,
                message="Video uploaded successfully. Processing started."
            )
            
        except Exception as e:
            logger.error(f"Error processing video upload: {e}", exc_info=True)
            raise
        
        finally:
            # Clean up temporary file
            Path(tmp_path).unlink(missing_ok=True)
    
    def _extract_video_metadata(self, video_path: str) -> VideoMetadata:
        """
        Extract metadata from video file using OpenCV
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError("Failed to open video file")
            
            # Extract properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            bitrate = int(cap.get(cv2.CAP_PROP_BITRATE)) if cap.get(cv2.CAP_PROP_BITRATE) else None
            
            # Calculate duration
            duration = frame_count / fps if fps > 0 else 0
            
            # Decode codec
            codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
            
            cap.release()
            
            metadata = VideoMetadata(
                duration=duration,
                fps=fps,
                width=width,
                height=height,
                codec=codec,
                bitrate=bitrate,
                total_frames=frame_count
            )
            
            logger.info(f"Extracted metadata: {metadata}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract video metadata: {e}", exc_info=True)
            raise ValueError(f"Invalid video file: {e}")
