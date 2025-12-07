"""
SQL Query Builder for AI Assistant

Generates SQLAlchemy queries based on parsed intent.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from app.models.models import Match, Video, TrackPoint

# Phase 2-3 models - import with fallback if not available
try:
    from app.models.models import (
        PlayerTrack, PlayerMetrics, TeamMetrics, HeatmapData,
        TacticalSnapshot, TransitionMetrics, XTMetrics, Event
    )
except ImportError:
    # Models not yet implemented - set to None for graceful degradation
    PlayerTrack = None
    PlayerMetrics = None
    TeamMetrics = None
    HeatmapData = None
    TacticalSnapshot = None
    TransitionMetrics = None
    XTMetrics = None
    Event = None


class QueryBuilder:
    """Build SQL queries for different question types"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================
    # PHYSICAL METRICS QUERIES
    # ========================================
    
    def get_top_distance_players(
        self,
        match_id: UUID,
        team_side: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get players ranked by total distance"""
        query = self.db.query(
            PlayerMetrics.player_id,
            PlayerTrack.jersey_number,
            PlayerTrack.team_side,
            PlayerMetrics.total_distance_m,
            PlayerMetrics.max_speed_ms,
            PlayerMetrics.sprint_count,
            PlayerMetrics.stamina_index
        ).join(
            PlayerTrack,
            PlayerMetrics.player_track_id == PlayerTrack.id
        ).filter(
            PlayerMetrics.match_id == match_id
        )
        
        if team_side:
            query = query.filter(PlayerTrack.team_side == team_side)
        
        results = query.order_by(desc(PlayerMetrics.total_distance_m)).limit(limit).all()
        
        return [
            {
                "player_id": str(r.player_id),
                "jersey": r.jersey_number,
                "team": r.team_side,
                "name": f"Player #{r.jersey_number}",
                "distance_km": r.total_distance_m / 1000.0,
                "max_speed": r.max_speed_ms * 3.6,  # m/s to km/h
                "sprint_count": r.sprint_count,
                "stamina_pct": r.stamina_index * 100 if r.stamina_index else 0
            }
            for r in results
        ]
    
    def get_top_speed_players(
        self,
        match_id: UUID,
        team_side: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get players ranked by max speed"""
        query = self.db.query(
            PlayerMetrics.player_id,
            PlayerTrack.jersey_number,
            PlayerTrack.team_side,
            PlayerMetrics.max_speed_ms,
            PlayerMetrics.avg_speed_ms,
            PlayerMetrics.sprint_count
        ).join(
            PlayerTrack,
            PlayerMetrics.player_track_id == PlayerTrack.id
        ).filter(
            PlayerMetrics.match_id == match_id
        )
        
        if team_side:
            query = query.filter(PlayerTrack.team_side == team_side)
        
        results = query.order_by(desc(PlayerMetrics.max_speed_ms)).limit(limit).all()
        
        return [
            {
                "player_id": str(r.player_id),
                "jersey": r.jersey_number,
                "team": r.team_side,
                "name": f"Player #{r.jersey_number}",
                "max_speed": r.max_speed_ms * 3.6,
                "avg_speed": r.avg_speed_ms * 3.6,
                "sprint_count": r.sprint_count
            }
            for r in results
        ]
    
    def get_workload_analysis(
        self,
        match_id: UUID,
        team_side: Optional[str] = None,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Get players with high workload (candidates for rest)"""
        query = self.db.query(
            PlayerMetrics.player_id,
            PlayerTrack.jersey_number,
            PlayerTrack.team_side,
            PlayerMetrics.total_distance_m,
            PlayerMetrics.sprint_count,
            PlayerMetrics.stamina_index,
            PlayerMetrics.high_intensity_distance_m
        ).join(
            PlayerTrack,
            PlayerMetrics.player_track_id == PlayerTrack.id
        ).filter(
            PlayerMetrics.match_id == match_id,
            PlayerMetrics.stamina_index < threshold
        )
        
        if team_side:
            query = query.filter(PlayerTrack.team_side == team_side)
        
        results = query.order_by(PlayerMetrics.stamina_index).all()
        
        return [
            {
                "player_id": str(r.player_id),
                "jersey": r.jersey_number,
                "team": r.team_side,
                "name": f"Player #{r.jersey_number}",
                "distance_km": r.total_distance_m / 1000.0,
                "sprint_count": r.sprint_count,
                "stamina_pct": r.stamina_index * 100 if r.stamina_index else 0,
                "high_intensity_km": r.high_intensity_distance_m / 1000.0 if r.high_intensity_distance_m else 0
            }
            for r in results
        ]
    
    def get_player_metrics(self, player_id: UUID, match_id: UUID) -> Optional[Dict[str, Any]]:
        """Get comprehensive metrics for a specific player"""
        result = self.db.query(
            PlayerMetrics,
            PlayerTrack.jersey_number,
            PlayerTrack.team_side
        ).join(
            PlayerTrack,
            PlayerMetrics.player_track_id == PlayerTrack.id
        ).filter(
            PlayerMetrics.player_id == player_id,
            PlayerMetrics.match_id == match_id
        ).first()
        
        if not result:
            return None
        
        metrics, jersey, team = result
        
        return {
            "player_id": str(player_id),
            "jersey": jersey,
            "team": team,
            "name": f"Player #{jersey}",
            "distance_km": metrics.total_distance_m / 1000.0,
            "max_speed": metrics.max_speed_ms * 3.6,
            "avg_speed": metrics.avg_speed_ms * 3.6,
            "sprint_count": metrics.sprint_count,
            "stamina_pct": metrics.stamina_index * 100 if metrics.stamina_index else 0,
            "high_intensity_km": metrics.high_intensity_distance_m / 1000.0 if metrics.high_intensity_distance_m else 0
        }
    
    # ========================================
    # xT METRICS QUERIES
    # ========================================
    
    def get_top_xt_players(
        self,
        match_id: UUID,
        team_side: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get players ranked by xT gain"""
        query = self.db.query(
            XTMetrics.player_id,
            PlayerTrack.jersey_number,
            PlayerTrack.team_side,
            XTMetrics.total_xt_gain,
            XTMetrics.danger_score,
            XTMetrics.pass_xt,
            XTMetrics.carry_xt,
            XTMetrics.shot_xt,
            XTMetrics.pass_count,
            XTMetrics.carry_count,
            XTMetrics.shot_count
        ).join(
            PlayerTrack,
            XTMetrics.player_track_id == PlayerTrack.id
        ).filter(
            XTMetrics.match_id == match_id
        )
        
        if team_side:
            query = query.filter(PlayerTrack.team_side == team_side)
        
        results = query.order_by(desc(XTMetrics.total_xt_gain)).limit(limit).all()
        
        return [
            {
                "player_id": str(r.player_id),
                "jersey": r.jersey_number,
                "team": r.team_side,
                "name": f"Player #{r.jersey_number}",
                "xt_gain": r.total_xt_gain,
                "danger_score": r.danger_score,
                "pass_xt": r.pass_xt,
                "carry_xt": r.carry_xt,
                "shot_xt": r.shot_xt,
                "pass_count": r.pass_count,
                "carry_count": r.carry_count,
                "shot_count": r.shot_count
            }
            for r in results
        ]
    
    def get_player_xt_metrics(self, player_id: UUID, match_id: UUID) -> Optional[Dict[str, Any]]:
        """Get xT metrics for a specific player"""
        result = self.db.query(
            XTMetrics,
            PlayerTrack.jersey_number,
            PlayerTrack.team_side
        ).join(
            PlayerTrack,
            XTMetrics.player_track_id == PlayerTrack.id
        ).filter(
            XTMetrics.player_id == player_id,
            XTMetrics.match_id == match_id
        ).first()
        
        if not result:
            return None
        
        xt, jersey, team = result
        
        return {
            "player_id": str(player_id),
            "jersey": jersey,
            "team": team,
            "name": f"Player #{jersey}",
            "xt_gain": xt.total_xt_gain,
            "danger_score": xt.danger_score,
            "pass_xt": xt.pass_xt,
            "carry_xt": xt.carry_xt,
            "shot_xt": xt.shot_xt,
            "pass_count": xt.pass_count,
            "carry_count": xt.carry_count,
            "shot_count": xt.shot_count
        }
    
    # ========================================
    # TACTICAL QUERIES
    # ========================================
    
    def get_latest_tactical_snapshot(
        self,
        match_id: UUID,
        team_side: str
    ) -> Optional[Dict[str, Any]]:
        """Get most recent tactical snapshot"""
        result = self.db.query(TacticalSnapshot).filter(
            TacticalSnapshot.match_id == match_id,
            TacticalSnapshot.team_side == team_side
        ).order_by(desc(TacticalSnapshot.timestamp_seconds)).first()
        
        if not result:
            return None
        
        return {
            "formation": result.formation,
            "formation_confidence": result.formation_confidence,
            "pressing_intensity": result.pressing_intensity,
            "team_compactness": result.team_compactness,
            "defensive_line_height": result.defensive_line_height,
            "block_type": result.block_type,
            "timestamp": result.timestamp_seconds
        }
    
    def get_pressing_timeline(
        self,
        match_id: UUID,
        team_side: str
    ) -> List[Dict[str, Any]]:
        """Get pressing intensity over time"""
        results = self.db.query(
            TacticalSnapshot.timestamp_seconds,
            TacticalSnapshot.pressing_intensity
        ).filter(
            TacticalSnapshot.match_id == match_id,
            TacticalSnapshot.team_side == team_side
        ).order_by(TacticalSnapshot.timestamp_seconds).all()
        
        return [
            {"time": r.timestamp_seconds, "intensity": r.pressing_intensity}
            for r in results
        ]
    
    def get_transitions(
        self,
        match_id: UUID,
        team_side: str,
        transition_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get transition events"""
        query = self.db.query(TransitionMetrics).filter(
            TransitionMetrics.match_id == match_id,
            TransitionMetrics.team_side == team_side
        )
        
        if transition_type:
            query = query.filter(TransitionMetrics.transition_type == transition_type)
        
        results = query.order_by(TransitionMetrics.start_time).all()
        
        return [
            {
                "type": r.transition_type,
                "start_time": r.start_time,
                "end_time": r.end_time,
                "duration": r.duration_seconds,
                "distance": r.distance_covered_m,
                "avg_speed": r.avg_speed_ms * 3.6,
                "players_involved": r.players_involved_count
            }
            for r in results
        ]
    
    # ========================================
    # EVENTS QUERIES
    # ========================================
    
    def get_events(
        self,
        match_id: UUID,
        event_type: Optional[str] = None,
        player_id: Optional[UUID] = None,
        team_side: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get events with filtering"""
        query = self.db.query(
            Event,
            PlayerTrack.jersey_number,
            PlayerTrack.team_side
        ).join(
            PlayerTrack,
            Event.player_track_id == PlayerTrack.id
        ).filter(
            Event.match_id == match_id
        )
        
        if event_type:
            query = query.filter(Event.event_type == event_type)
        
        if player_id:
            query = query.filter(Event.player_id == player_id)
        
        if team_side:
            query = query.filter(PlayerTrack.team_side == team_side)
        
        results = query.order_by(Event.timestamp_seconds).limit(limit).all()
        
        return [
            {
                "event_id": str(r.Event.id),
                "player_id": str(r.Event.player_id),
                "jersey": r.jersey_number,
                "team": r.team_side,
                "event_type": r.Event.event_type,
                "timestamp": r.Event.timestamp_seconds,
                "start_x": r.Event.start_x_m,
                "start_y": r.Event.start_y_m,
                "end_x": r.Event.end_x_m,
                "end_y": r.Event.end_y_m,
                "distance": r.Event.distance_m,
                "duration": r.Event.duration_seconds,
                "velocity": r.Event.velocity_ms,
                "xt_value": r.Event.xt_value
            }
            for r in results
        ]
    
    def get_top_events_by_xt(
        self,
        match_id: UUID,
        event_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get highest xT events"""
        query = self.db.query(
            Event,
            PlayerTrack.jersey_number,
            PlayerTrack.team_side
        ).join(
            PlayerTrack,
            Event.player_track_id == PlayerTrack.id
        ).filter(
            Event.match_id == match_id
        )
        
        if event_type:
            query = query.filter(Event.event_type == event_type)
        
        results = query.order_by(desc(Event.xt_value)).limit(limit).all()
        
        return [
            {
                "event_id": str(r.Event.id),
                "player_id": str(r.Event.player_id),
                "jersey": r.jersey_number,
                "team": r.team_side,
                "event_type": r.Event.event_type,
                "timestamp": r.Event.timestamp_seconds,
                "xt_value": r.Event.xt_value,
                "distance": r.Event.distance_m
            }
            for r in results
        ]
    
    # ========================================
    # MATCH INFO
    # ========================================
    
    def get_match_info(self, match_id: UUID) -> Optional[Dict[str, Any]]:
        """Get match metadata"""
        match = self.db.query(Match).filter(Match.id == match_id).first()
        
        if not match:
            return None
        
        video = self.db.query(Video).filter(Video.match_id == match_id).first()
        
        return {
            "match_id": str(match.id),
            "match_name": match.name,
            "home_team": match.home_team or "Home Team",
            "away_team": match.away_team or "Away Team",
            "date": match.match_date.isoformat() if match.match_date else "Unknown",
            "duration": video.duration if video else None,
            "status": video.status if video else "unknown"
        }
    
    # ========================================
    # TEAM COMPARISONS
    # ========================================
    
    def compare_teams(self, match_id: UUID) -> Dict[str, Any]:
        """Compare home vs away team metrics"""
        
        # Physical comparison
        home_metrics = self.db.query(
            func.sum(PlayerMetrics.total_distance_m).label("total_distance"),
            func.avg(PlayerMetrics.max_speed_ms).label("avg_max_speed"),
            func.sum(PlayerMetrics.sprint_count).label("total_sprints")
        ).join(
            PlayerTrack,
            PlayerMetrics.player_track_id == PlayerTrack.id
        ).filter(
            PlayerMetrics.match_id == match_id,
            PlayerTrack.team_side == "home"
        ).first()
        
        away_metrics = self.db.query(
            func.sum(PlayerMetrics.total_distance_m).label("total_distance"),
            func.avg(PlayerMetrics.max_speed_ms).label("avg_max_speed"),
            func.sum(PlayerMetrics.sprint_count).label("total_sprints")
        ).join(
            PlayerTrack,
            PlayerMetrics.player_track_id == PlayerTrack.id
        ).filter(
            PlayerMetrics.match_id == match_id,
            PlayerTrack.team_side == "away"
        ).first()
        
        # xT comparison
        home_xt = self.db.query(
            func.sum(XTMetrics.total_xt_gain).label("total_xt")
        ).join(
            PlayerTrack,
            XTMetrics.player_track_id == PlayerTrack.id
        ).filter(
            XTMetrics.match_id == match_id,
            PlayerTrack.team_side == "home"
        ).scalar() or 0.0
        
        away_xt = self.db.query(
            func.sum(XTMetrics.total_xt_gain).label("total_xt")
        ).join(
            PlayerTrack,
            XTMetrics.player_track_id == PlayerTrack.id
        ).filter(
            XTMetrics.match_id == match_id,
            PlayerTrack.team_side == "away"
        ).scalar() or 0.0
        
        return {
            "home": {
                "distance_km": home_metrics.total_distance / 1000.0 if home_metrics.total_distance else 0,
                "avg_max_speed": home_metrics.avg_max_speed * 3.6 if home_metrics.avg_max_speed else 0,
                "total_sprints": home_metrics.total_sprints or 0,
                "total_xt": home_xt
            },
            "away": {
                "distance_km": away_metrics.total_distance / 1000.0 if away_metrics.total_distance else 0,
                "avg_max_speed": away_metrics.avg_max_speed * 3.6 if away_metrics.avg_max_speed else 0,
                "total_sprints": away_metrics.total_sprints or 0,
                "total_xt": away_xt
            }
        }
