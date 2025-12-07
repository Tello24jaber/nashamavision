"""
Player Analytics API
Computes player metrics and heatmaps from tracking data
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from uuid import UUID
import numpy as np
import logging

from app.db.session import get_db
from app.models.models import Video, Track, TrackPoint, Match

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/player-analytics", tags=["Player Analytics"])


def compute_player_metrics(track_points: List[TrackPoint], fps: float = 30.0) -> Dict[str, Any]:
    """
    Compute physical metrics for a player from track points.
    Uses pixel coordinates and estimates real-world values.
    
    Assumes:
    - Standard football pitch visible in frame
    - 1920x1080 video resolution covering ~105m x 68m pitch
    - Approximate conversion: 1 pixel ≈ 0.055 meters (105m / 1920px)
    """
    if len(track_points) < 2:
        return None
    
    # Sort by frame number
    points = sorted(track_points, key=lambda p: p.frame_number)
    
    # Pixel to meter conversion (approximate)
    # Assuming 1920px width = 105m pitch length
    PIXELS_TO_METERS = 105.0 / 1920.0
    
    # Extract positions and timestamps
    positions = []
    timestamps = []
    
    for p in points:
        positions.append((float(p.x_px), float(p.y_px)))
        timestamps.append(float(p.timestamp))
    
    # Calculate distances between consecutive points
    distances_px = []
    speeds_mps = []
    
    for i in range(1, len(positions)):
        dx = positions[i][0] - positions[i-1][0]
        dy = positions[i][1] - positions[i-1][1]
        dist_px = np.sqrt(dx*dx + dy*dy)
        dist_m = dist_px * PIXELS_TO_METERS
        distances_px.append(dist_m)
        
        dt = timestamps[i] - timestamps[i-1]
        if dt > 0:
            speed = dist_m / dt
            # Cap unrealistic speeds (max ~12 m/s = 43 km/h)
            speed = min(speed, 12.0)
            speeds_mps.append(speed)
    
    if not speeds_mps:
        return None
    
    # Total distance
    total_distance_m = sum(distances_px)
    total_distance_km = total_distance_m / 1000.0
    
    # Speed metrics
    avg_speed_mps = np.mean(speeds_mps)
    top_speed_mps = max(speeds_mps)
    avg_speed_kmh = avg_speed_mps * 3.6
    top_speed_kmh = top_speed_mps * 3.6
    
    # High intensity and sprint detection
    HIGH_INTENSITY_THRESHOLD = 5.5  # m/s (~20 km/h)
    SPRINT_THRESHOLD = 7.0  # m/s (~25 km/h)
    
    high_intensity_distance = sum(
        d for d, s in zip(distances_px, speeds_mps) if s >= HIGH_INTENSITY_THRESHOLD
    )
    sprint_distance = sum(
        d for d, s in zip(distances_px, speeds_mps) if s >= SPRINT_THRESHOLD
    )
    
    # Count sprints (consecutive high-speed segments)
    sprint_count = 0
    in_sprint = False
    for s in speeds_mps:
        if s >= SPRINT_THRESHOLD:
            if not in_sprint:
                sprint_count += 1
                in_sprint = True
        else:
            in_sprint = False
    
    # Calculate acceleration
    accelerations = []
    for i in range(1, len(speeds_mps)):
        dt = timestamps[i+1] - timestamps[i] if i+1 < len(timestamps) else 0.1
        if dt > 0:
            accel = (speeds_mps[i] - speeds_mps[i-1]) / dt
            accelerations.append(accel)
    
    max_acceleration = max(accelerations) if accelerations else 0
    max_deceleration = min(accelerations) if accelerations else 0
    avg_acceleration = np.mean([abs(a) for a in accelerations]) if accelerations else 0
    
    # Stamina index (based on speed consistency over time)
    # Higher = more consistent performance
    if len(speeds_mps) > 10:
        first_half = speeds_mps[:len(speeds_mps)//2]
        second_half = speeds_mps[len(speeds_mps)//2:]
        first_avg = np.mean(first_half)
        second_avg = np.mean(second_half)
        stamina_index = min(100, (second_avg / first_avg * 100)) if first_avg > 0 else 100
    else:
        stamina_index = 100
    
    # Speed time series (sampled)
    speed_timeseries = []
    sample_interval = max(1, len(speeds_mps) // 50)  # ~50 data points
    for i in range(0, len(speeds_mps), sample_interval):
        speed_timeseries.append({
            'timestamp': timestamps[i+1] if i+1 < len(timestamps) else timestamps[-1],
            'value': speeds_mps[i]
        })
    
    return {
        'total_distance_m': round(total_distance_m, 2),
        'total_distance_km': round(total_distance_km, 3),
        'avg_speed_mps': round(avg_speed_mps, 2),
        'avg_speed_kmh': round(avg_speed_kmh, 2),
        'top_speed_mps': round(top_speed_mps, 2),
        'top_speed_kmh': round(top_speed_kmh, 2),
        'high_intensity_distance_m': round(high_intensity_distance, 2),
        'sprint_distance_m': round(sprint_distance, 2),
        'sprint_count': sprint_count,
        'max_acceleration_mps2': round(max_acceleration, 2),
        'max_deceleration_mps2': round(max_deceleration, 2),
        'avg_acceleration_mps2': round(avg_acceleration, 2),
        'stamina_index': round(stamina_index, 1),
        'speed_timeseries': speed_timeseries,
        'total_points': len(points),
        'duration_seconds': round(timestamps[-1] - timestamps[0], 2) if timestamps else 0
    }


def compute_player_heatmap(track_points: List[TrackPoint], grid_size: int = 20) -> Dict[str, Any]:
    """
    Generate a 2D heatmap from player positions.
    Uses pixel coordinates normalized to a grid.
    """
    if len(track_points) < 5:
        return None
    
    # Extract positions
    positions = [(float(p.x_px), float(p.y_px)) for p in track_points]
    
    # Find bounds
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    
    # Use video dimensions (assume 1920x1080 if not available)
    x_min, x_max = 0, 1920
    y_min, y_max = 0, 1080
    
    # Create grid
    grid_width = grid_size
    grid_height = int(grid_size * (y_max - y_min) / (x_max - x_min))
    
    heatmap = np.zeros((grid_height, grid_width))
    
    # Populate grid
    for x, y in positions:
        col = int((x - x_min) / (x_max - x_min) * (grid_width - 1))
        row = int((y - y_min) / (y_max - y_min) * (grid_height - 1))
        col = max(0, min(grid_width - 1, col))
        row = max(0, min(grid_height - 1, row))
        heatmap[row, col] += 1
    
    # Apply Gaussian smoothing
    from scipy.ndimage import gaussian_filter
    heatmap = gaussian_filter(heatmap, sigma=1.0)
    
    # Normalize to 0-1
    max_val = np.max(heatmap)
    if max_val > 0:
        heatmap = heatmap / max_val
    
    return {
        'data': heatmap.tolist(),
        'grid_width': grid_width,
        'grid_height': grid_height,
        'pitch_length': 105.0,
        'pitch_width': 68.0,
        'total_positions': len(positions),
        'max_intensity': float(max_val) if max_val > 0 else 1.0
    }


@router.get("/video/{video_id}/players")
def get_video_players_analytics(
    video_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get analytics summary for all players in a video
    """
    # Get video
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Get all player tracks
    tracks = db.query(Track).filter(
        Track.video_id == video_id
    ).all()
    
    if not tracks:
        raise HTTPException(status_code=404, detail="No tracks found for this video")
    
    # Get video FPS from processing info or default
    fps = 30.0
    
    players = []
    for track in tracks:
        # Get track points
        track_points = db.query(TrackPoint).filter(
            TrackPoint.track_id == track.id
        ).order_by(TrackPoint.frame_number).all()
        
        if len(track_points) < 2:
            continue
        
        # Compute metrics
        metrics = compute_player_metrics(track_points, fps)
        
        if metrics:
            players.append({
                'player_id': str(track.id),
                'track_id': track.track_id,
                'team_side': track.team_side,
                'first_frame': track.first_frame,
                'last_frame': track.last_frame,
                'total_detections': track.total_detections,
                'metrics': metrics
            })
    
    # Sort by track_id
    players.sort(key=lambda p: p['track_id'])
    
    # Calculate team totals
    total_distance = sum(p['metrics']['total_distance_km'] for p in players)
    avg_speed = np.mean([p['metrics']['avg_speed_kmh'] for p in players]) if players else 0
    max_speed = max([p['metrics']['top_speed_kmh'] for p in players]) if players else 0
    total_sprints = sum(p['metrics']['sprint_count'] for p in players)
    
    return {
        'video_id': str(video_id),
        'total_players': len(players),
        'summary': {
            'total_distance_km': round(total_distance, 2),
            'avg_team_speed_kmh': round(avg_speed, 2),
            'max_speed_kmh': round(max_speed, 2),
            'total_sprints': total_sprints
        },
        'players': players
    }


@router.get("/player/{track_id}/metrics")
def get_player_metrics(
    track_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get detailed metrics for a single player
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    track_points = db.query(TrackPoint).filter(
        TrackPoint.track_id == track_id
    ).order_by(TrackPoint.frame_number).all()
    
    if len(track_points) < 2:
        raise HTTPException(status_code=404, detail="Insufficient track points")
    
    metrics = compute_player_metrics(track_points)
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Could not compute metrics")
    
    return {
        'player_id': str(track_id),
        'track_id': track.track_id,
        'team_side': track.team_side,
        **metrics
    }


@router.get("/player/{track_id}/heatmap")
def get_player_heatmap(
    track_id: UUID,
    grid_size: int = 25,
    db: Session = Depends(get_db)
):
    """
    Get position heatmap for a single player
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    track_points = db.query(TrackPoint).filter(
        TrackPoint.track_id == track_id
    ).all()
    
    if len(track_points) < 5:
        raise HTTPException(status_code=404, detail="Insufficient track points for heatmap")
    
    heatmap = compute_player_heatmap(track_points, grid_size)
    
    if not heatmap:
        raise HTTPException(status_code=404, detail="Could not generate heatmap")
    
    return {
        'player_id': str(track_id),
        'track_id': track.track_id,
        'team_side': track.team_side,
        **heatmap
    }


@router.get("/video/{video_id}/heatmap")
def get_video_combined_heatmap(
    video_id: UUID,
    grid_size: int = 25,
    db: Session = Depends(get_db)
):
    """
    Get combined heatmap for all players in a video
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Get all tracks
    tracks = db.query(Track).filter(Track.video_id == video_id).all()
    
    if not tracks:
        raise HTTPException(status_code=404, detail="No tracks found")
    
    # Collect all positions
    all_positions = []
    for track in tracks:
        track_points = db.query(TrackPoint).filter(
            TrackPoint.track_id == track.id
        ).all()
        all_positions.extend(track_points)
    
    if len(all_positions) < 10:
        raise HTTPException(status_code=404, detail="Insufficient data for heatmap")
    
    heatmap = compute_player_heatmap(all_positions, grid_size)
    
    return {
        'video_id': str(video_id),
        'total_players': len(tracks),
        'total_positions': len(all_positions),
        **heatmap
    }


@router.get("/player/{track_id}/timeseries/{metric_type}")
def get_player_timeseries(
    track_id: UUID,
    metric_type: str,
    db: Session = Depends(get_db)
):
    """
    Get time series data for a specific metric (speed, position, etc.)
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    track_points = db.query(TrackPoint).filter(
        TrackPoint.track_id == track_id
    ).order_by(TrackPoint.frame_number).all()
    
    if len(track_points) < 2:
        raise HTTPException(status_code=404, detail="Insufficient track points")
    
    PIXELS_TO_METERS = 105.0 / 1920.0
    
    data_points = []
    
    if metric_type == 'speed':
        for i in range(1, len(track_points)):
            p1, p2 = track_points[i-1], track_points[i]
            dx = (float(p2.x_px) - float(p1.x_px)) * PIXELS_TO_METERS
            dy = (float(p2.y_px) - float(p1.y_px)) * PIXELS_TO_METERS
            dist = np.sqrt(dx*dx + dy*dy)
            dt = float(p2.timestamp) - float(p1.timestamp)
            speed = min(dist / dt, 12.0) if dt > 0 else 0
            data_points.append({
                'timestamp': float(p2.timestamp),
                'value': round(speed, 2)
            })
    
    elif metric_type == 'position_x':
        for p in track_points:
            data_points.append({
                'timestamp': float(p.timestamp),
                'value': float(p.x_px) * PIXELS_TO_METERS
            })
    
    elif metric_type == 'position_y':
        for p in track_points:
            data_points.append({
                'timestamp': float(p.timestamp),
                'value': float(p.y_px) * PIXELS_TO_METERS
            })
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown metric type: {metric_type}")
    
    # Sample to reduce data points
    if len(data_points) > 100:
        sample_interval = len(data_points) // 100
        data_points = data_points[::sample_interval]
    
    return {
        'player_id': str(track_id),
        'metric_type': metric_type,
        'data_points': data_points
    }
