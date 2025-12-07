"""
Frame Extractor
Extracts frames from video for processing
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Generator, Optional
import logging

logger = logging.getLogger(__name__)


class FrameExtractor:
    """
    Extracts frames from video file at specified FPS
    """
    
    def __init__(self, video_path: str, target_fps: Optional[int] = None):
        """
        Initialize frame extractor
        
        Args:
            video_path: Path to video file
            target_fps: Target FPS for extraction (None = use video FPS)
        """
        self.video_path = video_path
        self.target_fps = target_fps
        self.cap = None
        self.video_fps = None
        self.total_frames = None
        self.width = None
        self.height = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize video capture and extract properties"""
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video: {self.video_path}")
        
        self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if self.target_fps is None:
            self.target_fps = self.video_fps
        
        logger.info(
            f"Video initialized: {self.width}x{self.height} @ {self.video_fps}fps, "
            f"{self.total_frames} frames"
        )
    
    def extract_frames(self) -> Generator[tuple[int, np.ndarray], None, None]:
        """
        Generator that yields (frame_number, frame_image) tuples
        
        Yields:
            tuple: (frame_number, frame_image)
        """
        if not self.cap or not self.cap.isOpened():
            raise RuntimeError("Video capture not initialized")
        
        frame_interval = int(self.video_fps / self.target_fps) if self.target_fps < self.video_fps else 1
        frame_number = 0
        extracted_count = 0
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                break
            
            # Extract frame at specified interval
            if frame_number % frame_interval == 0:
                yield frame_number, frame
                extracted_count += 1
            
            frame_number += 1
        
        logger.info(f"Extracted {extracted_count} frames from {self.total_frames} total frames")
    
    def get_frame_at_index(self, frame_index: int) -> Optional[np.ndarray]:
        """
        Get a specific frame by index
        
        Args:
            frame_index: Frame index to retrieve
            
        Returns:
            Frame image or None if failed
        """
        if not self.cap or not self.cap.isOpened():
            raise RuntimeError("Video capture not initialized")
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = self.cap.read()
        
        return frame if ret else None
    
    def get_frame_at_timestamp(self, timestamp: float) -> Optional[np.ndarray]:
        """
        Get frame at specific timestamp (in seconds)
        
        Args:
            timestamp: Timestamp in seconds
            
        Returns:
            Frame image or None if failed
        """
        frame_index = int(timestamp * self.video_fps)
        return self.get_frame_at_index(frame_index)
    
    def release(self):
        """Release video capture resources"""
        if self.cap:
            self.cap.release()
            logger.info("Video capture released")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
    
    def __del__(self):
        self.release()
