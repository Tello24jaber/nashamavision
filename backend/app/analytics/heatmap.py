"""
Heatmap Generation Engine
Creates 2D spatial heatmaps for player and team analysis
"""
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class HeatmapConfig:
    """Configuration for heatmap generation"""
    pitch_length: float = 105.0  # meters
    pitch_width: float = 68.0  # meters
    grid_width: int = 40  # number of horizontal bins
    grid_height: int = 25  # number of vertical bins
    smoothing_sigma: float = 1.0  # Gaussian smoothing parameter


@dataclass
class Heatmap:
    """Heatmap data structure"""
    data: np.ndarray  # 2D array of intensity values
    grid_width: int
    grid_height: int
    pitch_length: float
    pitch_width: float
    total_positions: int
    max_intensity: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "data": self.data.tolist(),
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "pitch_length": self.pitch_length,
            "pitch_width": self.pitch_width,
            "total_positions": self.total_positions,
            "max_intensity": float(self.max_intensity)
        }
    
    def to_normalized_dict(self) -> Dict:
        """Convert to dictionary with normalized intensities (0-1)"""
        normalized_data = self.data / self.max_intensity if self.max_intensity > 0 else self.data
        return {
            "data": normalized_data.tolist(),
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "pitch_length": self.pitch_length,
            "pitch_width": self.pitch_width,
            "total_positions": self.total_positions,
            "max_intensity": float(self.max_intensity)
        }


class HeatmapEngine:
    """
    Generates spatial heatmaps from position data
    """
    
    def __init__(self, config: Optional[HeatmapConfig] = None):
        self.config = config or HeatmapConfig()
    
    def generate_heatmap(
        self,
        positions: List[Tuple[float, float]],
        normalize: bool = True,
        apply_smoothing: bool = True
    ) -> Optional[Heatmap]:
        """
        Generate a 2D heatmap from position data
        
        Args:
            positions: List of (x, y) coordinates in meters
            normalize: Whether to normalize intensities to 0-1 range
            apply_smoothing: Whether to apply Gaussian smoothing
            
        Returns:
            Heatmap object or None if insufficient data
        """
        if len(positions) == 0:
            logger.warning("No positions provided for heatmap generation")
            return None
        
        # Initialize grid
        grid = np.zeros((self.config.grid_height, self.config.grid_width))
        
        # Calculate bin sizes
        bin_width = self.config.pitch_length / self.config.grid_width
        bin_height = self.config.pitch_width / self.config.grid_height
        
        # Populate grid
        for x, y in positions:
            # Convert position to grid indices
            col = int(x / bin_width)
            row = int(y / bin_height)
            
            # Clamp to grid boundaries
            col = max(0, min(col, self.config.grid_width - 1))
            row = max(0, min(row, self.config.grid_height - 1))
            
            grid[row, col] += 1
        
        # Apply Gaussian smoothing if requested
        if apply_smoothing:
            grid = self._apply_gaussian_smoothing(grid, sigma=self.config.smoothing_sigma)
        
        # Get statistics
        total_positions = len(positions)
        max_intensity = np.max(grid)
        
        # Normalize if requested
        if normalize and max_intensity > 0:
            grid = grid / max_intensity
            max_intensity = 1.0
        
        return Heatmap(
            data=grid,
            grid_width=self.config.grid_width,
            grid_height=self.config.grid_height,
            pitch_length=self.config.pitch_length,
            pitch_width=self.config.pitch_width,
            total_positions=total_positions,
            max_intensity=max_intensity
        )
    
    def generate_team_heatmap(
        self,
        player_positions: Dict[str, List[Tuple[float, float]]],
        normalize: bool = True,
        apply_smoothing: bool = True
    ) -> Optional[Heatmap]:
        """
        Generate combined heatmap for all players in a team
        
        Args:
            player_positions: Dict mapping player_id to list of positions
            normalize: Whether to normalize intensities
            apply_smoothing: Whether to apply Gaussian smoothing
            
        Returns:
            Heatmap object
        """
        # Combine all positions
        all_positions = []
        for positions in player_positions.values():
            all_positions.extend(positions)
        
        return self.generate_heatmap(all_positions, normalize, apply_smoothing)
    
    def generate_zone_occupancy(
        self,
        positions: List[Tuple[float, float]],
        zones: List[Tuple[float, float, float, float]]
    ) -> Dict[int, float]:
        """
        Calculate percentage of time spent in each zone
        
        Args:
            positions: List of (x, y) coordinates in meters
            zones: List of zones defined as (x_min, y_min, x_max, y_max)
            
        Returns:
            Dict mapping zone index to occupancy percentage
        """
        if len(positions) == 0:
            return {i: 0.0 for i in range(len(zones))}
        
        zone_counts = {i: 0 for i in range(len(zones))}
        
        for x, y in positions:
            for i, (x_min, y_min, x_max, y_max) in enumerate(zones):
                if x_min <= x <= x_max and y_min <= y <= y_max:
                    zone_counts[i] += 1
                    break  # Count each position in only one zone
        
        total_positions = len(positions)
        zone_occupancy = {
            i: (count / total_positions) * 100.0
            for i, count in zone_counts.items()
        }
        
        return zone_occupancy
    
    def generate_dynamic_heatmap(
        self,
        positions_with_time: List[Tuple[float, float, float]],
        time_window: float = 300.0,  # 5 minutes
        normalize: bool = True
    ) -> List[Tuple[float, Heatmap]]:
        """
        Generate time-windowed heatmaps showing evolution over time
        
        Args:
            positions_with_time: List of (x, y, timestamp) tuples
            time_window: Window size in seconds
            normalize: Whether to normalize intensities
            
        Returns:
            List of (window_start_time, heatmap) tuples
        """
        if len(positions_with_time) == 0:
            return []
        
        # Sort by timestamp
        sorted_positions = sorted(positions_with_time, key=lambda p: p[2])
        
        # Determine time range
        min_time = sorted_positions[0][2]
        max_time = sorted_positions[-1][2]
        
        heatmaps = []
        current_time = min_time
        
        while current_time <= max_time:
            window_end = current_time + time_window
            
            # Get positions in this window
            window_positions = [
                (x, y) for x, y, t in sorted_positions
                if current_time <= t < window_end
            ]
            
            if len(window_positions) > 0:
                heatmap = self.generate_heatmap(window_positions, normalize, apply_smoothing=True)
                if heatmap:
                    heatmaps.append((current_time, heatmap))
            
            current_time += time_window
        
        return heatmaps
    
    def _apply_gaussian_smoothing(self, grid: np.ndarray, sigma: float = 1.0) -> np.ndarray:
        """
        Apply Gaussian smoothing to grid using convolution
        
        Args:
            grid: 2D numpy array
            sigma: Standard deviation for Gaussian kernel
            
        Returns:
            Smoothed grid
        """
        # Create Gaussian kernel
        kernel_size = int(6 * sigma + 1)
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        kernel = self._gaussian_kernel_2d(kernel_size, sigma)
        
        # Apply convolution
        from scipy.ndimage import convolve
        smoothed = convolve(grid, kernel, mode='constant', cval=0.0)
        
        return smoothed
    
    def _gaussian_kernel_2d(self, size: int, sigma: float) -> np.ndarray:
        """
        Create 2D Gaussian kernel
        
        Args:
            size: Kernel size (should be odd)
            sigma: Standard deviation
            
        Returns:
            2D Gaussian kernel
        """
        center = size // 2
        kernel = np.zeros((size, size))
        
        for i in range(size):
            for j in range(size):
                x = i - center
                y = j - center
                kernel[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
        
        # Normalize
        kernel = kernel / np.sum(kernel)
        
        return kernel


class ZoneAnalyzer:
    """
    Analyzes player activity in predefined pitch zones
    """
    
    # Standard pitch zones (thirds)
    DEFENSIVE_THIRD = (0, 0, 35, 68)
    MIDDLE_THIRD = (35, 0, 70, 68)
    ATTACKING_THIRD = (70, 0, 105, 68)
    
    # Left/Center/Right channels
    LEFT_CHANNEL = (0, 0, 105, 22.67)
    CENTER_CHANNEL = (0, 22.67, 105, 45.33)
    RIGHT_CHANNEL = (0, 45.33, 105, 68)
    
    @classmethod
    def get_standard_zones(cls) -> Dict[str, Tuple[float, float, float, float]]:
        """Get standard pitch zones"""
        return {
            "defensive_third": cls.DEFENSIVE_THIRD,
            "middle_third": cls.MIDDLE_THIRD,
            "attacking_third": cls.ATTACKING_THIRD,
            "left_channel": cls.LEFT_CHANNEL,
            "center_channel": cls.CENTER_CHANNEL,
            "right_channel": cls.RIGHT_CHANNEL
        }
    
    @classmethod
    def analyze_zone_activity(
        cls,
        positions: List[Tuple[float, float]]
    ) -> Dict[str, float]:
        """
        Analyze player activity across standard zones
        
        Returns:
            Dict mapping zone name to occupancy percentage
        """
        zones = cls.get_standard_zones()
        engine = HeatmapEngine()
        
        zone_list = list(zones.values())
        occupancy = engine.generate_zone_occupancy(positions, zone_list)
        
        # Map back to zone names
        zone_names = list(zones.keys())
        return {zone_names[i]: occ for i, occ in occupancy.items()}
