"""
Expected Threat (xT) API Routes - Phase 3
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.phase3_schemas import (
    MatchXTAnalysisResponse,
    TeamXTSummaryResponse,
    PlayerXTSummaryResponse,
    PlayerXTDetailResponse,
    XTEventResponse,
    MatchXTEventsResponse,
    XTGridResponse
)
from app.analytics.xt import ExpectedThreatEngine
from app.analytics.models import XTMetric, Event
from app.models.models import Match

router = APIRouter(prefix="/api/v1/xt", tags=["Expected Threat (xT)"])


@router.get("/match/{match_id}", response_model=MatchXTAnalysisResponse)
async def get_match_xt_analysis(
    match_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete xT analysis for a match
    
    Returns xT summaries for both teams and all players
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Try database first
    xt_metrics = db.query(XTMetric).filter(
        XTMetric.match_id == match_id
    ).all()
    
    if xt_metrics:
        # Parse from database
        home_metrics = [m for m in xt_metrics if m.team_side == "home"]
        away_metrics = [m for m in xt_metrics if m.team_side == "away"]
        
        home_summaries = [
            PlayerXTSummaryResponse(
                player_id=str(m.player_id),
                match_id=str(m.match_id),
                total_xt_gain=m.total_xt_gain,
                danger_score=m.danger_score,
                pass_xt=m.pass_xt,
                carry_xt=m.carry_xt,
                shot_xt=m.shot_xt,
                num_passes=m.num_passes,
                num_carries=m.num_carries,
                num_shots=m.num_shots,
                avg_xt_per_action=m.avg_xt_per_action
            )
            for m in home_metrics
        ]
        
        away_summaries = [
            PlayerXTSummaryResponse(
                player_id=str(m.player_id),
                match_id=str(m.match_id),
                total_xt_gain=m.total_xt_gain,
                danger_score=m.danger_score,
                pass_xt=m.pass_xt,
                carry_xt=m.carry_xt,
                shot_xt=m.shot_xt,
                num_passes=m.num_passes,
                num_carries=m.num_carries,
                num_shots=m.num_shots,
                avg_xt_per_action=m.avg_xt_per_action
            )
            for m in away_metrics
        ]
        
        home_total = sum(m.total_xt_gain for m in home_metrics)
        away_total = sum(m.total_xt_gain for m in away_metrics)
        
        return MatchXTAnalysisResponse(
            match_id=match_id,
            home=TeamXTSummaryResponse(
                team_side="home",
                total_xt=home_total,
                player_summaries=home_summaries
            ),
            away=TeamXTSummaryResponse(
                team_side="away",
                total_xt=away_total,
                player_summaries=away_summaries
            )
        )
    
    # Compute on-the-fly
    engine = ExpectedThreatEngine(db)
    analysis = engine.analyze_match_xt(match_id)
    
    home_summaries = [
        PlayerXTSummaryResponse(
            player_id=s.player_id,
            match_id=s.match_id,
            total_xt_gain=s.total_xt_gain,
            danger_score=s.danger_score,
            pass_xt=s.pass_xt,
            carry_xt=s.carry_xt,
            shot_xt=s.shot_xt,
            num_passes=s.num_passes,
            num_carries=s.num_carries,
            num_shots=s.num_shots,
            avg_xt_per_action=s.avg_xt_per_action
        )
        for s in analysis["home"]["player_summaries"]
    ]
    
    away_summaries = [
        PlayerXTSummaryResponse(
            player_id=s.player_id,
            match_id=s.match_id,
            total_xt_gain=s.total_xt_gain,
            danger_score=s.danger_score,
            pass_xt=s.pass_xt,
            carry_xt=s.carry_xt,
            shot_xt=s.shot_xt,
            num_passes=s.num_passes,
            num_carries=s.num_carries,
            num_shots=s.num_shots,
            avg_xt_per_action=s.avg_xt_per_action
        )
        for s in analysis["away"]["player_summaries"]
    ]
    
    return MatchXTAnalysisResponse(
        match_id=match_id,
        home=TeamXTSummaryResponse(
            team_side="home",
            total_xt=analysis["home"]["total_xt"],
            player_summaries=home_summaries
        ),
        away=TeamXTSummaryResponse(
            team_side="away",
            total_xt=analysis["away"]["total_xt"],
            player_summaries=away_summaries
        )
    )


@router.get("/player/{player_id}", response_model=PlayerXTDetailResponse)
async def get_player_xt_detail(
    player_id: str,
    match_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed xT analysis for a specific player
    
    Includes summary and all xT events
    """
    engine = ExpectedThreatEngine(db)
    
    try:
        summary, events = engine.analyze_player_xt(match_id, player_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    summary_response = PlayerXTSummaryResponse(
        player_id=summary.player_id,
        match_id=summary.match_id,
        total_xt_gain=summary.total_xt_gain,
        danger_score=summary.danger_score,
        pass_xt=summary.pass_xt,
        carry_xt=summary.carry_xt,
        shot_xt=summary.shot_xt,
        num_passes=summary.num_passes,
        num_carries=summary.num_carries,
        num_shots=summary.num_shots,
        avg_xt_per_action=summary.avg_xt_per_action
    )
    
    event_responses = [
        XTEventResponse(
            event_id=e.event_id,
            player_id=e.player_id,
            match_id=e.match_id,
            timestamp=e.timestamp,
            event_type=e.event_type,
            start_x=e.start_x,
            start_y=e.start_y,
            end_x=e.end_x,
            end_y=e.end_y,
            start_cell=e.start_cell,
            end_cell=e.end_cell,
            xt_start=e.xt_start,
            xt_end=e.xt_end,
            xt_gain=e.xt_gain,
            metadata=e.metadata
        )
        for e in events
    ]
    
    return PlayerXTDetailResponse(
        summary=summary_response,
        events=event_responses
    )


@router.get("/events/{match_id}", response_model=MatchXTEventsResponse)
async def get_match_xt_events(
    match_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all xT events for a match
    """
    engine = ExpectedThreatEngine(db)
    analysis = engine.analyze_match_xt(match_id)
    
    home_events = [
        XTEventResponse(
            event_id=e.event_id,
            player_id=e.player_id,
            match_id=e.match_id,
            timestamp=e.timestamp,
            event_type=e.event_type,
            start_x=e.start_x,
            start_y=e.start_y,
            end_x=e.end_x,
            end_y=e.end_y,
            start_cell=e.start_cell,
            end_cell=e.end_cell,
            xt_start=e.xt_start,
            xt_end=e.xt_end,
            xt_gain=e.xt_gain,
            metadata=e.metadata
        )
        for e in analysis["home"]["events"]
    ]
    
    away_events = [
        XTEventResponse(
            event_id=e.event_id,
            player_id=e.player_id,
            match_id=e.match_id,
            timestamp=e.timestamp,
            event_type=e.event_type,
            start_x=e.start_x,
            start_y=e.start_y,
            end_x=e.end_x,
            end_y=e.end_y,
            start_cell=e.start_cell,
            end_cell=e.end_cell,
            xt_start=e.xt_start,
            xt_end=e.xt_end,
            xt_gain=e.xt_gain,
            metadata=e.metadata
        )
        for e in analysis["away"]["events"]
    ]
    
    return MatchXTEventsResponse(
        match_id=match_id,
        home_events=home_events,
        away_events=away_events
    )


@router.get("/grid", response_model=XTGridResponse)
async def get_xt_grid(db: Session = Depends(get_db)):
    """
    Get the xT grid data for visualization
    
    Returns the baseline xT values for each grid cell
    """
    engine = ExpectedThreatEngine(db)
    grid_data = engine.get_xt_grid_data()
    
    return XTGridResponse(**grid_data)
