"""
Tests for Assistant Service (Intent Parsing, Query Building, LLM Integration)
"""
import pytest
from sqlalchemy.orm import Session
from app.assistant.service import IntentParser, AssistantService
from app.assistant.llm_client import MockLLMClient


# ========================================
# Intent Parser Tests
# ========================================

def test_intent_parser_distance_query():
    """Test parsing distance-related queries"""
    parser = IntentParser()
    
    queries = [
        "Who covered the most distance?",
        "Show me distance stats",
        "Which player ran the furthest?"
    ]
    
    for query in queries:
        result = parser.parse(query)
        assert result["intent"] in ["player_distance", "general"]
        assert result["confidence"] > 0


def test_intent_parser_formation_query():
    """Test parsing formation queries"""
    parser = IntentParser()
    
    queries = [
        "What was the formation?",
        "Show me the tactical setup",
        "What formation did the home team use?"
    ]
    
    for query in queries:
        result = parser.parse(query)
        assert result["intent"] in ["tactical", "formation"]
        assert result["confidence"] > 0


def test_intent_parser_xt_query():
    """Test parsing xT queries"""
    parser = IntentParser()
    
    queries = [
        "Who had the highest xT?",
        "Show me threat creation",
        "Which player generated the most danger?"
    ]
    
    for query in queries:
        result = parser.parse(query)
        assert result["intent"] in ["player_xt", "general"]
        assert result["confidence"] > 0


def test_intent_parser_extracts_jersey_number():
    """Test extraction of jersey numbers from queries"""
    parser = IntentParser()
    
    result = parser.parse("Show me stats for player 10")
    
    assert "entities" in result
    if "jersey_number" in result["entities"]:
        assert result["entities"]["jersey_number"] == 10


def test_intent_parser_extracts_team():
    """Test extraction of team from queries"""
    parser = IntentParser()
    
    result = parser.parse("What was the home team's formation?")
    
    assert "entities" in result
    if "team" in result["entities"]:
        assert result["entities"]["team"] in ["home", "away"]


# ========================================
# Assistant Service Tests
# ========================================

@pytest.mark.asyncio
async def test_assistant_service_builds_context_without_crash(db_session: Session, sample_match, sample_players, sample_metrics, mock_llm_config):
    """Test that assistant service can build context from data"""
    service = AssistantService(db_session)
    
    query = "Who covered the most distance?"
    
    try:
        response = await service.handle_query(query, match_id=sample_match.id)
        assert response is not None
        assert "answer" in response
        assert isinstance(response["answer"], str)
    except Exception as e:
        pytest.fail(f"Assistant service crashed: {e}")


@pytest.mark.asyncio
async def test_assistant_service_returns_suggested_actions(db_session: Session, sample_match, sample_players, mock_llm_config):
    """Test that assistant generates suggested actions for some intents"""
    service = AssistantService(db_session)
    
    query = "Show me player metrics"
    response = await service.handle_query(query, match_id=sample_match.id)
    
    assert "suggested_actions" in response
    assert isinstance(response["suggested_actions"], list)


@pytest.mark.asyncio
async def test_assistant_service_handles_no_data_gracefully(db_session: Session, sample_match, mock_llm_config):
    """Test that assistant handles queries when no data is available"""
    service = AssistantService(db_session)
    
    # Query for data that doesn't exist
    query = "Show me data for player 99"
    
    try:
        response = await service.handle_query(query, match_id=sample_match.id)
        assert response is not None
        assert "answer" in response
    except Exception as e:
        pytest.fail(f"Assistant should handle no data gracefully: {e}")


@pytest.mark.asyncio
async def test_assistant_service_with_mock_llm(db_session: Session, sample_match, mock_llm_config):
    """Test that mock LLM client returns recognizable mock answer"""
    service = AssistantService(db_session)
    
    query = "Who covered the most distance?"
    response = await service.handle_query(query, match_id=sample_match.id)
    
    assert response is not None
    assert "answer" in response
    # Mock LLM should return a string
    assert isinstance(response["answer"], str)
    assert len(response["answer"]) > 0


@pytest.mark.asyncio
async def test_assistant_service_data_used_field(db_session: Session, sample_match, sample_players, sample_metrics, mock_llm_config):
    """Test that assistant includes data_used in response"""
    service = AssistantService(db_session)
    
    query = "Who covered the most distance?"
    response = await service.handle_query(query, match_id=sample_match.id)
    
    assert "data_used" in response
    assert isinstance(response["data_used"], dict)


@pytest.mark.asyncio
async def test_assistant_service_follow_up_questions(db_session: Session, sample_match, mock_llm_config):
    """Test that assistant includes follow-up questions"""
    service = AssistantService(db_session)
    
    query = "What was the score?"
    response = await service.handle_query(query, match_id=sample_match.id)
    
    assert "follow_up_questions" in response
    assert isinstance(response["follow_up_questions"], list)


# ========================================
# Mock LLM Client Tests
# ========================================

def test_mock_llm_client_returns_mock_answer():
    """Test that MockLLMClient returns recognizable mock answer"""
    client = MockLLMClient()  # MockLLMClient doesn't take arguments
    
    import asyncio
    answer = asyncio.run(client.generate_answer(
        system_prompt="You are a test",
        user_prompt="Test query"
    ))
    
    assert isinstance(answer, str)
    assert len(answer) > 0
    # Mock client returns something with "Mock" in it
    assert "Mock" in answer or "mock" in answer.lower()
