"""
Team Classifier
Classifies players into teams based on jersey color using K-means clustering
"""
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.cluster import KMeans
import logging

logger = logging.getLogger(__name__)


class TeamClassifier:
    """
    Classifies players into teams based on jersey color
    Uses K-means clustering on torso region colors
    """
    
    def __init__(self, n_clusters: int = 3):
        """
        Initialize team classifier
        
        Args:
            n_clusters: Number of clusters for K-means (typically 3: team1, team2, referee)
        """
        self.n_clusters = n_clusters
        self.team_colors: Optional[Dict[str, np.ndarray]] = None
        self.is_trained = False
        
        logger.info(f"TeamClassifier initialized with {n_clusters} clusters")
    
    def extract_torso_region(
        self,
        frame: np.ndarray,
        bbox: List[int]
    ) -> Optional[np.ndarray]:
        """
        Extract torso region from player bounding box
        Torso is approximately the middle 40% of the bbox
        
        Args:
            frame: Full frame image
            bbox: Player bounding box [x1, y1, x2, y2]
            
        Returns:
            Torso region image or None if extraction fails
        """
        try:
            x1, y1, x2, y2 = bbox
            
            # Calculate torso region
            height = y2 - y1
            width = x2 - x1
            
            # Torso: middle 40% vertically, middle 60% horizontally
            torso_y1 = y1 + int(height * 0.2)
            torso_y2 = y1 + int(height * 0.6)
            torso_x1 = x1 + int(width * 0.2)
            torso_x2 = x2 - int(width * 0.2)
            
            # Ensure coordinates are within frame bounds
            torso_y1 = max(0, torso_y1)
            torso_y2 = min(frame.shape[0], torso_y2)
            torso_x1 = max(0, torso_x1)
            torso_x2 = min(frame.shape[1], torso_x2)
            
            # Extract region
            torso = frame[torso_y1:torso_y2, torso_x1:torso_x2]
            
            if torso.size == 0:
                return None
            
            return torso
            
        except Exception as e:
            logger.warning(f"Failed to extract torso region: {e}")
            return None
    
    def get_dominant_color(self, image: np.ndarray, n_colors: int = 1) -> np.ndarray:
        """
        Get dominant color(s) from image using K-means
        
        Args:
            image: Input image (BGR format)
            n_colors: Number of dominant colors to extract
            
        Returns:
            Array of dominant colors in HSV format
        """
        # Convert to HSV color space (more robust for color classification)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Reshape image to be a list of pixels
        pixels = hsv.reshape(-1, 3)
        
        # Remove very dark and very light pixels (shadows/highlights)
        mask = (pixels[:, 2] > 30) & (pixels[:, 2] < 225)
        filtered_pixels = pixels[mask]
        
        if len(filtered_pixels) < 10:
            # Fall back to all pixels if filtering removed too many
            filtered_pixels = pixels
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(filtered_pixels)
        
        # Return cluster centers (dominant colors)
        return kmeans.cluster_centers_
    
    def train_from_samples(
        self,
        frame: np.ndarray,
        player_bboxes: List[List[int]],
        labels: Optional[List[str]] = None
    ):
        """
        Train classifier using sample player detections
        
        Args:
            frame: Frame image
            player_bboxes: List of player bounding boxes
            labels: Optional manual labels for supervised training
        """
        # Extract colors from all players
        colors = []
        
        for bbox in player_bboxes:
            torso = self.extract_torso_region(frame, bbox)
            if torso is not None:
                dominant_color = self.get_dominant_color(torso, n_colors=1)
                colors.append(dominant_color[0])
        
        if len(colors) < self.n_clusters:
            logger.warning(
                f"Not enough samples ({len(colors)}) for {self.n_clusters} clusters"
            )
            return
        
        colors_array = np.array(colors)
        
        # Cluster colors to identify teams
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        kmeans.fit(colors_array)
        
        # Store team colors
        self.team_colors = {
            f"team_{i}": center
            for i, center in enumerate(kmeans.cluster_centers_)
        }
        
        self.is_trained = True
        
        logger.info(f"Team classifier trained with {len(colors)} samples")
        logger.info(f"Team colors (HSV): {self.team_colors}")
    
    def classify_player(
        self,
        frame: np.ndarray,
        bbox: List[int]
    ) -> Optional[str]:
        """
        Classify a player into a team
        
        Args:
            frame: Frame image
            bbox: Player bounding box
            
        Returns:
            Team label or None if classification fails
        """
        if not self.is_trained:
            logger.warning("Classifier not trained yet")
            return None
        
        # Extract torso region
        torso = self.extract_torso_region(frame, bbox)
        if torso is None:
            return None
        
        # Get dominant color
        player_color = self.get_dominant_color(torso, n_colors=1)[0]
        
        # Find closest team color
        min_distance = float('inf')
        best_team = None
        
        for team_name, team_color in self.team_colors.items():
            # Compute color distance in HSV space
            distance = self._color_distance_hsv(player_color, team_color)
            
            if distance < min_distance:
                min_distance = distance
                best_team = team_name
        
        return best_team
    
    def _color_distance_hsv(self, color1: np.ndarray, color2: np.ndarray) -> float:
        """
        Compute distance between two colors in HSV space
        
        Args:
            color1: Color in HSV format [H, S, V]
            color2: Color in HSV format [H, S, V]
            
        Returns:
            Distance value
        """
        # Hue is circular (0-179 in OpenCV)
        h_diff = min(abs(color1[0] - color2[0]), 180 - abs(color1[0] - color2[0]))
        s_diff = abs(color1[1] - color2[1])
        v_diff = abs(color1[2] - color2[2])
        
        # Weighted distance (Hue is most important)
        distance = np.sqrt((h_diff * 2) ** 2 + s_diff ** 2 + v_diff ** 2)
        
        return distance
    
    def __repr__(self):
        return f"TeamClassifier(clusters={self.n_clusters}, trained={self.is_trained})"
