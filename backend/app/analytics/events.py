"""
Event Detection Engine for Nashama Vision Phase 3

Detects and classifies football events: passes, carries, shots
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import numpy as np

from sqlalchemy.orm import Session
from app.models.models import Track, TrackPoint


@dataclass
class FootballEvent:
    """Represents a detected football event"""
    id: str
    match_id: str
    player_id: str
    team_side: str
    
    event_type: str  # "pass", "carry", "shot", "dribble"
    timestamp: float
    frame_number: Optional[int]
    
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    
    distance: float
    duration: float
    velocity: float
    
    xt_value: Optional[float] = None
    
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class EventDetectionEngine:
    """
    Detects football events from tracking data
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_all_events(
        self,
        match_id: str
    ) -> List[FootballEvent]:
        """
        Detect all events for a match
        
        Args:
            match_id: Match UUID
            
        Returns:
            List of FootballEvent objects
        """
        tracks = self.db.query(Track).filter(
            Track.match_id == match_id,
            Track.team_side.isnot(None)
        ).all()
        
        all_events = []
        
        for track in tracks:
            player_events = self.detect_player_events(track.id, match_id)
            all_events.extend(player_events)
        
        # Sort by timestamp
        all_events.sort(key=lambda e: e.timestamp)
        
        return all_events
    
    def detect_player_events(
        self,
        player_id: str,
        match_id: str
    ) -> List[FootballEvent]:
        """
        Detect events for a single player
        
        Args:
            player_id: Track UUID
            match_id: Match UUID
            
        Returns:
            List of FootballEvent objects
        """
        track = self.db.query(Track).filter(Track.id == player_id).first()
        if not track:
            return []
        
        points = self.db.query(TrackPoint).filter(
            TrackPoint.track_id == player_id,
            TrackPoint.x_m.isnot(None),
            TrackPoint.y_m.isnot(None)
        ).order_by(TrackPoint.timestamp).all()
        
        if len(points) < 2:
            return []
        
        events = []
        
        # Pass detection
        pass_events = self._detect_passes(points, player_id, match_id, track.team_side)
        events.extend(pass_events)
        
        # Carry detection
        carry_events = self._detect_carries(points, player_id, match_id, track.team_side)
        events.extend(carry_events)
        
        # Shot detection
        shot_events = self._detect_shots(points, player_id, match_id, track.team_side)
        events.extend(shot_events)
        
        return events
    
    def _detect_passes(
        self,
        points: List[TrackPoint],
        player_id: str,
        match_id: str,
        team_side: str
    ) -> List[FootballEvent]:
        """
        Detect pass events
        
        Pass characteristics:
        - Rapid ball movement (high velocity)
        - Distance > 5m
        - Duration < 2 seconds
        """
        passes = []
        
        i = 0
        while i < len(points) - 1:
            current = points[i]
            
            # Look ahead for rapid movement
            for j in range(i + 1, min(i + 20, len(points))):
                next_point = points[j]
                
                distance = np.sqrt(
                    (next_point.x_m - current.x_m) ** 2 +
                    (next_point.y_m - current.y_m) ** 2
                )
                
                duration = next_point.timestamp - current.timestamp
                
                if duration > 0 and distance > 5.0 and duration < 2.0:
                    velocity = distance / duration
                    
                    if velocity > 12.0:  # High velocity threshold for pass
                        event = FootballEvent(
                            id=str(uuid.uuid4()),
                            match_id=match_id,
                            player_id=player_id,
                            team_side=team_side,
                            event_type="pass",
                            timestamp=current.timestamp,
                            frame_number=current.frame_number,
                            start_x=current.x_m,
                            start_y=current.y_m,
                            end_x=next_point.x_m,
                            end_y=next_point.y_m,
                            distance=distance,
                            duration=duration,
                            velocity=velocity,
                            metadata={
                                "pass_length": distance,
                                "pass_velocity": velocity
                            }
                        )
                        passes.append(event)
                        i = j
                        break
            
            i += 1
        
        return passes
    
    def _detect_carries(
        self,
        points: List[TrackPoint],
        player_id: str,
        match_id: str,
        team_side: str
    ) -> List[FootballEvent]:
        """
        Detect carry/dribble events
        
        Carry characteristics:
        - Continuous movement
        - Moderate velocity (3-10 m/s)
        - Distance > 3m
        """
        carries = []
        
        i = 0
        while i < len(points) - 1:
            # Accumulate continuous movement
            start_point = points[i]
            carry_distance = 0.0
            carry_duration = 0.0
            last_point = start_point
            
            j = i + 1
            while j < len(points):
                current_point = points[j]
                
                segment_dist = np.sqrt(
                    (current_point.x_m - last_point.x_m) ** 2 +
                    (current_point.y_m - last_point.y_m) ** 2
                )
                
                segment_time = current_point.timestamp - last_point.timestamp
                
                if segment_time > 0:
                    segment_velocity = segment_dist / segment_time
                    
                    # Continue carry if velocity is moderate
                    if 3.0 < segment_velocity < 12.0:
                        carry_distance += segment_dist
                        carry_duration += segment_time
                        last_point = current_point
                        j += 1
                    else:
                        break
                else:
                    j += 1
            
            # Create carry event if meaningful
            if carry_distance > 3.0 and carry_duration > 0:
                velocity = carry_distance / carry_duration
                
                event = FootballEvent(
                    id=str(uuid.uuid4()),
                    match_id=match_id,
                    player_id=player_id,
                    team_side=team_side,
                    event_type="carry",
                    timestamp=start_point.timestamp,
                    frame_number=start_point.frame_number,
                    start_x=start_point.x_m,
                    start_y=start_point.y_m,
                    end_x=last_point.x_m,
                    end_y=last_point.y_m,
                    distance=carry_distance,
                    duration=carry_duration,
                    velocity=velocity,
                    metadata={
                        "carry_distance": carry_distance,
                        "avg_velocity": velocity
                    }
                )
                carries.append(event)
                i = j
            else:
                i += 1
        
        return carries
    
    def _detect_shots(
        self,
        points: List[TrackPoint],
        player_id: str,
        match_id: str,
        team_side: str
    ) -> List[FootballEvent]:
        """
        Detect shot events
        
        Shot characteristics:
        - Very high velocity (> 20 m/s)
        - Movement toward goal
        - In attacking third (x > 70m)
        """
        shots = []
        
        PITCH_LENGTH = 105.0
        PITCH_WIDTH = 68.0
        ATTACKING_THIRD = PITCH_LENGTH * 2 / 3
        
        goal_x = PITCH_LENGTH
        goal_y = PITCH_WIDTH / 2
        
        i = 0
        while i < len(points) - 1:
            current = points[i]
            
            # Only consider if in attacking third
            if current.x_m > ATTACKING_THIRD:
                # Look for rapid movement toward goal
                for j in range(i + 1, min(i + 10, len(points))):
                    next_point = points[j]
                    
                    distance = np.sqrt(
                        (next_point.x_m - current.x_m) ** 2 +
                        (next_point.y_m - current.y_m) ** 2
                    )
                    
                    duration = next_point.timestamp - current.timestamp
                    
                    if duration > 0 and distance > 3.0:
                        velocity = distance / duration
                        
                        # Check if movement is toward goal
                        move_x = next_point.x_m - current.x_m
                        move_y = next_point.y_m - current.y_m
                        
                        to_goal_x = goal_x - current.x_m
                        to_goal_y = goal_y - current.y_m
                        
                        dot = move_x * to_goal_x + move_y * to_goal_y
                        mag_move = np.sqrt(move_x**2 + move_y**2)
                        mag_goal = np.sqrt(to_goal_x**2 + to_goal_y**2)
                        
                        if mag_move > 0 and mag_goal > 0:
                            toward_goal = dot / (mag_move * mag_goal)
                        else:
                            toward_goal = 0
                        
                        # High velocity toward goal = shot
                        if velocity > 18.0 and toward_goal > 0.7:
                            event = FootballEvent(
                                id=str(uuid.uuid4()),
                                match_id=match_id,
                                player_id=player_id,
                                team_side=team_side,
                                event_type="shot",
                                timestamp=current.timestamp,
                                frame_number=current.frame_number,
                                start_x=current.x_m,
                                start_y=current.y_m,
                                end_x=next_point.x_m,
                                end_y=next_point.y_m,
                                distance=distance,
                                duration=duration,
                                velocity=velocity,
                                metadata={
                                    "shot_velocity": velocity,
                                    "toward_goal_score": toward_goal,
                                    "distance_from_goal": mag_goal
                                }
                            )
                            shots.append(event)
                            i = j
                            break
            
            i += 1
        
        return shots
    
    def annotate_events_with_xt(
        self,
        events: List[FootballEvent],
        xt_engine
    ) -> List[FootballEvent]:
        """
        Add xT values to events
        
        Args:
            events: List of FootballEvent objects
            xt_engine: ExpectedThreatEngine instance
            
        Returns:
            Events with xt_value populated
        """
        for event in events:
            xt_gain = xt_engine.compute_xt_gain(
                event.start_x,
                event.start_y,
                event.end_x,
                event.end_y
            )
            event.xt_value = xt_gain
        
        return events


def detect_match_events(db: Session, match_id: str) -> List[FootballEvent]:
    """
    Convenience function to detect all events in a match
    
    Args:
        db: Database session
        match_id: Match UUID
        
    Returns:
        List of FootballEvent objects
    """
    engine = EventDetectionEngine(db)
    return engine.detect_all_events(match_id)
