"""
Tests for Replay API endpoints
"""
import pytest
from fastapi.testclient import TestClient


def test_get_replay_summary(client: TestClient, sample_match, sample_players):
    """Test GET /api/v1/replay/match/{match_id}/summary"""
    response = client.get(f"/api/v1/replay/match/{sample_match.id}/summary")
    assert response.status_code == 200
    data = response.json()
    
    assert "match" in data
    assert "players" in data
    assert data["match"]["id"] == sample_match.id
    assert isinstance(data["players"], list)
    assert len(data["players"]) == 22  # 11 home + 11 away


def test_get_replay_timeline(client: TestClient, sample_match, sample_tracks):
    """Test GET /api/v1/replay/match/{match_id}/timeline"""
    response = client.get(f"/api/v1/replay/match/{sample_match.id}/timeline")
    assert response.status_code == 200
    data = response.json()
    
    assert "frames" in data
    frames = data["frames"]
    assert isinstance(frames, list)
    
    if len(frames) > 0:
        # Check frame structure
        frame = frames[0]
        assert "t" in frame
        assert "players" in frame
        assert isinstance(frame["players"], list)
        
        # Frames should be ordered by time
        if len(frames) >= 2:
            assert frames[0]["t"] <= frames[1]["t"]


def test_get_replay_timeline_with_time_range(client: TestClient, sample_match, sample_tracks):
    """Test GET /api/v1/replay/match/{match_id}/timeline with start_t and end_t"""
    response = client.get(f"/api/v1/replay/match/{sample_match.id}/timeline?start_t=0&end_t=2")
    assert response.status_code == 200
    data = response.json()
    
    frames = data["frames"]
    # All frames should be within requested time range
    for frame in frames:
        assert 0 <= frame["t"] <= 2


def test_get_replay_pitch_dimensions(client: TestClient, sample_match):
    """Test GET /api/v1/replay/match/{match_id}/pitch"""
    response = client.get(f"/api/v1/replay/match/{sample_match.id}/pitch")
    # May return 200 or 404 depending on whether calibration data exists
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "width" in data or "length" in data


def test_replay_player_positions_within_bounds(client: TestClient, sample_match, sample_tracks):
    """Test that player positions in timeline are within pitch dimensions"""
    response = client.get(f"/api/v1/replay/match/{sample_match.id}/timeline")
    assert response.status_code == 200
    data = response.json()
    
    frames = data["frames"]
    if len(frames) > 0:
        for frame in frames:
            for player in frame["players"]:
                # Assuming standard pitch dimensions (105m x 68m)
                assert -10 <= player["x"] <= 115  # Allow some margin
                assert -10 <= player["y"] <= 78
