"""
Physical Metrics Engine
Computes physical performance metrics from tracking data
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class TrackPointData:
    """Data structure for a single track point"""
    timestamp: float  # seconds
    frame_number: int
    x_m: float  # position in meters
    y_m: float
    x_px: float  # position in pixels (backup)
    y_px: float


@dataclass
class PhysicalMetrics:
    """Complete physical metrics for a player"""
    # Distance metrics
    total_distance_m: float
    total_distance_km: float
    
    # Speed metrics
    avg_speed_mps: float
    avg_speed_kmh: float
    top_speed_mps: float
    top_speed_kmh: float
    
    # Intensity metrics
    high_intensity_distance_m: float  # distance covered above threshold
    sprint_distance_m: float  # distance covered at sprint speed
    sprint_count: int  # number of distinct sprint events
    
    # Acceleration metrics
    max_acceleration_mps2: float
    max_deceleration_mps2: float
    avg_acceleration_mps2: float
    
    # Stamina metrics
    stamina_index: float  # 0-100 scale
    distance_per_minute: List[float]  # distance covered per minute
    
    # Time series data
    speed_timeseries: List[Tuple[float, float]]  # (timestamp, speed_mps)
    acceleration_timeseries: List[Tuple[float, float]]  # (timestamp, acceleration)
    stamina_curve: List[Tuple[float, float]]  # (timestamp, stamina_value)


class PhysicalMetricsEngine:
    """
    Computes physical performance metrics from track point data
    """
    
    # Thresholds (configurable)
    HIGH_INTENSITY_THRESHOLD_MPS = 5.5  # ~19.8 km/h
    SPRINT_THRESHOLD_MPS = 7.0  # ~25.2 km/h
    SPRINT_MIN_DURATION = 1.0  # seconds
    STAMINA_WINDOW_SIZE = 60  # seconds for rolling average
    
    def __init__(
        self,
        high_intensity_threshold_mps: float = HIGH_INTENSITY_THRESHOLD_MPS,
        sprint_threshold_mps: float = SPRINT_THRESHOLD_MPS,
        sprint_min_duration: float = SPRINT_MIN_DURATION
    ):
        self.high_intensity_threshold = high_intensity_threshold_mps
        self.sprint_threshold = sprint_threshold_mps
        self.sprint_min_duration = sprint_min_duration
    
    def compute_metrics(self, track_points: List[TrackPointData]) -> Optional[PhysicalMetrics]:
        """
        Compute all physical metrics for a player track
        
        Args:
            track_points: List of track points ordered by timestamp
            
        Returns:
            PhysicalMetrics object or None if insufficient data
        """
        if len(track_points) < 2:
            logger.warning("Insufficient track points for metric computation")
            return None
        
        # Sort by timestamp to ensure correct ordering
        track_points = sorted(track_points, key=lambda p: p.timestamp)
        
        # Check if metric coordinates are available
        has_metric_coords = all(p.x_m is not None and p.y_m is not None for p in track_points)
        
        if not has_metric_coords:
            logger.warning("Track points missing metric coordinates (x_m, y_m). Cannot compute metrics.")
            return None
        
        # Compute distance and speed
        distances, speeds, timestamps = self._compute_distance_and_speed(track_points)
        
        # Compute acceleration
        accelerations = self._compute_acceleration(speeds, timestamps)
        
        # Compute high-intensity and sprint metrics
        high_intensity_distance = self._compute_high_intensity_distance(distances, speeds)
        sprint_distance, sprint_count = self._compute_sprint_metrics(distances, speeds, timestamps)
        
        # Compute stamina metrics
        distance_per_minute = self._compute_distance_per_minute(track_points, distances, timestamps)
        stamina_index = self._compute_stamina_index(distance_per_minute, speeds)
        stamina_curve = self._compute_stamina_curve(speeds, timestamps)
        
        # Aggregate metrics
        total_distance = np.sum(distances)
        avg_speed = np.mean(speeds) if len(speeds) > 0 else 0.0
        top_speed = np.max(speeds) if len(speeds) > 0 else 0.0
        max_accel = np.max(accelerations) if len(accelerations) > 0 else 0.0
        max_decel = np.min(accelerations) if len(accelerations) > 0 else 0.0
        avg_accel = np.mean(np.abs(accelerations)) if len(accelerations) > 0 else 0.0
        
        # Build time series
        speed_timeseries = [(timestamps[i], speeds[i]) for i in range(len(speeds))]
        acceleration_timeseries = [(timestamps[i], accelerations[i]) for i in range(len(accelerations))]
        
        return PhysicalMetrics(
            total_distance_m=total_distance,
            total_distance_km=total_distance / 1000.0,
            avg_speed_mps=avg_speed,
            avg_speed_kmh=avg_speed * 3.6,
            top_speed_mps=top_speed,
            top_speed_kmh=top_speed * 3.6,
            high_intensity_distance_m=high_intensity_distance,
            sprint_distance_m=sprint_distance,
            sprint_count=sprint_count,
            max_acceleration_mps2=max_accel,
            max_deceleration_mps2=max_decel,
            avg_acceleration_mps2=avg_accel,
            stamina_index=stamina_index,
            distance_per_minute=distance_per_minute,
            speed_timeseries=speed_timeseries,
            acceleration_timeseries=acceleration_timeseries,
            stamina_curve=stamina_curve
        )
    
    def _compute_distance_and_speed(
        self, track_points: List[TrackPointData]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute point-to-point distance and instantaneous speed
        
        Returns:
            distances: array of distances between consecutive points (meters)
            speeds: array of instantaneous speeds (m/s)
            timestamps: array of timestamps for each speed measurement
        """
        distances = []
        speeds = []
        timestamps = []
        
        for i in range(1, len(track_points)):
            p1 = track_points[i - 1]
            p2 = track_points[i]
            
            # Euclidean distance
            dx = p2.x_m - p1.x_m
            dy = p2.y_m - p1.y_m
            dist = np.sqrt(dx**2 + dy**2)
            
            # Time difference
            dt = p2.timestamp - p1.timestamp
            
            if dt > 0:
                speed = dist / dt
                distances.append(dist)
                speeds.append(speed)
                timestamps.append(p2.timestamp)
        
        return np.array(distances), np.array(speeds), np.array(timestamps)
    
    def _compute_acceleration(
        self, speeds: np.ndarray, timestamps: np.ndarray
    ) -> np.ndarray:
        """
        Compute acceleration from speed time series
        
        Returns:
            accelerations: array of instantaneous accelerations (m/s^2)
        """
        if len(speeds) < 2:
            return np.array([])
        
        accelerations = []
        
        for i in range(1, len(speeds)):
            dv = speeds[i] - speeds[i - 1]
            dt = timestamps[i] - timestamps[i - 1]
            
            if dt > 0:
                accel = dv / dt
                accelerations.append(accel)
            else:
                accelerations.append(0.0)
        
        return np.array(accelerations)
    
    def _compute_high_intensity_distance(
        self, distances: np.ndarray, speeds: np.ndarray
    ) -> float:
        """
        Compute distance covered above high-intensity threshold
        """
        high_intensity_mask = speeds >= self.high_intensity_threshold
        return np.sum(distances[high_intensity_mask])
    
    def _compute_sprint_metrics(
        self, distances: np.ndarray, speeds: np.ndarray, timestamps: np.ndarray
    ) -> Tuple[float, int]:
        """
        Compute sprint distance and count
        
        A sprint is defined as sustained speed above sprint threshold
        for at least sprint_min_duration seconds
        
        Returns:
            sprint_distance: total distance covered during sprints
            sprint_count: number of distinct sprint events
        """
        sprint_mask = speeds >= self.sprint_threshold
        sprint_distance = np.sum(distances[sprint_mask])
        
        # Count distinct sprint events
        sprint_count = 0
        in_sprint = False
        sprint_start_time = 0.0
        
        for i, is_sprinting in enumerate(sprint_mask):
            if is_sprinting and not in_sprint:
                # Start of a potential sprint
                in_sprint = True
                sprint_start_time = timestamps[i]
            elif not is_sprinting and in_sprint:
                # End of sprint
                sprint_duration = timestamps[i - 1] - sprint_start_time
                if sprint_duration >= self.sprint_min_duration:
                    sprint_count += 1
                in_sprint = False
        
        # Check if still in sprint at the end
        if in_sprint:
            sprint_duration = timestamps[-1] - sprint_start_time
            if sprint_duration >= self.sprint_min_duration:
                sprint_count += 1
        
        return sprint_distance, sprint_count
    
    def _compute_distance_per_minute(
        self, track_points: List[TrackPointData], distances: np.ndarray, timestamps: np.ndarray
    ) -> List[float]:
        """
        Compute distance covered per minute of the match
        
        Returns:
            List of distances per minute
        """
        if len(track_points) == 0:
            return []
        
        total_duration = track_points[-1].timestamp
        num_minutes = int(np.ceil(total_duration / 60.0))
        
        distance_per_minute = [0.0] * num_minutes
        
        for i, dist in enumerate(distances):
            minute_idx = int(timestamps[i] / 60.0)
            if minute_idx < num_minutes:
                distance_per_minute[minute_idx] += dist
        
        return distance_per_minute
    
    def _compute_stamina_index(
        self, distance_per_minute: List[float], speeds: np.ndarray
    ) -> float:
        """
        Compute stamina index (0-100 scale)
        
        Simple formula: 
        - StaminaIndex = 100 - (coefficient_of_variation * scale_factor)
        - Higher values indicate more consistent performance
        - Lower values indicate fatigue/decline over time
        """
        if len(distance_per_minute) == 0:
            return 0.0
        
        distances_array = np.array(distance_per_minute)
        
        # Remove zeros for better calculation
        non_zero_distances = distances_array[distances_array > 0]
        
        if len(non_zero_distances) < 2:
            return 50.0  # Default neutral value
        
        mean_dist = np.mean(non_zero_distances)
        std_dist = np.std(non_zero_distances)
        
        if mean_dist == 0:
            return 50.0
        
        # Coefficient of variation
        cv = (std_dist / mean_dist) * 100
        
        # Stamina index (inverse relationship with CV)
        stamina_index = 100.0 - min(cv, 100.0)
        
        return max(0.0, stamina_index)
    
    def _compute_stamina_curve(
        self, speeds: np.ndarray, timestamps: np.ndarray
    ) -> List[Tuple[float, float]]:
        """
        Compute stamina curve using rolling average of speed
        
        Returns:
            List of (timestamp, rolling_avg_speed) tuples
        """
        if len(speeds) == 0:
            return []
        
        window_size = self.STAMINA_WINDOW_SIZE
        stamina_curve = []
        
        for i, ts in enumerate(timestamps):
            # Find points within window
            window_start = ts - window_size / 2
            window_end = ts + window_size / 2
            
            mask = (timestamps >= window_start) & (timestamps <= window_end)
            window_speeds = speeds[mask]
            
            if len(window_speeds) > 0:
                avg_speed = np.mean(window_speeds)
                stamina_curve.append((ts, avg_speed))
        
        return stamina_curve


class TeamMetricsEngine:
    """
    Computes team-level tactical metrics
    """
    
    def compute_team_centroid(
        self, player_positions: List[Tuple[float, float]]
    ) -> Tuple[float, float]:
        """
        Compute team centroid (center of mass)
        
        Args:
            player_positions: List of (x, y) positions in meters
            
        Returns:
            (centroid_x, centroid_y)
        """
        if len(player_positions) == 0:
            return (0.0, 0.0)
        
        positions = np.array(player_positions)
        centroid = np.mean(positions, axis=0)
        return tuple(centroid)
    
    def compute_team_spread(
        self, player_positions: List[Tuple[float, float]]
    ) -> Dict[str, float]:
        """
        Compute team spread metrics (width, height, compactness)
        
        Returns:
            Dict with 'width', 'height', 'area', 'compactness'
        """
        if len(player_positions) < 2:
            return {"width": 0.0, "height": 0.0, "area": 0.0, "compactness": 0.0}
        
        positions = np.array(player_positions)
        
        # Width and height (range in x and y)
        width = np.max(positions[:, 0]) - np.min(positions[:, 0])
        height = np.max(positions[:, 1]) - np.min(positions[:, 1])
        area = width * height
        
        # Compactness (standard deviation from centroid)
        centroid = np.mean(positions, axis=0)
        distances = np.sqrt(np.sum((positions - centroid)**2, axis=1))
        compactness = np.mean(distances)
        
        return {
            "width": width,
            "height": height,
            "area": area,
            "compactness": compactness
        }
