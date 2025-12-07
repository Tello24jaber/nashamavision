"""
Events API Routes - Phase 3
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.phase3_schemas import (
    MatchEventsResponse,
    PlayerEventsResponse,
    FootballEventResponse,
    TeamEventStatsResponse,
    EventTypeStatsResponse
)
from app.analytics.events import EventDetectionEngine
from app.analytics.models import Event, EventType as EventTypeEnum
from app.models.models import Match, Track

router = APIRouter(prefix="/api/v1/events", tags=["Event Detection"])


@router.get("/match/{match_id}", response_model=MatchEventsResponse)
async def get_match_events(
    match_id: str,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all events for a match
    
    Optionally filter by event_type: pass, carry, shot
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Try database first
    query = db.query(Event).filter(Event.match_id == match_id)
    
    if event_type:
        try:
            event_enum = EventTypeEnum[event_type.upper()]
            query = query.filter(Event.event_type == event_enum)
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")
    
    db_events = query.order_by(Event.timestamp).all()
    
    if db_events:
        # Return from database
        event_responses = [
            FootballEventResponse(
                id=str(e.id),
                match_id=str(e.match_id),
                player_id=str(e.player_id),
                team_side=e.team_side,
                event_type=e.event_type.value,
                timestamp=e.timestamp,
                frame_number=e.frame_number,
                start_x=e.start_x,
                start_y=e.start_y,
                end_x=e.end_x,
                end_y=e.end_y,
                distance=e.distance,
                duration=e.duration,
                velocity=e.velocity,
                xt_value=e.xt_value,
                metadata=e.metadata
            )
            for e in db_events
        ]
        
        num_passes = len([e for e in db_events if e.event_type == EventTypeEnum.PASS])
        num_carries = len([e for e in db_events if e.event_type == EventTypeEnum.CARRY])
        num_shots = len([e for e in db_events if e.event_type == EventTypeEnum.SHOT])
        
        return MatchEventsResponse(
            match_id=match_id,
            events=event_responses,
            num_passes=num_passes,
            num_carries=num_carries,
            num_shots=num_shots,
            total_events=len(db_events)
        )
    
    # Compute on-the-fly
    engine = EventDetectionEngine(db)
    events = engine.detect_all_events(match_id)
    
    if event_type:
        events = [e for e in events if e.event_type == event_type.lower()]
    
    event_responses = [
        FootballEventResponse(
            id=e.id,
            match_id=e.match_id,
            player_id=e.player_id,
            team_side=e.team_side,
            event_type=e.event_type,
            timestamp=e.timestamp,
            frame_number=e.frame_number,
            start_x=e.start_x,
            start_y=e.start_y,
            end_x=e.end_x,
            end_y=e.end_y,
            distance=e.distance,
            duration=e.duration,
            velocity=e.velocity,
            xt_value=e.xt_value,
            metadata=e.metadata
        )
        for e in events
    ]
    
    num_passes = len([e for e in events if e.event_type == "pass"])
    num_carries = len([e for e in events if e.event_type == "carry"])
    num_shots = len([e for e in events if e.event_type == "shot"])
    
    return MatchEventsResponse(
        match_id=match_id,
        events=event_responses,
        num_passes=num_passes,
        num_carries=num_carries,
        num_shots=num_shots,
        total_events=len(events)
    )


@router.get("/player/{player_id}", response_model=PlayerEventsResponse)
async def get_player_events(
    player_id: str,
    match_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all events for a specific player
    """
    track = db.query(Track).filter(Track.id == player_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Try database
    db_events = db.query(Event).filter(
        Event.player_id == player_id,
        Event.match_id == match_id
    ).order_by(Event.timestamp).all()
    
    if db_events:
        event_responses = [
            FootballEventResponse(
                id=str(e.id),
                match_id=str(e.match_id),
                player_id=str(e.player_id),
                team_side=e.team_side,
                event_type=e.event_type.value,
                timestamp=e.timestamp,
                frame_number=e.frame_number,
                start_x=e.start_x,
                start_y=e.start_y,
                end_x=e.end_x,
                end_y=e.end_y,
                distance=e.distance,
                duration=e.duration,
                velocity=e.velocity,
                xt_value=e.xt_value,
                metadata=e.metadata
            )
            for e in db_events
        ]
        
        num_passes = len([e for e in db_events if e.event_type == EventTypeEnum.PASS])
        num_carries = len([e for e in db_events if e.event_type == EventTypeEnum.CARRY])
        num_shots = len([e for e in db_events if e.event_type == EventTypeEnum.SHOT])
        total_xt = sum(e.xt_value for e in db_events if e.xt_value)
        
        return PlayerEventsResponse(
            player_id=player_id,
            match_id=match_id,
            team_side=track.team_side or "unknown",
            events=event_responses,
            num_passes=num_passes,
            num_carries=num_carries,
            num_shots=num_shots,
            total_xt_from_events=total_xt
        )
    
    # Compute on-the-fly
    engine = EventDetectionEngine(db)
    events = engine.detect_player_events(player_id, match_id)
    
    event_responses = [
        FootballEventResponse(
            id=e.id,
            match_id=e.match_id,
            player_id=e.player_id,
            team_side=e.team_side,
            event_type=e.event_type,
            timestamp=e.timestamp,
            frame_number=e.frame_number,
            start_x=e.start_x,
            start_y=e.start_y,
            end_x=e.end_x,
            end_y=e.end_y,
            distance=e.distance,
            duration=e.duration,
            velocity=e.velocity,
            xt_value=e.xt_value,
            metadata=e.metadata
        )
        for e in events
    ]
    
    num_passes = len([e for e in events if e.event_type == "pass"])
    num_carries = len([e for e in events if e.event_type == "carry"])
    num_shots = len([e for e in events if e.event_type == "shot"])
    total_xt = sum(e.xt_value for e in events if e.xt_value)
    
    return PlayerEventsResponse(
        player_id=player_id,
        match_id=match_id,
        team_side=track.team_side or "unknown",
        events=event_responses,
        num_passes=num_passes,
        num_carries=num_carries,
        num_shots=num_shots,
        total_xt_from_events=total_xt
    )


@router.get("/match/{match_id}/team/{team_side}/stats", response_model=TeamEventStatsResponse)
async def get_team_event_stats(
    match_id: str,
    team_side: str,
    db: Session = Depends(get_db)
):
    """
    Get event statistics for a team
    """
    events = db.query(Event).filter(
        Event.match_id == match_id,
        Event.team_side == team_side
    ).all()
    
    if not events:
        # Compute on-the-fly
        engine = EventDetectionEngine(db)
        all_events = engine.detect_all_events(match_id)
        events_data = [e for e in all_events if e.team_side == team_side]
        
        # Convert to Event-like objects for processing
        class EventData:
            def __init__(self, e):
                self.event_type = e.event_type
                self.distance = e.distance
                self.velocity = e.velocity
                self.xt_value = e.xt_value
        
        events = [EventData(e) for e in events_data]
    
    # Compute stats by type
    event_type_stats = {}
    
    for event in events:
        etype = event.event_type if isinstance(event.event_type, str) else event.event_type.value
        
        if etype not in event_type_stats:
            event_type_stats[etype] = {
                "count": 0,
                "distances": [],
                "velocities": [],
                "xt_gains": []
            }
        
        event_type_stats[etype]["count"] += 1
        event_type_stats[etype]["distances"].append(event.distance)
        event_type_stats[etype]["velocities"].append(event.velocity)
        if event.xt_value:
            event_type_stats[etype]["xt_gains"].append(event.xt_value)
    
    # Build response
    breakdown = []
    for etype, stats in event_type_stats.items():
        avg_dist = sum(stats["distances"]) / len(stats["distances"]) if stats["distances"] else 0.0
        avg_vel = sum(stats["velocities"]) / len(stats["velocities"]) if stats["velocities"] else 0.0
        avg_xt = sum(stats["xt_gains"]) / len(stats["xt_gains"]) if stats["xt_gains"] else None
        
        breakdown.append(EventTypeStatsResponse(
            event_type=etype,
            count=stats["count"],
            avg_distance=avg_dist,
            avg_velocity=avg_vel,
            avg_xt_gain=avg_xt
        ))
    
    total_passes = sum(1 for e in events if (e.event_type if isinstance(e.event_type, str) else e.event_type.value) == "pass")
    total_carries = sum(1 for e in events if (e.event_type if isinstance(e.event_type, str) else e.event_type.value) == "carry")
    total_shots = sum(1 for e in events if (e.event_type if isinstance(e.event_type, str) else e.event_type.value) == "shot")
    
    pass_distances = [e.distance for e in events if (e.event_type if isinstance(e.event_type, str) else e.event_type.value) == "pass"]
    carry_distances = [e.distance for e in events if (e.event_type if isinstance(e.event_type, str) else e.event_type.value) == "carry"]
    
    avg_pass_dist = sum(pass_distances) / len(pass_distances) if pass_distances else 0.0
    avg_carry_dist = sum(carry_distances) / len(carry_distances) if carry_distances else 0.0
    
    return TeamEventStatsResponse(
        team_side=team_side,
        match_id=match_id,
        total_events=len(events),
        event_type_breakdown=breakdown,
        total_passes=total_passes,
        total_carries=total_carries,
        total_shots=total_shots,
        avg_pass_distance=avg_pass_dist,
        avg_carry_distance=avg_carry_dist
    )
