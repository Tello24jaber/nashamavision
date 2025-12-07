"""
Tests for Physical Metrics Engine
"""
import pytest
from sqlalchemy.orm import Session
from app.analytics.physical import PhysicalMetricsEngine, TrackPointData


def test_physical_metrics_engine_initialization():
    """Test that PhysicalMetricsEngine can be instantiated"""
    engine = PhysicalMetricsEngine()
    assert engine is not None
    assert engine.high_intensity_threshold > 0
    assert engine.sprint_threshold > 0


def test_compute_distance_from_straight_line_movement():
    """Test distance calculation from synthetic straight-line movement"""
    engine = PhysicalMetricsEngine()
    
    # Create synthetic track points (straight line movement)
    track_points = []
    for i in range(100):
        track_points.append(TrackPointData(
            timestamp=i * 0.033,  # 30 fps
            frame_number=i,
            x_m=float(i) * 0.4,  # Moving 0.4m per frame
            y_m=0.0,
            x_px=float(i) * 10,
            y_px=100.0
        ))
    
    metrics = engine.compute_metrics(track_points)
    
    # We created 100 frames with 0.4m movement per frame = ~40m total
    assert metrics is not None
    assert metrics.total_distance_m > 35.0  # At least 35m
    assert metrics.total_distance_m < 50.0  # Less than 50m


def test_compute_avg_speed():
    """Test average speed calculation"""
    engine = PhysicalMetricsEngine()
    
    track_points = []
    for i in range(100):
        track_points.append(TrackPointData(
            timestamp=i * 0.033,
            frame_number=i,
            x_m=float(i) * 0.4,
            y_m=0.0,
            x_px=float(i) * 10,
            y_px=100.0
        ))
    
    metrics = engine.compute_metrics(track_points)
    
    assert metrics is not None
    assert metrics.avg_speed_mps > 0
    assert metrics.avg_speed_mps < 30  # Reasonable upper bound


def test_compute_max_speed():
    """Test max speed detection"""
    engine = PhysicalMetricsEngine()
    
    track_points = []
    for i in range(100):
        track_points.append(TrackPointData(
            timestamp=i * 0.033,
            frame_number=i,
            x_m=float(i) * 0.4,
            y_m=0.0,
            x_px=float(i) * 10,
            y_px=100.0
        ))
    
    metrics = engine.compute_metrics(track_points)
    
    assert metrics is not None
    assert metrics.top_speed_mps >= metrics.avg_speed_mps
    assert metrics.top_speed_mps > 0


def test_stamina_curve_exists():
    """Test that stamina curve is generated"""
    engine = PhysicalMetricsEngine()
    
    track_points = []
    for i in range(100):
        track_points.append(TrackPointData(
            timestamp=i * 0.033,
            frame_number=i,
            x_m=float(i) * 0.4,
            y_m=0.0,
            x_px=float(i) * 10,
            y_px=100.0
        ))
    
    metrics = engine.compute_metrics(track_points)
    
    # Stamina should be between 0 and 100
    assert metrics is not None
    assert hasattr(metrics, 'stamina_index')
    assert 0 <= metrics.stamina_index <= 100


def test_insufficient_tracks_returns_none():
    """Test that insufficient track points return None"""
    engine = PhysicalMetricsEngine()
    
    # Only one track point (insufficient)
    track_points = [TrackPointData(
        timestamp=0.0,
        frame_number=0,
        x_m=0.0,
        y_m=0.0,
        x_px=0.0,
        y_px=0.0
    )]
    
    metrics = engine.compute_metrics(track_points)
    
    # Should return None for insufficient data
    assert metrics is None
