"""
Tests for Matches API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_list_matches(client: TestClient, sample_match):
    """Test GET /api/v1/matches"""
    response = client.get("/api/v1/matches")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(sample_match.id)  # UUID serialized as string in JSON
    assert data[0]["home_team"] == "Team A"
    assert data[0]["away_team"] == "Team B"


def test_get_match_by_id(client: TestClient, sample_match):
    """Test GET /api/v1/matches/{match_id}"""
    response = client.get(f"/api/v1/matches/{sample_match.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_match.id)  # UUID serialized as string in JSON
    assert data["name"] == "Test Match"
    assert data["home_team"] == "Team A"
    assert data["away_team"] == "Team B"


def test_get_match_not_found(client: TestClient):
    """Test GET /api/v1/matches/{match_id} with non-existent ID"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/matches/{fake_id}")
    assert response.status_code == 404


def test_get_match_players(client: TestClient, sample_match, sample_players):
    """Test GET /api/v1/matches/{match_id}/players"""
    response = client.get(f"/api/v1/matches/{sample_match.id}/players")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 22  # 11 home + 11 away
    
    # Check home team players
    home_players = [p for p in data if p["team"] == "home"]
    assert len(home_players) == 11
    
    # Check away team players
    away_players = [p for p in data if p["team"] == "away"]
    assert len(away_players) == 11


def test_match_status_flow(client: TestClient, sample_match):
    """Test that match details are correctly returned"""
    response = client.get(f"/api/v1/matches/{sample_match.id}")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "created_at" in data
    assert "updated_at" in data
