"""
Detection Engine
Object detection using YOLO models
"""
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Detection:
    """Represents a single object detection"""
    
    def __init__(
        self,
        bbox: List[int],
        confidence: float,
        class_id: int,
        class_name: str
    ):
        self.bbox = bbox  # [x1, y1, x2, y2]
        self.confidence = confidence
        self.class_id = class_id
        self.class_name = class_name
    
    @property
    def center(self) -> tuple[float, float]:
        """Get center point of bounding box"""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    @property
    def area(self) -> float:
        """Get area of bounding box"""
        x1, y1, x2, y2 = self.bbox
        return (x2 - x1) * (y2 - y1)
    
    def __repr__(self):
        return f"Detection(class={self.class_name}, conf={self.confidence:.2f}, bbox={self.bbox})"


class DetectionEngine:
    """
    YOLO-based object detection engine
    Detects players, ball, and referees
    """
    
    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = "cpu"
    ):
        """
        Initialize detection engine
        
        Args:
            model_path: Path to YOLO model weights
            confidence_threshold: Minimum confidence for detections
            iou_threshold: IoU threshold for NMS
            device: Device to run inference on ('cpu' or 'cuda')
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        self.model = None
        
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model"""
        try:
            # Lazy import to avoid loading if not needed
            from ultralytics import YOLO
            
            if not Path(self.model_path).exists():
                logger.warning(f"Model not found at {self.model_path}, downloading default model...")
                # Download default model
                self.model = YOLO("yolov8x.pt")
            else:
                self.model = YOLO(self.model_path)
            
            # Set device
            if self.device == "cuda":
                self.model.to("cuda")
            
            logger.info(f"YOLO model loaded: {self.model_path}")
            
        except ImportError:
            logger.error("ultralytics package not installed. Install with: pip install ultralytics")
            raise
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}", exc_info=True)
            raise
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Run object detection on a frame
        
        Args:
            frame: Input frame (BGR format from OpenCV)
            
        Returns:
            List of Detection objects
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            # Run inference
            results = self.model.predict(
                frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False
            )
            
            detections = []
            
            # Parse results
            for result in results:
                boxes = result.boxes
                
                for i in range(len(boxes)):
                    # Get bounding box coordinates
                    box = boxes.xyxy[i].cpu().numpy()
                    x1, y1, x2, y2 = map(int, box)
                    
                    # Get confidence and class
                    confidence = float(boxes.conf[i].cpu().numpy())
                    class_id = int(boxes.cls[i].cpu().numpy())
                    class_name = result.names[class_id]
                    
                    # Filter for relevant classes (person, sports ball)
                    # COCO classes: 0 = person, 32 = sports ball
                    if class_id in [0, 32]:
                        detection = Detection(
                            bbox=[x1, y1, x2, y2],
                            confidence=confidence,
                            class_id=class_id,
                            class_name=class_name
                        )
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection failed: {e}", exc_info=True)
            return []
    
    def detect_batch(self, frames: List[np.ndarray]) -> List[List[Detection]]:
        """
        Run detection on multiple frames (batch processing)
        
        Args:
            frames: List of frames
            
        Returns:
            List of detection lists for each frame
        """
        # For now, process sequentially
        # TODO: Implement true batch processing for efficiency
        return [self.detect(frame) for frame in frames]
    
    def __repr__(self):
        return (
            f"DetectionEngine(model={self.model_path}, "
            f"conf={self.confidence_threshold}, device={self.device})"
        )
