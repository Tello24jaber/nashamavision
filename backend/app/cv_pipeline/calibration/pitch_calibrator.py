"""
Pitch Calibrator
Performs camera calibration and pixel-to-meter coordinate transformation
using homography
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PitchCalibrator:
    """
    Calibrates camera view to real-world pitch coordinates
    Uses homography transformation (perspective transform)
    """
    
    def __init__(
        self,
        pitch_length: float = 105.0,
        pitch_width: float = 68.0
    ):
        """
        Initialize pitch calibrator
        
        Args:
            pitch_length: Pitch length in meters (default: 105m)
            pitch_width: Pitch width in meters (default: 68m)
        """
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        self.homography_matrix: Optional[np.ndarray] = None
        self.is_calibrated = False
        
        logger.info(
            f"PitchCalibrator initialized: {pitch_length}m x {pitch_width}m"
        )
    
    def calibrate_from_points(
        self,
        source_points: List[Tuple[float, float]],
        target_points: List[Tuple[float, float]]
    ) -> np.ndarray:
        """
        Calibrate camera using corresponding point pairs
        
        Args:
            source_points: Points in pixel coordinates [(x, y), ...]
            target_points: Points in real-world coordinates (meters) [(x, y), ...]
            
        Returns:
            Homography matrix (3x3)
        """
        if len(source_points) < 4 or len(target_points) < 4:
            raise ValueError("At least 4 point correspondences required")
        
        if len(source_points) != len(target_points):
            raise ValueError("Source and target points must have same length")
        
        # Convert to numpy arrays
        src_pts = np.array(source_points, dtype=np.float32)
        dst_pts = np.array(target_points, dtype=np.float32)
        
        # Compute homography matrix
        self.homography_matrix, status = cv2.findHomography(
            src_pts,
            dst_pts,
            method=cv2.RANSAC,
            ransacReprojThreshold=5.0
        )
        
        if self.homography_matrix is None:
            raise ValueError("Failed to compute homography matrix")
        
        self.is_calibrated = True
        
        # Compute reprojection error
        reprojection_error = self._compute_reprojection_error(
            src_pts, dst_pts, self.homography_matrix
        )
        
        logger.info(
            f"Calibration complete. Reprojection error: {reprojection_error:.2f} meters"
        )
        
        return self.homography_matrix
    
    def calibrate_auto(self, frame: np.ndarray) -> np.ndarray:
        """
        Automatic calibration using pitch line detection
        (Stub implementation - requires line detection algorithm)
        
        Args:
            frame: Frame image
            
        Returns:
            Homography matrix
        """
        # TODO: Implement automatic pitch line detection
        # 1. Detect lines using Hough transform
        # 2. Identify pitch markings (center circle, penalty box, etc.)
        # 3. Match detected lines to known pitch template
        # 4. Compute homography
        
        logger.warning("Automatic calibration not yet implemented")
        raise NotImplementedError("Automatic calibration not yet implemented")
    
    def pixel_to_meter(
        self,
        pixel_point: Tuple[float, float]
    ) -> Optional[Tuple[float, float]]:
        """
        Transform pixel coordinates to real-world meters
        
        Args:
            pixel_point: Point in pixel coordinates (x, y)
            
        Returns:
            Point in meter coordinates (x, y) or None if not calibrated
        """
        if not self.is_calibrated or self.homography_matrix is None:
            logger.warning("Calibration not performed yet")
            return None
        
        # Convert to homogeneous coordinates
        pixel_homogeneous = np.array([[pixel_point[0], pixel_point[1], 1.0]], dtype=np.float32).T
        
        # Apply homography
        meter_homogeneous = self.homography_matrix @ pixel_homogeneous
        
        # Convert back to Cartesian coordinates
        meter_x = meter_homogeneous[0, 0] / meter_homogeneous[2, 0]
        meter_y = meter_homogeneous[1, 0] / meter_homogeneous[2, 0]
        
        return (float(meter_x), float(meter_y))
    
    def pixel_to_meter_batch(
        self,
        pixel_points: List[Tuple[float, float]]
    ) -> List[Optional[Tuple[float, float]]]:
        """
        Transform multiple pixel coordinates to meters
        
        Args:
            pixel_points: List of points in pixel coordinates
            
        Returns:
            List of points in meter coordinates
        """
        return [self.pixel_to_meter(point) for point in pixel_points]
    
    def meter_to_pixel(
        self,
        meter_point: Tuple[float, float]
    ) -> Optional[Tuple[float, float]]:
        """
        Transform real-world meter coordinates to pixels (inverse transform)
        
        Args:
            meter_point: Point in meter coordinates (x, y)
            
        Returns:
            Point in pixel coordinates (x, y) or None if not calibrated
        """
        if not self.is_calibrated or self.homography_matrix is None:
            logger.warning("Calibration not performed yet")
            return None
        
        # Compute inverse homography
        inv_homography = np.linalg.inv(self.homography_matrix)
        
        # Convert to homogeneous coordinates
        meter_homogeneous = np.array([[meter_point[0], meter_point[1], 1.0]], dtype=np.float32).T
        
        # Apply inverse homography
        pixel_homogeneous = inv_homography @ meter_homogeneous
        
        # Convert back to Cartesian coordinates
        pixel_x = pixel_homogeneous[0, 0] / pixel_homogeneous[2, 0]
        pixel_y = pixel_homogeneous[1, 0] / pixel_homogeneous[2, 0]
        
        return (float(pixel_x), float(pixel_y))
    
    def _compute_reprojection_error(
        self,
        src_points: np.ndarray,
        dst_points: np.ndarray,
        homography: np.ndarray
    ) -> float:
        """
        Compute average reprojection error
        
        Args:
            src_points: Source points
            dst_points: Target points
            homography: Homography matrix
            
        Returns:
            Average reprojection error in meters
        """
        # Transform source points
        src_homogeneous = np.hstack([src_points, np.ones((len(src_points), 1))])
        projected = homography @ src_homogeneous.T
        projected = projected / projected[2, :]
        projected = projected[:2, :].T
        
        # Compute Euclidean distances
        errors = np.linalg.norm(projected - dst_points, axis=1)
        
        return float(np.mean(errors))
    
    def get_pitch_boundaries_pixels(
        self,
        frame_width: int,
        frame_height: int
    ) -> Optional[List[Tuple[float, float]]]:
        """
        Get pitch boundary corners in pixel coordinates
        
        Returns:
            List of 4 corner points in pixels
        """
        if not self.is_calibrated:
            return None
        
        # Define pitch corners in meters
        pitch_corners = [
            (0, 0),  # Bottom-left
            (self.pitch_length, 0),  # Bottom-right
            (self.pitch_length, self.pitch_width),  # Top-right
            (0, self.pitch_width),  # Top-left
        ]
        
        # Transform to pixels
        pixel_corners = [
            self.meter_to_pixel(corner) for corner in pitch_corners
        ]
        
        return pixel_corners
    
    def __repr__(self):
        return (
            f"PitchCalibrator(pitch={self.pitch_length}x{self.pitch_width}m, "
            f"calibrated={self.is_calibrated})"
        )
