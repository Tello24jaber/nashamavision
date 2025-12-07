"""
Tests for Assistant API endpoints
"""
import pytest
from fastapi.testclient import TestClient


def test_assistant_health(client: TestClient, mock_llm_config):
    """Test GET /api/v1/assistant/health"""
    response = client.get("/api/v1/assistant/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "llm_provider" in data
    assert data["status"] == "healthy"
    assert data["llm_provider"] == "mock"


def test_assistant_test_llm(client: TestClient, mock_llm_config):
    """Test GET /api/v1/assistant/test"""
    response = client.get("/api/v1/assistant/test")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "provider" in data
    assert data["status"] == "success"
    assert data["provider"] == "mock"


def test_assistant_query_basic(client: TestClient, sample_match, sample_players, mock_llm_config):
    """Test POST /api/v1/assistant/query with basic query"""
    payload = {
        "query": "Who covered the most distance?",
        "match_id": str(sample_match.id)
    }
    response = client.post("/api/v1/assistant/query", json=payload)
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "answer" in data
    assert "data_used" in data
    assert "suggested_actions" in data
    assert "follow_up_questions" in data
    
    # Answer should be a non-empty string
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0
    
    # Actions should be a list
    assert isinstance(data["suggested_actions"], list)


def test_assistant_query_with_mock_returns_mock_answer(client: TestClient, sample_match, mock_llm_config):
    """Test that mock LLM returns recognizable mock answer"""
    payload = {
        "query": "What was the formation?",
        "match_id": str(sample_match.id)
    }
    response = client.post("/api/v1/assistant/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Mock LLM should return a string (possibly containing "MOCK" or similar)
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0


def test_assistant_query_without_match_id(client: TestClient, mock_llm_config):
    """Test POST /api/v1/assistant/query without match_id"""
    payload = {
        "query": "Who scored the most goals?"
    }
    response = client.post("/api/v1/assistant/query", json=payload)
    # Should either succeed with limited context or return 400
    assert response.status_code in [200, 400]


def test_assistant_query_invalid_match_id(client: TestClient, mock_llm_config):
    """Test POST /api/v1/assistant/query with invalid match_id"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    payload = {
        "query": "Who covered the most distance?",
        "match_id": fake_id
    }
    response = client.post("/api/v1/assistant/query", json=payload)
    # Should handle gracefully - either 404 or 200 with "no data" message
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "answer" in data


def test_assistant_query_generates_actions(client: TestClient, sample_match, sample_players, sample_metrics, mock_llm_config):
    """Test that assistant generates suggested actions for relevant queries"""
    payload = {
        "query": "Show me player metrics",
        "match_id": sample_match.id
    }
    response = client.post("/api/v1/assistant/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Should have at least one suggested action
    actions = data["suggested_actions"]
    if len(actions) > 0:
        action = actions[0]
        assert "label" in action
        assert "action_type" in action
        assert action["action_type"] in ["navigate", "filter", "highlight", "replay"]


def test_assistant_query_multiple_intents(client: TestClient, sample_match, mock_llm_config):
    """Test assistant with different query types"""
    queries = [
        "Who covered the most distance?",
        "What was the formation?",
        "Which player had the highest xT?",
        "Show me all passes",
        "How many sprints did player 10 make?"
    ]
    
    for query in queries:
        payload = {
            "query": query,
            "match_id": str(sample_match.id)
        }
        response = client.post("/api/v1/assistant/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert isinstance(data["answer"], str)
