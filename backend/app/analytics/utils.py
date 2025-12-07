"""
Analytics utilities and helper functions
"""
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


def smooth_trajectory(
    positions: List[Tuple[float, float]],
    window_size: int = 5
) -> List[Tuple[float, float]]:
    """
    Smooth trajectory using moving average
    
    Args:
        positions: List of (x, y) positions
        window_size: Size of smoothing window
        
    Returns:
        Smoothed positions
    """
    if len(positions) < window_size:
        return positions
    
    positions_array = np.array(positions)
    smoothed = np.copy(positions_array)
    
    half_window = window_size // 2
    
    for i in range(half_window, len(positions) - half_window):
        window = positions_array[i - half_window:i + half_window + 1]
        smoothed[i] = np.mean(window, axis=0)
    
    return [(x, y) for x, y in smoothed]


def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def calculate_angle(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate angle of movement vector in degrees
    
    Returns:
        Angle in degrees (0-360)
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle_rad = np.arctan2(dy, dx)
    angle_deg = np.degrees(angle_rad)
    return (angle_deg + 360) % 360


def detect_direction_changes(
    positions: List[Tuple[float, float]],
    angle_threshold: float = 45.0
) -> int:
    """
    Detect number of significant direction changes
    
    Args:
        positions: List of (x, y) positions
        angle_threshold: Minimum angle change to count as direction change
        
    Returns:
        Number of direction changes
    """
    if len(positions) < 3:
        return 0
    
    changes = 0
    prev_angle = None
    
    for i in range(1, len(positions)):
        angle = calculate_angle(positions[i - 1], positions[i])
        
        if prev_angle is not None:
            angle_diff = abs(angle - prev_angle)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
            
            if angle_diff >= angle_threshold:
                changes += 1
        
        prev_angle = angle
    
    return changes


def calculate_convex_hull_area(positions: List[Tuple[float, float]]) -> float:
    """
    Calculate area of convex hull enclosing positions
    
    Returns:
        Area in square meters
    """
    if len(positions) < 3:
        return 0.0
    
    try:
        from scipy.spatial import ConvexHull
        points = np.array(positions)
        hull = ConvexHull(points)
        return hull.volume  # In 2D, volume is area
    except Exception as e:
        logger.warning(f"Could not compute convex hull: {e}")
        return 0.0


def interpolate_missing_positions(
    positions: List[Tuple[float, float, float]],
    timestamps: List[float],
    target_fps: float = 25.0
) -> List[Tuple[float, float, float]]:
    """
    Interpolate missing positions to achieve target FPS
    
    Args:
        positions: List of (x, y, timestamp) tuples
        timestamps: List of all expected timestamps
        target_fps: Target frames per second
        
    Returns:
        Interpolated positions with consistent timestamps
    """
    if len(positions) < 2:
        return positions
    
    from scipy.interpolate import interp1d
    
    # Extract data
    pos_array = np.array([(x, y, t) for x, y, t in positions])
    original_times = pos_array[:, 2]
    original_x = pos_array[:, 0]
    original_y = pos_array[:, 1]
    
    # Create interpolation functions
    interp_x = interp1d(original_times, original_x, kind='linear', fill_value='extrapolate')
    interp_y = interp1d(original_times, original_y, kind='linear', fill_value='extrapolate')
    
    # Interpolate
    interpolated = []
    for t in timestamps:
        if min(original_times) <= t <= max(original_times):
            x = float(interp_x(t))
            y = float(interp_y(t))
            interpolated.append((x, y, t))
    
    return interpolated
