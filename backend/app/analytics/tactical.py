"""
Tactical Analysis Engine for Nashama Vision Phase 3

This module provides comprehensive tactical analysis including:
- Formation detection
- Team shape and positioning
- Defensive line analysis
- Pressing intensity
- Transition speed
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import numpy as np
from scipy.spatial import ConvexHull
from scipy.cluster.vq import kmeans2
from collections import defaultdict

from sqlalchemy.orm import Session
from app.models.models import Track, TrackPoint, Match


@dataclass
class TeamTacticalSnapshot:
    """Represents tactical state at a moment in time"""
    timestamp: float
    team_side: str
    
    # Formation
    formation: str
    formation_confidence: float
    
    # Positioning
    centroid_x: float
    centroid_y: float
    spread_x: float
    spread_y: float
    compactness: float  # Convex hull area
    
    # Lines
    defensive_line_y: float
    midfield_line_y: float
    attacking_line_y: float
    line_spacing_def_mid: float
    line_spacing_mid_att: float
    
    # Defensive metrics
    defensive_line_height: float  # Distance from own goal
    block_type: str  # "low", "medium", "high"
    
    # Pressing
    pressing_intensity: float  # 0-100
    
    # Player positions (for debugging/visualization)
    player_positions: List[Tuple[float, float]]


@dataclass
class TransitionEvent:
    """Represents a transition from defense to attack or vice versa"""
    start_time: float
    end_time: float
    duration: float
    transition_type: str  # "defense_to_attack" or "attack_to_defense"
    distance_covered: float
    avg_speed: float


class TacticalAnalysisEngine:
    """
    Main engine for tactical analysis
    """
    
    # Standard formations (y-positions normalized 0-1, x-positions normalized 0-1)
    STANDARD_FORMATIONS = {
        "4-4-2": [
            # GK
            [(0.5, 0.05)],
            # Defense (4)
            [(0.2, 0.2), (0.4, 0.2), (0.6, 0.2), (0.8, 0.2)],
            # Midfield (4)
            [(0.2, 0.5), (0.4, 0.5), (0.6, 0.5), (0.8, 0.5)],
            # Attack (2)
            [(0.4, 0.8), (0.6, 0.8)]
        ],
        "4-3-3": [
            # GK
            [(0.5, 0.05)],
            # Defense (4)
            [(0.2, 0.2), (0.4, 0.2), (0.6, 0.2), (0.8, 0.2)],
            # Midfield (3)
            [(0.3, 0.5), (0.5, 0.5), (0.7, 0.5)],
            # Attack (3)
            [(0.3, 0.8), (0.5, 0.8), (0.7, 0.8)]
        ],
        "4-2-3-1": [
            # GK
            [(0.5, 0.05)],
            # Defense (4)
            [(0.2, 0.2), (0.4, 0.2), (0.6, 0.2), (0.8, 0.2)],
            # Defensive Mid (2)
            [(0.4, 0.4), (0.6, 0.4)],
            # Attacking Mid (3)
            [(0.3, 0.6), (0.5, 0.6), (0.7, 0.6)],
            # Striker (1)
            [(0.5, 0.85)]
        ],
        "3-5-2": [
            # GK
            [(0.5, 0.05)],
            # Defense (3)
            [(0.3, 0.2), (0.5, 0.2), (0.7, 0.2)],
            # Midfield (5)
            [(0.2, 0.5), (0.35, 0.5), (0.5, 0.5), (0.65, 0.5), (0.8, 0.5)],
            # Attack (2)
            [(0.4, 0.8), (0.6, 0.8)]
        ]
    }
    
    PITCH_LENGTH = 105.0  # meters
    PITCH_WIDTH = 68.0    # meters
    
    def __init__(self, db: Session):
        self.db = db
        
    def analyze_match_tactics(
        self, 
        match_id: str, 
        window_size: float = 60.0
    ) -> Dict[str, List[TeamTacticalSnapshot]]:
        """
        Compute tactical snapshots for both teams across the match
        
        Args:
            match_id: Match UUID
            window_size: Time window in seconds for averaging positions
            
        Returns:
            Dict with 'home' and 'away' keys, each containing list of snapshots
        """
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise ValueError(f"Match {match_id} not found")
        
        # Get all tracks for this match
        tracks = self.db.query(Track).filter(
            Track.match_id == match_id,
            Track.team_side.isnot(None)
        ).all()
        
        if not tracks:
            return {"home": [], "away": []}
        
        # Group by team
        home_tracks = [t for t in tracks if t.team_side == "home"]
        away_tracks = [t for t in tracks if t.team_side == "away"]
        
        # Get time range
        all_track_points = self.db.query(TrackPoint).join(Track).filter(
            Track.match_id == match_id
        ).all()
        
        if not all_track_points:
            return {"home": [], "away": []}
        
        min_time = min(tp.timestamp for tp in all_track_points)
        max_time = max(tp.timestamp for tp in all_track_points)
        
        # Generate snapshots
        home_snapshots = self._generate_snapshots(
            home_tracks, min_time, max_time, window_size, "home"
        )
        away_snapshots = self._generate_snapshots(
            away_tracks, min_time, max_time, window_size, "away"
        )
        
        return {
            "home": home_snapshots,
            "away": away_snapshots
        }
    
    def _generate_snapshots(
        self,
        tracks: List[Track],
        min_time: float,
        max_time: float,
        window_size: float,
        team_side: str
    ) -> List[TeamTacticalSnapshot]:
        """Generate tactical snapshots for a team"""
        snapshots = []
        
        # Create time windows
        current_time = min_time
        step = window_size / 2  # 50% overlap
        
        while current_time < max_time:
            window_end = current_time + window_size
            
            snapshot = self._compute_snapshot(
                tracks, current_time, window_end, team_side
            )
            
            if snapshot:
                snapshots.append(snapshot)
            
            current_time += step
        
        return snapshots
    
    def _compute_snapshot(
        self,
        tracks: List[Track],
        start_time: float,
        end_time: float,
        team_side: str
    ) -> Optional[TeamTacticalSnapshot]:
        """Compute a single tactical snapshot"""
        
        # Get average positions for each player in this window
        player_positions = []
        
        for track in tracks:
            points = self.db.query(TrackPoint).filter(
                TrackPoint.track_id == track.id,
                TrackPoint.timestamp >= start_time,
                TrackPoint.timestamp < end_time,
                TrackPoint.x_m.isnot(None),
                TrackPoint.y_m.isnot(None)
            ).all()
            
            if points:
                avg_x = np.mean([p.x_m for p in points])
                avg_y = np.mean([p.y_m for p in points])
                player_positions.append((avg_x, avg_y))
        
        if len(player_positions) < 3:
            return None
        
        positions_array = np.array(player_positions)
        
        # Compute formation
        formation, confidence = self._detect_formation(positions_array)
        
        # Compute centroid and spread
        centroid_x = np.mean(positions_array[:, 0])
        centroid_y = np.mean(positions_array[:, 1])
        spread_x = np.std(positions_array[:, 0])
        spread_y = np.std(positions_array[:, 1])
        
        # Compute compactness (convex hull area)
        compactness = self._compute_compactness(positions_array)
        
        # Compute defensive lines
        lines = self._compute_lines(positions_array)
        
        # Compute defensive line height
        defensive_line_height = self._compute_defensive_line_height(
            lines['defensive'], team_side
        )
        
        # Determine block type
        block_type = self._determine_block_type(defensive_line_height)
        
        # Compute pressing intensity (simplified - would need ball position)
        pressing_intensity = self._estimate_pressing_intensity(
            positions_array, centroid_y
        )
        
        return TeamTacticalSnapshot(
            timestamp=(start_time + end_time) / 2,
            team_side=team_side,
            formation=formation,
            formation_confidence=confidence,
            centroid_x=centroid_x,
            centroid_y=centroid_y,
            spread_x=spread_x,
            spread_y=spread_y,
            compactness=compactness,
            defensive_line_y=lines['defensive'],
            midfield_line_y=lines['midfield'],
            attacking_line_y=lines['attacking'],
            line_spacing_def_mid=abs(lines['midfield'] - lines['defensive']),
            line_spacing_mid_att=abs(lines['attacking'] - lines['midfield']),
            defensive_line_height=defensive_line_height,
            block_type=block_type,
            pressing_intensity=pressing_intensity,
            player_positions=player_positions
        )
    
    def _detect_formation(
        self, 
        positions: np.ndarray
    ) -> Tuple[str, float]:
        """
        Detect formation by comparing to standard formations
        
        Returns:
            Tuple of (formation_name, confidence_score)
        """
        # Normalize positions to 0-1 range
        x_norm = (positions[:, 0] - positions[:, 0].min()) / (positions[:, 0].max() - positions[:, 0].min() + 1e-6)
        y_norm = (positions[:, 1] - positions[:, 1].min()) / (positions[:, 1].max() - positions[:, 1].min() + 1e-6)
        normalized_positions = np.column_stack([x_norm, y_norm])
        
        best_formation = "4-4-2"
        best_score = float('inf')
        
        for formation_name, formation_template in self.STANDARD_FORMATIONS.items():
            # Flatten template
            template_positions = []
            for line in formation_template:
                template_positions.extend(line)
            
            template_array = np.array(template_positions)
            
            # Match number of players (take closest)
            if len(template_array) != len(normalized_positions):
                # Pad or truncate
                if len(template_array) > len(normalized_positions):
                    template_array = template_array[:len(normalized_positions)]
                else:
                    # Duplicate some positions
                    repeats = len(normalized_positions) - len(template_array)
                    template_array = np.vstack([
                        template_array,
                        template_array[:repeats]
                    ])
            
            # Compute distance (Hungarian algorithm would be better, but simplified here)
            # Sort both by y-coordinate
            template_sorted = template_array[template_array[:, 1].argsort()]
            positions_sorted = normalized_positions[normalized_positions[:, 1].argsort()]
            
            distance = np.sum(np.sqrt(np.sum((template_sorted - positions_sorted) ** 2, axis=1)))
            
            if distance < best_score:
                best_score = distance
                best_formation = formation_name
        
        # Convert distance to confidence (0-1)
        confidence = max(0.0, 1.0 - (best_score / len(normalized_positions)))
        
        return best_formation, confidence
    
    def _compute_compactness(self, positions: np.ndarray) -> float:
        """Compute team compactness using convex hull area"""
        if len(positions) < 3:
            return 0.0
        
        try:
            hull = ConvexHull(positions)
            return hull.volume  # In 2D, volume is area
        except:
            return 0.0
    
    def _compute_lines(self, positions: np.ndarray) -> Dict[str, float]:
        """Compute defensive, midfield, and attacking line positions"""
        y_positions = positions[:, 1]
        y_sorted = np.sort(y_positions)
        
        n = len(y_sorted)
        
        # Divide into thirds
        defensive_line = np.mean(y_sorted[:n//3]) if n >= 3 else y_sorted[0]
        midfield_line = np.mean(y_sorted[n//3:2*n//3]) if n >= 3 else np.mean(y_sorted)
        attacking_line = np.mean(y_sorted[2*n//3:]) if n >= 3 else y_sorted[-1]
        
        return {
            'defensive': defensive_line,
            'midfield': midfield_line,
            'attacking': attacking_line
        }
    
    def _compute_defensive_line_height(
        self, 
        defensive_line_y: float, 
        team_side: str
    ) -> float:
        """
        Compute distance of defensive line from own goal
        
        Args:
            defensive_line_y: Y-coordinate of defensive line
            team_side: 'home' or 'away'
            
        Returns:
            Distance in meters from own goal
        """
        if team_side == "home":
            # Home defends at y=0
            return defensive_line_y
        else:
            # Away defends at y=PITCH_LENGTH
            return self.PITCH_LENGTH - defensive_line_y
    
    def _determine_block_type(self, defensive_line_height: float) -> str:
        """Determine if team is playing low/medium/high block"""
        if defensive_line_height < self.PITCH_LENGTH * 0.25:
            return "low"
        elif defensive_line_height < self.PITCH_LENGTH * 0.5:
            return "medium"
        else:
            return "high"
    
    def _estimate_pressing_intensity(
        self, 
        positions: np.ndarray, 
        centroid_y: float
    ) -> float:
        """
        Estimate pressing intensity (0-100)
        
        Simplified version - in reality would need ball position and player velocities
        """
        # Use team centroid position as proxy
        # Higher centroid = more pressing
        pressing_score = (centroid_y / self.PITCH_LENGTH) * 100
        return min(100.0, max(0.0, pressing_score))
    
    def detect_transitions(
        self,
        match_id: str,
        team_side: str
    ) -> List[TransitionEvent]:
        """
        Detect transition events (defense to attack and vice versa)
        
        Args:
            match_id: Match UUID
            team_side: 'home' or 'away'
            
        Returns:
            List of TransitionEvent objects
        """
        snapshots = self.analyze_match_tactics(match_id)[team_side]
        
        if len(snapshots) < 2:
            return []
        
        transitions = []
        
        # Thresholds
        ATTACKING_THIRD_START = self.PITCH_LENGTH * 2 / 3
        DEFENSIVE_THIRD_END = self.PITCH_LENGTH / 3
        
        for i in range(len(snapshots) - 1):
            current = snapshots[i]
            next_snap = snapshots[i + 1]
            
            # Check for defense to attack transition
            if (current.centroid_y < DEFENSIVE_THIRD_END and 
                next_snap.centroid_y > ATTACKING_THIRD_START):
                
                duration = next_snap.timestamp - current.timestamp
                distance = abs(next_snap.centroid_y - current.centroid_y)
                avg_speed = distance / duration if duration > 0 else 0
                
                transitions.append(TransitionEvent(
                    start_time=current.timestamp,
                    end_time=next_snap.timestamp,
                    duration=duration,
                    transition_type="defense_to_attack",
                    distance_covered=distance,
                    avg_speed=avg_speed
                ))
            
            # Check for attack to defense transition
            elif (current.centroid_y > ATTACKING_THIRD_START and 
                  next_snap.centroid_y < DEFENSIVE_THIRD_END):
                
                duration = next_snap.timestamp - current.timestamp
                distance = abs(current.centroid_y - next_snap.centroid_y)
                avg_speed = distance / duration if duration > 0 else 0
                
                transitions.append(TransitionEvent(
                    start_time=current.timestamp,
                    end_time=next_snap.timestamp,
                    duration=duration,
                    transition_type="attack_to_defense",
                    distance_covered=distance,
                    avg_speed=avg_speed
                ))
        
        return transitions


def compute_tactical_snapshots(db: Session, match_id: str) -> Dict[str, List[TeamTacticalSnapshot]]:
    """
    Convenience function to compute tactical snapshots
    
    Args:
        db: Database session
        match_id: Match UUID
        
    Returns:
        Dict with 'home' and 'away' snapshots
    """
    engine = TacticalAnalysisEngine(db)
    return engine.analyze_match_tactics(match_id)
