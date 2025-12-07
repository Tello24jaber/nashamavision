"""
Pytest configuration and shared fixtures for Nashama Vision tests
"""
import pytest
import os
from typing import Generator, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import uuid

# Set testing environment variable before importing app
os.environ["TESTING"] = "1"

from app.main import app
from app.db.session import get_db, Base
from app.models.models import Match

# Import analytics models from Phase 2-3
try:
    from app.analytics.models import (
        PlayerMetric as PlayerMetrics,
        TeamMetric,
        HeatmapData,
        TacticalSnapshot,
        XTMetric as XTMetrics,
        Event
    )
except ImportError:
    # Fallback if models aren't available - use mock models
    class PlayerMetrics(Base):
        __tablename__ = "player_metrics"
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True, index=True)
        match_id = Column(Integer, nullable=False)
        player_id = Column(Integer, nullable=False)
        half = Column(Integer, nullable=False)

    class TeamMetric(Base):
        __tablename__ = "team_metrics"
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True, index=True)
        match_id = Column(Integer, nullable=False)
        
    class HeatmapData(Base):
        __tablename__ = "heatmap_data"
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True, index=True)
        match_id = Column(Integer, nullable=False)
        
    class TacticalSnapshot(Base):
        __tablename__ = "tactical_snapshots"
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True, index=True)
        match_id = Column(Integer, nullable=False)
        
    class XTMetrics(Base):
        __tablename__ = "xt_metrics"
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True, index=True)
        match_id = Column(Integer, nullable=False)
        
    class Event(Base):
        __tablename__ = "events"
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True, index=True)
        match_id = Column(Integer, nullable=False)

# For Player and PlayerTrack, we still need mocks since they're not in models.py
# Note: In SQLite, UUID columns are stored as strings
class Player(Base):
    __tablename__ = "players"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(36), ForeignKey("matches.id"), nullable=False)  # UUID as string in SQLite
    team = Column(String, nullable=False)
    jersey_number = Column(Integer, nullable=False)
    position = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class PlayerTrack(Base):
    __tablename__ = "player_tracks"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(36), ForeignKey("matches.id"), nullable=False)  # UUID as string in SQLite
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    frame_number = Column(Integer, nullable=False)
    t = Column(Float, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    vx = Column(Float, nullable=True)
    vy = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Test database setup (in-memory SQLite for speed)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """Create a fresh database engine for each test"""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Temporarily remove TeamColor table from metadata (uses PostgreSQL ARRAY type incompatible with SQLite)
    tables_to_create = [table for table in Base.metadata.sorted_tables if table.name != 'team_colors']
    for table in tables_to_create:
        table.create(bind=engine, checkfirst=True)
    
    yield engine
    
    # Cleanup
    for table in tables_to_create:
        table.drop(bind=engine, checkfirst=True)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a FastAPI test client with overridden database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ========================================
# Sample Data Fixtures
# ========================================

@pytest.fixture
def sample_match(db_session: Session) -> Match:
    """Create a sample match"""
    match = Match(
        name="Test Match",
        home_team="Team A",
        away_team="Team B",
        match_date=datetime.now(timezone.utc),
        venue="Test Stadium",
        competition="Test League",
        season="2024/25"
    )
    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)
    return match


@pytest.fixture
def sample_players(db_session: Session, sample_match: Match) -> list[Player]:
    """Create sample players for both teams"""
    players = []
    
    # Convert UUID to string for SQLite compatibility
    match_id_str = str(sample_match.id)
    
    # Home team (Team A) - 11 players
    for jersey_num in range(1, 12):
        player = Player(
            # Don't set ID - let SQLite autoincrement
            match_id=match_id_str,
            team="home",
            jersey_number=jersey_num,
            position="defender" if jersey_num <= 4 else "midfielder" if jersey_num <= 8 else "forward",
            created_at=datetime.now(timezone.utc)
        )
        players.append(player)
        db_session.add(player)
    
    # Away team (Team B) - 11 players
    for jersey_num in range(1, 12):
        player = Player(
            # Don't set ID - let SQLite autoincrement
            match_id=match_id_str,
            team="away",
            jersey_number=jersey_num,
            position="defender" if jersey_num <= 4 else "midfielder" if jersey_num <= 8 else "forward",
            created_at=datetime.now(timezone.utc)
        )
        players.append(player)
        db_session.add(player)
    
    db_session.commit()
    for player in players:
        db_session.refresh(player)
    return players


@pytest.fixture
def sample_tracks(db_session: Session, sample_match: Match, sample_players: list[Player]) -> list[PlayerTrack]:
    """Create sample tracking data - simple straight-line movement"""
    tracks = []
    
    # Create tracks for first player (jersey #1, home team)
    player = sample_players[0]
    
    # Convert UUID to string for SQLite compatibility
    match_id_str = str(sample_match.id)
    
    # 100 frames of movement from (10, 20) to (50, 60)
    for frame_idx in range(100):
        t = frame_idx / 30.0  # seconds
        x = 10.0 + (frame_idx * 0.4)  # moves 40m over 100 frames
        y = 20.0 + (frame_idx * 0.4)
        
        track = PlayerTrack(
            # Don't set ID - let SQLite autoincrement
            match_id=match_id_str,
            player_id=player.id,
            frame_number=frame_idx,
            t=t,
            x=x,
            y=y,
            vx=12.0,  # constant velocity (m/s)
            vy=12.0,
            speed=16.97,  # sqrt(12^2 + 12^2)
            created_at=datetime.now(timezone.utc)
        )
        tracks.append(track)
        db_session.add(track)
    
    db_session.commit()
    return tracks


@pytest.fixture
def sample_metrics(db_session: Session, sample_match: Match, sample_players: list[Player]) -> list[PlayerMetrics]:
    """Create sample player metrics"""
    metrics_list = []
    
    for i, player in enumerate(sample_players[:5]):  # First 5 players
        metrics = PlayerMetrics(
            id=str(uuid.uuid4()),
            match_id=sample_match.id,
            player_id=player.id,
            half=1,
            total_distance=5000.0 + (i * 500),  # 5km to 7km
            avg_speed=6.5 + (i * 0.5),
            max_speed=28.0 + i,
            sprints_count=15 + i,
            high_intensity_distance=800.0 + (i * 50),
            stamina_score=85.0 - (i * 5),
            workload_index=75.0 + (i * 3),
            created_at=datetime.now(timezone.utc)
        )
        metrics_list.append(metrics)
        db_session.add(metrics)
    
    db_session.commit()
    return metrics_list


@pytest.fixture
def sample_heatmap(db_session: Session, sample_match: Match, sample_players: list[Player]) -> HeatmapData:
    """Create sample heatmap data"""
    player = sample_players[0]
    
    # Simple heatmap - concentrated in one zone
    heatmap_bins = [[0] * 50 for _ in range(30)]  # 30x50 grid
    heatmap_bins[10][20] = 100  # Hot spot at (10, 20)
    heatmap_bins[11][20] = 80
    heatmap_bins[10][21] = 80
    
    heatmap = HeatmapData(
        id=str(uuid.uuid4()),
        match_id=sample_match.id,
        player_id=player.id,
        half=1,
        grid_resolution_x=50,
        grid_resolution_y=30,
        heatmap_bins=heatmap_bins,
        max_intensity=100,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(heatmap)
    db_session.commit()
    db_session.refresh(heatmap)
    return heatmap


@pytest.fixture
def sample_tactical_snapshot(db_session: Session, sample_match: Match) -> TacticalSnapshot:
    """Create sample tactical data"""
    snapshot = TacticalSnapshot(
        id=str(uuid.uuid4()),
        match_id=sample_match.id,
        half=1,
        t=600.0,  # 10 minutes
        home_formation="4-3-3",
        away_formation="4-4-2",
        home_formation_confidence=0.87,
        away_formation_confidence=0.82,
        home_compactness=22.5,
        away_compactness=25.3,
        home_defensive_line=35.0,
        away_defensive_line=70.0,
        home_pressing_intensity=0.65,
        away_pressing_intensity=0.52,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(snapshot)
    db_session.commit()
    db_session.refresh(snapshot)
    return snapshot


@pytest.fixture
def sample_xt_metrics(db_session: Session, sample_match: Match, sample_players: list[Player]) -> list[XTMetrics]:
    """Create sample xT metrics"""
    xt_metrics_list = []
    
    for i, player in enumerate(sample_players[:3]):
        metrics = XTMetrics(
            id=str(uuid.uuid4()),
            match_id=sample_match.id,
            player_id=player.id,
            half=1,
            total_xt_gain=0.5 + (i * 0.2),  # 0.5, 0.7, 0.9
            pass_xt=0.3 + (i * 0.1),
            carry_xt=0.15 + (i * 0.05),
            shot_xt=0.05 + (i * 0.05),
            actions_count=20 + (i * 5),
            avg_xt_per_action=0.025 + (i * 0.01),
            created_at=datetime.now(timezone.utc)
        )
        xt_metrics_list.append(metrics)
        db_session.add(metrics)
    
    db_session.commit()
    return xt_metrics_list


@pytest.fixture
def sample_events(db_session: Session, sample_match: Match, sample_players: list[Player]) -> list[Event]:
    """Create sample events"""
    events = []
    player = sample_players[0]
    
    # Pass event with xT gain
    pass_event = Event(
        id=str(uuid.uuid4()),
        match_id=sample_match.id,
        player_id=player.id,
        half=1,
        t=120.0,
        frame_number=3600,
        event_type="pass",
        x_start=30.0,
        y_start=40.0,
        x_end=60.0,
        y_end=50.0,
        xt_start=0.02,
        xt_end=0.08,
        xt_gain=0.06,
        success=True,
        created_at=datetime.now(timezone.utc)
    )
    events.append(pass_event)
    db_session.add(pass_event)
    
    # Carry event
    carry_event = Event(
        id=str(uuid.uuid4()),
        match_id=sample_match.id,
        player_id=player.id,
        half=1,
        t=125.0,
        frame_number=3750,
        event_type="carry",
        x_start=60.0,
        y_start=50.0,
        x_end=80.0,
        y_end=55.0,
        xt_start=0.08,
        xt_end=0.25,
        xt_gain=0.17,
        success=True,
        created_at=datetime.now(timezone.utc)
    )
    events.append(carry_event)
    db_session.add(carry_event)
    
    db_session.commit()
    return events


# ========================================
# Mock Configuration Fixtures
# ========================================

@pytest.fixture
def mock_llm_config(monkeypatch):
    """Set LLM provider to mock for testing"""
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "mock-model")
