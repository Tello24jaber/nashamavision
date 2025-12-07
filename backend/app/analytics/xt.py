"""
Expected Threat (xT) Analysis Engine for Nashama Vision Phase 3

This module implements Expected Threat calculations based on player movements
and actions on the pitch.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime

from sqlalchemy.orm import Session
from app.models.models import Track, TrackPoint, Match


@dataclass
class XTEvent:
    """Represents an xT-generating event"""
    event_id: str
    player_id: str
    match_id: str
    timestamp: float
    event_type: str  # "pass", "carry", "shot"
    
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    
    start_cell: Tuple[int, int]
    end_cell: Tuple[int, int]
    
    xt_start: float
    xt_end: float
    xt_gain: float
    
    metadata: Dict


@dataclass
class PlayerXTSummary:
    """Summary of xT contributions for a player"""
    player_id: str
    match_id: str
    
    total_xt_gain: float
    danger_score: float
    
    pass_xt: float
    carry_xt: float
    shot_xt: float
    
    num_passes: int
    num_carries: int
    num_shots: int
    
    avg_xt_per_action: float


class ExpectedThreatEngine:
    """
    Engine for computing Expected Threat (xT) values
    
    Based on the xT grid concept from:
    - Karun Singh's xT model
    - Friends of Tracking data
    """
    
    # Standard pitch dimensions
    PITCH_LENGTH = 105.0  # meters
    PITCH_WIDTH = 68.0    # meters
    
    # Grid dimensions (16x12 is standard)
    GRID_WIDTH = 16
    GRID_HEIGHT = 12
    
    # Baseline xT values (16x12 grid)
    # Higher values closer to goal
    # This is a simplified version - real values come from data analysis
    XT_GRID = np.array([
        [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
        [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
        [0.01, 0.01, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.01, 0.01],
        [0.02, 0.02, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.02, 0.02],
        [0.02, 0.03, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.03, 0.02],
        [0.03, 0.04, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.04, 0.03],
        [0.04, 0.05, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.05, 0.04],
        [0.05, 0.06, 0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.06, 0.05],
        [0.06, 0.07, 0.08, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09, 0.08, 0.07, 0.06],
        [0.07, 0.09, 0.10, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.10, 0.09, 0.07],
        [0.09, 0.11, 0.13, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.13, 0.11, 0.09],
        [0.11, 0.14, 0.16, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.16, 0.14, 0.11],
        [0.13, 0.17, 0.20, 0.22, 0.23, 0.23, 0.23, 0.23, 0.22, 0.20, 0.17, 0.13],
        [0.16, 0.21, 0.25, 0.28, 0.29, 0.30, 0.30, 0.29, 0.28, 0.25, 0.21, 0.16],
        [0.20, 0.26, 0.32, 0.36, 0.38, 0.40, 0.40, 0.38, 0.36, 0.32, 0.26, 0.20],
        [0.25, 0.32, 0.40, 0.48, 0.52, 0.56, 0.56, 0.52, 0.48, 0.40, 0.32, 0.25]
    ])
    
    def __init__(self, db: Session):
        self.db = db
        self.cell_width = self.PITCH_LENGTH / self.GRID_WIDTH
        self.cell_height = self.PITCH_WIDTH / self.GRID_HEIGHT
    
    def position_to_cell(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert pitch coordinates to grid cell
        
        Args:
            x, y: Coordinates in meters
            
        Returns:
            (col, row) cell indices
        """
        col = int(np.clip(x / self.cell_width, 0, self.GRID_WIDTH - 1))
        row = int(np.clip(y / self.cell_height, 0, self.GRID_HEIGHT - 1))
        return (col, row)
    
    def get_xt_value(self, x: float, y: float) -> float:
        """Get xT value for a position"""
        col, row = self.position_to_cell(x, y)
        return float(self.XT_GRID[col, row])
    
    def compute_xt_gain(
        self, 
        start_x: float, 
        start_y: float, 
        end_x: float, 
        end_y: float
    ) -> float:
        """
        Compute xT gain from moving ball from start to end position
        
        Args:
            start_x, start_y: Starting position
            end_x, end_y: Ending position
            
        Returns:
            xT gain (can be negative)
        """
        xt_start = self.get_xt_value(start_x, start_y)
        xt_end = self.get_xt_value(end_x, end_y)
        return xt_end - xt_start
    
    def analyze_player_xt(
        self,
        match_id: str,
        player_id: str
    ) -> Tuple[PlayerXTSummary, List[XTEvent]]:
        """
        Analyze xT contributions for a player
        
        Args:
            match_id: Match UUID
            player_id: Player (track) UUID
            
        Returns:
            Tuple of (PlayerXTSummary, List of XTEvents)
        """
        # Get track points
        track = self.db.query(Track).filter(Track.id == player_id).first()
        if not track:
            raise ValueError(f"Track {player_id} not found")
        
        points = self.db.query(TrackPoint).filter(
            TrackPoint.track_id == player_id,
            TrackPoint.x_m.isnot(None),
            TrackPoint.y_m.isnot(None)
        ).order_by(TrackPoint.timestamp).all()
        
        if len(points) < 2:
            return self._empty_summary(player_id, match_id), []
        
        # Detect events
        events = self._detect_events(points, player_id, match_id)
        
        # Compute summary
        summary = self._compute_summary(events, player_id, match_id)
        
        return summary, events
    
    def analyze_match_xt(self, match_id: str) -> Dict[str, any]:
        """
        Analyze xT for entire match
        
        Returns:
            Dict containing team summaries and all events
        """
        # Get all tracks
        tracks = self.db.query(Track).filter(
            Track.match_id == match_id,
            Track.team_side.isnot(None)
        ).all()
        
        home_events = []
        away_events = []
        home_summaries = []
        away_summaries = []
        
        for track in tracks:
            try:
                summary, events = self.analyze_player_xt(match_id, track.id)
                
                if track.team_side == "home":
                    home_events.extend(events)
                    home_summaries.append(summary)
                else:
                    away_events.extend(events)
                    away_summaries.append(summary)
            except Exception as e:
                print(f"Error analyzing track {track.id}: {e}")
                continue
        
        # Compute team totals
        home_total_xt = sum(s.total_xt_gain for s in home_summaries)
        away_total_xt = sum(s.total_xt_gain for s in away_summaries)
        
        return {
            "match_id": match_id,
            "home": {
                "total_xt": home_total_xt,
                "player_summaries": home_summaries,
                "events": sorted(home_events, key=lambda e: e.timestamp)
            },
            "away": {
                "total_xt": away_total_xt,
                "player_summaries": away_summaries,
                "events": sorted(away_events, key=lambda e: e.timestamp)
            }
        }
    
    def _detect_events(
        self,
        points: List[TrackPoint],
        player_id: str,
        match_id: str
    ) -> List[XTEvent]:
        """
        Detect pass, carry, and shot events from track points
        
        Simplified heuristics:
        - CARRY: Player moves with ball (continuous movement)
        - PASS: Ball changes position rapidly (velocity spike)
        - SHOT: Movement toward goal with high velocity
        """
        events = []
        
        i = 0
        while i < len(points) - 1:
            current = points[i]
            
            # Look ahead for next significant movement
            j = i + 1
            while j < len(points) and j < i + 10:  # Look ahead 10 frames max
                next_point = points[j]
                
                distance = np.sqrt(
                    (next_point.x_m - current.x_m) ** 2 + 
                    (next_point.y_m - current.y_m) ** 2
                )
                time_diff = next_point.timestamp - current.timestamp
                
                if time_diff > 0 and distance > 1.0:  # Meaningful movement
                    velocity = distance / time_diff
                    
                    # Detect event type
                    event_type = self._classify_event(
                        current.x_m, current.y_m,
                        next_point.x_m, next_point.y_m,
                        velocity, distance
                    )
                    
                    if event_type:
                        # Compute xT
                        xt_gain = self.compute_xt_gain(
                            current.x_m, current.y_m,
                            next_point.x_m, next_point.y_m
                        )
                        
                        start_cell = self.position_to_cell(current.x_m, current.y_m)
                        end_cell = self.position_to_cell(next_point.x_m, next_point.y_m)
                        
                        event = XTEvent(
                            event_id=f"{player_id}_{current.timestamp}",
                            player_id=player_id,
                            match_id=match_id,
                            timestamp=current.timestamp,
                            event_type=event_type,
                            start_x=current.x_m,
                            start_y=current.y_m,
                            end_x=next_point.x_m,
                            end_y=next_point.y_m,
                            start_cell=start_cell,
                            end_cell=end_cell,
                            xt_start=self.get_xt_value(current.x_m, current.y_m),
                            xt_end=self.get_xt_value(next_point.x_m, next_point.y_m),
                            xt_gain=xt_gain,
                            metadata={
                                "distance": distance,
                                "velocity": velocity,
                                "duration": time_diff
                            }
                        )
                        
                        events.append(event)
                        i = j  # Skip to end of event
                        break
                
                j += 1
            
            i += 1
        
        return events
    
    def _classify_event(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        velocity: float,
        distance: float
    ) -> Optional[str]:
        """
        Classify event type based on movement characteristics
        
        Returns:
            "pass", "carry", "shot", or None
        """
        # Direction toward goal
        goal_x = self.PITCH_LENGTH
        goal_y = self.PITCH_WIDTH / 2
        
        # Vector to goal from start
        to_goal_x = goal_x - start_x
        to_goal_y = goal_y - start_y
        
        # Movement vector
        move_x = end_x - start_x
        move_y = end_y - start_y
        
        # Dot product (cosine similarity)
        dot = to_goal_x * move_x + to_goal_y * move_y
        mag_goal = np.sqrt(to_goal_x**2 + to_goal_y**2)
        mag_move = np.sqrt(move_x**2 + move_y**2)
        
        if mag_move > 0 and mag_goal > 0:
            toward_goal = dot / (mag_goal * mag_move)
        else:
            toward_goal = 0
        
        # Classification rules
        if velocity > 15.0 and distance > 10.0:
            # High velocity, long distance = likely pass
            return "pass"
        elif velocity > 20.0 and toward_goal > 0.8 and start_x > 70:
            # Very high velocity toward goal in attacking third = shot
            return "shot"
        elif velocity > 3.0 and velocity < 12.0 and distance > 2.0:
            # Moderate velocity = carry
            return "carry"
        
        return None
    
    def _compute_summary(
        self,
        events: List[XTEvent],
        player_id: str,
        match_id: str
    ) -> PlayerXTSummary:
        """Compute summary statistics from events"""
        
        pass_events = [e for e in events if e.event_type == "pass"]
        carry_events = [e for e in events if e.event_type == "carry"]
        shot_events = [e for e in events if e.event_type == "shot"]
        
        pass_xt = sum(e.xt_gain for e in pass_events if e.xt_gain > 0)
        carry_xt = sum(e.xt_gain for e in carry_events if e.xt_gain > 0)
        shot_xt = sum(e.xt_gain for e in shot_events if e.xt_gain > 0)
        
        total_xt_gain = pass_xt + carry_xt + shot_xt
        
        # Danger score (only positive contributions)
        danger_score = total_xt_gain * 100  # Scale to 0-100
        
        num_actions = len(events)
        avg_xt = total_xt_gain / num_actions if num_actions > 0 else 0.0
        
        return PlayerXTSummary(
            player_id=player_id,
            match_id=match_id,
            total_xt_gain=total_xt_gain,
            danger_score=danger_score,
            pass_xt=pass_xt,
            carry_xt=carry_xt,
            shot_xt=shot_xt,
            num_passes=len(pass_events),
            num_carries=len(carry_events),
            num_shots=len(shot_events),
            avg_xt_per_action=avg_xt
        )
    
    def _empty_summary(self, player_id: str, match_id: str) -> PlayerXTSummary:
        """Return empty summary"""
        return PlayerXTSummary(
            player_id=player_id,
            match_id=match_id,
            total_xt_gain=0.0,
            danger_score=0.0,
            pass_xt=0.0,
            carry_xt=0.0,
            shot_xt=0.0,
            num_passes=0,
            num_carries=0,
            num_shots=0,
            avg_xt_per_action=0.0
        )
    
    def get_xt_grid_data(self) -> Dict:
        """
        Return xT grid data for visualization
        
        Returns:
            Dict with grid dimensions and values
        """
        return {
            "grid_width": self.GRID_WIDTH,
            "grid_height": self.GRID_HEIGHT,
            "cell_width": self.cell_width,
            "cell_height": self.cell_height,
            "pitch_length": self.PITCH_LENGTH,
            "pitch_width": self.PITCH_WIDTH,
            "values": self.XT_GRID.tolist()
        }


def compute_match_xt(db: Session, match_id: str) -> Dict:
    """
    Convenience function to compute xT for a match
    
    Args:
        db: Database session
        match_id: Match UUID
        
    Returns:
        Match xT analysis dict
    """
    engine = ExpectedThreatEngine(db)
    return engine.analyze_match_xt(match_id)
