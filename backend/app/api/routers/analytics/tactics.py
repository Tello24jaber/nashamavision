"""
Tactical Analysis API Routes - Phase 3
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.phase3_schemas import (
    MatchTacticsResponse,
    TeamTacticalSnapshotResponse,
    TeamTransitionsResponse,
    TacticalTimelineResponse,
    FormationTimelineItem
)
from app.analytics.tactical import TacticalAnalysisEngine
from app.analytics.models import TacticalSnapshot
from app.models.models import Match

router = APIRouter(prefix="/api/v1/tactics", tags=["Tactical Analysis"])


@router.get("/match/{match_id}", response_model=MatchTacticsResponse)
async def get_match_tactics(
    match_id: str,
    db: Session = Depends(get_db)
):
    """
    Get tactical analysis for a match
    
    Returns tactical snapshots for both teams including:
    - Formation detection
    - Team positioning
    - Defensive line analysis
    - Pressing intensity
    """
    # Check if match exists
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Try to get from database first
    snapshots = db.query(TacticalSnapshot).filter(
        TacticalSnapshot.match_id == match_id
    ).all()
    
    if not snapshots:
        # Compute on-the-fly
        engine = TacticalAnalysisEngine(db)
        tactical_data = engine.analyze_match_tactics(match_id)
        
        home_snapshots = [
            TeamTacticalSnapshotResponse(
                timestamp=s.timestamp,
                team_side=s.team_side,
                formation=s.formation,
                formation_confidence=s.formation_confidence,
                centroid_x=s.centroid_x,
                centroid_y=s.centroid_y,
                spread_x=s.spread_x,
                spread_y=s.spread_y,
                compactness=s.compactness,
                defensive_line_y=s.defensive_line_y,
                midfield_line_y=s.midfield_line_y,
                attacking_line_y=s.attacking_line_y,
                line_spacing_def_mid=s.line_spacing_def_mid,
                line_spacing_mid_att=s.line_spacing_mid_att,
                defensive_line_height=s.defensive_line_height,
                block_type=s.block_type,
                pressing_intensity=s.pressing_intensity,
                player_positions=s.player_positions
            )
            for s in tactical_data["home"]
        ]
        
        away_snapshots = [
            TeamTacticalSnapshotResponse(
                timestamp=s.timestamp,
                team_side=s.team_side,
                formation=s.formation,
                formation_confidence=s.formation_confidence,
                centroid_x=s.centroid_x,
                centroid_y=s.centroid_y,
                spread_x=s.spread_x,
                spread_y=s.spread_y,
                compactness=s.compactness,
                defensive_line_y=s.defensive_line_y,
                midfield_line_y=s.midfield_line_y,
                attacking_line_y=s.attacking_line_y,
                line_spacing_def_mid=s.line_spacing_def_mid,
                line_spacing_mid_att=s.line_spacing_mid_att,
                defensive_line_height=s.defensive_line_height,
                block_type=s.block_type,
                pressing_intensity=s.pressing_intensity,
                player_positions=s.player_positions
            )
            for s in tactical_data["away"]
        ]
        
        return MatchTacticsResponse(
            match_id=match_id,
            home_snapshots=home_snapshots,
            away_snapshots=away_snapshots
        )
    
    # Parse from database
    home_snaps = []
    away_snaps = []
    
    for snap in snapshots:
        response = TeamTacticalSnapshotResponse(
            timestamp=snap.timestamp,
            team_side=snap.team_side,
            formation=snap.formation or "Unknown",
            formation_confidence=snap.formation_confidence or 0.0,
            centroid_x=snap.centroid_x or 0.0,
            centroid_y=snap.centroid_y or 0.0,
            spread_x=snap.spread_x or 0.0,
            spread_y=snap.spread_y or 0.0,
            compactness=snap.compactness or 0.0,
            defensive_line_y=snap.defensive_line_y or 0.0,
            midfield_line_y=snap.midfield_line_y or 0.0,
            attacking_line_y=snap.attacking_line_y or 0.0,
            line_spacing_def_mid=snap.line_spacing_def_mid or 0.0,
            line_spacing_mid_att=snap.line_spacing_mid_att or 0.0,
            defensive_line_height=snap.defensive_line_height or 0.0,
            block_type=snap.block_type or "unknown",
            pressing_intensity=snap.pressing_intensity or 0.0,
            player_positions=snap.player_positions or []
        )
        
        if snap.team_side == "home":
            home_snaps.append(response)
        else:
            away_snaps.append(response)
    
    return MatchTacticsResponse(
        match_id=match_id,
        home_snapshots=home_snaps,
        away_snapshots=away_snaps
    )


@router.get("/match/{match_id}/timeline", response_model=TacticalTimelineResponse)
async def get_tactical_timeline(
    match_id: str,
    team_side: str,
    db: Session = Depends(get_db)
):
    """
    Get tactical timeline for a specific team
    
    Includes formation changes over time and key tactical metrics
    """
    snapshots = db.query(TacticalSnapshot).filter(
        TacticalSnapshot.match_id == match_id,
        TacticalSnapshot.team_side == team_side
    ).order_by(TacticalSnapshot.timestamp).all()
    
    if not snapshots:
        raise HTTPException(status_code=404, detail="No tactical data found")
    
    formation_timeline = [
        FormationTimelineItem(
            timestamp=snap.timestamp,
            formation=snap.formation or "Unknown",
            confidence=snap.formation_confidence or 0.0
        )
        for snap in snapshots
    ]
    
    # Compute averages
    avg_pressing = sum(s.pressing_intensity or 0.0 for s in snapshots) / len(snapshots)
    avg_compactness = sum(s.compactness or 0.0 for s in snapshots) / len(snapshots)
    avg_def_height = sum(s.defensive_line_height or 0.0 for s in snapshots) / len(snapshots)
    
    return TacticalTimelineResponse(
        match_id=match_id,
        team_side=team_side,
        formation_timeline=formation_timeline,
        avg_pressing_intensity=avg_pressing,
        avg_compactness=avg_compactness,
        avg_defensive_line_height=avg_def_height
    )


@router.get("/match/{match_id}/transitions/{team_side}", response_model=TeamTransitionsResponse)
async def get_team_transitions(
    match_id: str,
    team_side: str,
    db: Session = Depends(get_db)
):
    """
    Get transition events for a team (defense to attack, attack to defense)
    """
    engine = TacticalAnalysisEngine(db)
    
    try:
        transitions = engine.detect_transitions(match_id, team_side)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    from app.schemas.phase3_schemas import TransitionEventResponse
    
    transition_responses = [
        TransitionEventResponse(
            start_time=t.start_time,
            end_time=t.end_time,
            duration=t.duration,
            transition_type=t.transition_type,
            distance_covered=t.distance_covered,
            avg_speed=t.avg_speed
        )
        for t in transitions
    ]
    
    # Compute summary stats
    d2a = [t for t in transitions if t.transition_type == "defense_to_attack"]
    a2d = [t for t in transitions if t.transition_type == "attack_to_defense"]
    
    avg_d2a = sum(t.duration for t in d2a) / len(d2a) if d2a else None
    avg_a2d = sum(t.duration for t in a2d) / len(a2d) if a2d else None
    
    return TeamTransitionsResponse(
        match_id=match_id,
        team_side=team_side,
        transitions=transition_responses,
        avg_defense_to_attack_time=avg_d2a,
        avg_attack_to_defense_time=avg_a2d,
        num_transitions=len(transitions)
    )
