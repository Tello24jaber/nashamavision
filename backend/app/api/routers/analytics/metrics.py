"""
Analytics API Routes
Endpoints for retrieving analytics metrics and visualizations
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
import logging

from app.db.session import get_db
from app.models.models import Video, Track, TrackPoint, Match, ObjectClass, ProcessingStatus
from app.analytics.models import (
    PlayerMetric, PlayerMetricTimeSeries, PlayerHeatmap,
    TeamMetric, MetricType, TimeSeriesMetricType
)
from app.schemas.analytics_schemas import (
    PlayerMetricResponse,
    PlayerMetricsSummary,
    PlayerTimeSeriesResponse,
    TimeSeriesDataPoint,
    HeatmapResponse,
    MatchAnalyticsSummary,
    TeamMetricResponse,
    PlayerListResponse,
    PlayerInMatch,
    ZoneAnalysisResponse,
    ZoneOccupancy
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


# ============= Match Analytics =============

@router.get("/matches/{match_id}", response_model=MatchAnalyticsSummary)
def get_match_analytics(
    match_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get analytics summary for an entire match
    """
    # Get match
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Get video
    video = db.query(Video).filter(
        Video.match_id == match_id,
        Video.status == 'completed'
    ).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="No processed video found for this match")
    
    # Get all player tracks
    tracks = db.query(Track).filter(
        Track.video_id == video.id,
        Track.object_class == 'player'
    ).all()
    
    if len(tracks) == 0:
        raise HTTPException(status_code=404, detail="No player tracks found")
    
    # Get team counts
    home_count = sum(1 for t in tracks if t.team_side and "home" in t.team_side.lower())
    away_count = sum(1 for t in tracks if t.team_side and "away" in t.team_side.lower())
    
    # Aggregate metrics
    track_ids = [t.id for t in tracks]
    
    total_distance_metrics = db.query(PlayerMetric).filter(
        PlayerMetric.player_id.in_(track_ids),
        PlayerMetric.metric_name == MetricType.TOTAL_DISTANCE
    ).all()
    
    top_speed_metrics = db.query(PlayerMetric).filter(
        PlayerMetric.player_id.in_(track_ids),
        PlayerMetric.metric_name == MetricType.TOP_SPEED
    ).all()
    
    sprint_metrics = db.query(PlayerMetric).filter(
        PlayerMetric.player_id.in_(track_ids),
        PlayerMetric.metric_name == MetricType.SPRINT_COUNT
    ).all()
    
    total_distance = sum(m.numeric_value for m in total_distance_metrics) / 1000.0  # km
    avg_speed = sum(m.numeric_value for m in top_speed_metrics) / len(top_speed_metrics) * 3.6 if top_speed_metrics else 0
    max_speed = max((m.numeric_value for m in top_speed_metrics), default=0) * 3.6
    total_sprints = sum(int(m.numeric_value) for m in sprint_metrics)
    
    # Find top performers
    top_distance_player = max(total_distance_metrics, key=lambda m: m.numeric_value) if total_distance_metrics else None
    top_speed_player = max(top_speed_metrics, key=lambda m: m.numeric_value) if top_speed_metrics else None
    
    return MatchAnalyticsSummary(
        match_id=match_id,
        match_name=match.name,
        video_id=video.id,
        total_players=len(tracks),
        home_players=home_count,
        away_players=away_count,
        total_distance_covered_km=total_distance,
        avg_speed_kmh=avg_speed,
        max_speed_kmh=max_speed,
        total_sprints=total_sprints,
        top_distance_player_id=top_distance_player.player_id if top_distance_player else None,
        top_speed_player_id=top_speed_player.player_id if top_speed_player else None
    )


@router.get("/matches/{match_id}/players", response_model=PlayerListResponse)
def get_match_players(
    match_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get list of all players in a match
    """
    # Get video
    video = db.query(Video).filter(
        Video.match_id == match_id,
        Video.status == 'completed'
    ).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="No processed video found for this match")
    
    # Get player tracks
    tracks = db.query(Track).filter(
        Track.video_id == video.id,
        Track.object_class == 'player'
    ).all()
    
    players = [
        PlayerInMatch(
            player_id=t.id,
            track_id=t.track_id,
            object_class=t.object_class if isinstance(t.object_class, str) else t.object_class.value,
            team_side=t.team_side if isinstance(t.team_side, str) else (t.team_side.value if t.team_side else None),
            player_number=t.player_number,
            player_name=t.player_name,
            first_frame=t.first_frame,
            last_frame=t.last_frame,
            total_detections=t.total_detections
        )
        for t in tracks
    ]
    
    return PlayerListResponse(
        match_id=match_id,
        video_id=video.id,
        players=players
    )


# ============= Player Metrics =============

@router.get("/players/{player_id}/metrics", response_model=PlayerMetricsSummary)
def get_player_metrics(
    player_id: UUID,
    match_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Get all metrics for a specific player
    """
    # Get track
    track = db.query(Track).filter(Track.id == player_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Get metrics
    query = db.query(PlayerMetric).filter(PlayerMetric.player_id == player_id)
    if match_id:
        query = query.filter(PlayerMetric.match_id == match_id)
    
    metrics = query.all()
    
    if len(metrics) == 0:
        raise HTTPException(status_code=404, detail="No metrics found for this player")
    
    # Build summary
    metric_dict = {m.metric_name: m.numeric_value for m in metrics}
    
    return PlayerMetricsSummary(
        player_id=player_id,
        track_id=track.track_id,
        object_class=track.object_class if isinstance(track.object_class, str) else track.object_class.value,
        team_side=track.team_side if isinstance(track.team_side, str) else (track.team_side.value if track.team_side else None),
        total_distance_km=metric_dict.get(MetricType.TOTAL_DISTANCE, 0) / 1000.0,
        avg_speed_kmh=metric_dict.get(MetricType.AVG_SPEED, 0) * 3.6,
        top_speed_kmh=metric_dict.get(MetricType.TOP_SPEED, 0) * 3.6,
        high_intensity_distance_m=metric_dict.get(MetricType.HIGH_INTENSITY_DISTANCE, 0),
        sprint_count=int(metric_dict.get(MetricType.SPRINT_COUNT, 0)),
        max_acceleration_mps2=metric_dict.get(MetricType.MAX_ACCELERATION, 0),
        max_deceleration_mps2=metric_dict.get(MetricType.MAX_DECELERATION, 0),
        stamina_index=metric_dict.get(MetricType.STAMINA_INDEX, 0)
    )


@router.get("/players/{player_id}/metrics/all", response_model=List[PlayerMetricResponse])
def get_player_metrics_detailed(
    player_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all detailed metrics for a player
    """
    metrics = db.query(PlayerMetric).filter(PlayerMetric.player_id == player_id).all()
    
    if len(metrics) == 0:
        raise HTTPException(status_code=404, detail="No metrics found")
    
    return metrics


@router.get("/players/{player_id}/timeseries/{metric_type}", response_model=PlayerTimeSeriesResponse)
def get_player_timeseries(
    player_id: UUID,
    metric_type: str,
    match_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Get time series data for a specific metric
    """
    # Validate metric type
    try:
        metric_enum = TimeSeriesMetricType(metric_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid metric type: {metric_type}")
    
    # Get time series data
    query = db.query(PlayerMetricTimeSeries).filter(
        PlayerMetricTimeSeries.player_id == player_id,
        PlayerMetricTimeSeries.metric_type == metric_enum
    ).order_by(PlayerMetricTimeSeries.timestamp)
    
    if match_id:
        query = query.filter(PlayerMetricTimeSeries.match_id == match_id)
    
    timeseries = query.all()
    
    if len(timeseries) == 0:
        raise HTTPException(status_code=404, detail="No time series data found")
    
    data_points = [
        TimeSeriesDataPoint(
            timestamp=ts.timestamp,
            value=ts.value,
            unit=ts.unit
        )
        for ts in timeseries
    ]
    
    return PlayerTimeSeriesResponse(
        player_id=player_id,
        match_id=timeseries[0].match_id,
        metric_type=metric_type,
        data_points=data_points
    )


# ============= Heatmaps =============

@router.get("/players/{player_id}/heatmap", response_model=HeatmapResponse)
def get_player_heatmap(
    player_id: UUID,
    match_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Get heatmap for a specific player
    """
    query = db.query(PlayerHeatmap).filter(PlayerHeatmap.player_id == player_id)
    
    if match_id:
        query = query.filter(PlayerHeatmap.match_id == match_id)
    
    heatmap = query.first()
    
    if not heatmap:
        raise HTTPException(status_code=404, detail="Heatmap not found")
    
    return heatmap


@router.get("/matches/{match_id}/heatmap/team/{team_side}", response_model=HeatmapResponse)
def get_team_heatmap(
    match_id: UUID,
    team_side: str,
    db: Session = Depends(get_db)
):
    """
    Get combined heatmap for an entire team
    """
    # Get video
    video = db.query(Video).filter(
        Video.match_id == match_id,
        Video.status == 'completed'
    ).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="No processed video found")
    
    # Get player tracks for this team
    tracks = db.query(Track).filter(
        Track.video_id == video.id,
        Track.object_class == 'player',
        Track.team_side == team_side
    ).all()
    
    if len(tracks) == 0:
        raise HTTPException(status_code=404, detail=f"No players found for team {team_side}")
    
    # Get all heatmaps and combine them
    track_ids = [t.id for t in tracks]
    heatmaps = db.query(PlayerHeatmap).filter(
        PlayerHeatmap.player_id.in_(track_ids),
        PlayerHeatmap.match_id == match_id
    ).all()
    
    if len(heatmaps) == 0:
        raise HTTPException(status_code=404, detail="No heatmaps found")
    
    # Combine heatmaps (simple addition)
    import numpy as np
    combined_data = np.zeros((heatmaps[0].grid_height, heatmaps[0].grid_width))
    
    for hm in heatmaps:
        combined_data += np.array(hm.heatmap_data)
    
    # Create response
    return HeatmapResponse(
        id=heatmaps[0].id,
        player_id=heatmaps[0].player_id,
        match_id=match_id,
        video_id=video.id,
        grid_width=heatmaps[0].grid_width,
        grid_height=heatmaps[0].grid_height,
        heatmap_data=combined_data.tolist(),
        pitch_length=heatmaps[0].pitch_length,
        pitch_width=heatmaps[0].pitch_width,
        total_positions=sum(hm.total_positions for hm in heatmaps),
        max_intensity=float(np.max(combined_data)),
        created_at=heatmaps[0].created_at
    )


# ============= Team Metrics =============

@router.get("/teams/{team_side}/metrics", response_model=List[TeamMetricResponse])
def get_team_metrics(
    team_side: str,
    match_id: UUID = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get team-level metrics
    """
    metrics = db.query(TeamMetric).filter(
        TeamMetric.match_id == match_id,
        TeamMetric.team_side == team_side
    ).all()
    
    if len(metrics) == 0:
        raise HTTPException(status_code=404, detail="No team metrics found")
    
    return metrics
