"""
AI Assistant API Router

Endpoints for natural language queries and LLM testing.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.assistant_schemas import (
    AssistantQueryRequest,
    AssistantResponse,
    LLMTestResponse
)
from app.assistant.service import AssistantService
from app.assistant.llm_client import test_llm_connection

router = APIRouter(prefix="/api/v1/assistant", tags=["AI Assistant"])


@router.post("/query", response_model=AssistantResponse)
async def query_assistant(
    request: AssistantQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Ask the AI assistant a natural language question about match analytics.
    
    **Examples:**
    - "Who covered the most distance?"
    - "Which player had the highest xT?"
    - "Compare the stamina of both teams"
    - "Show me the top 5 passes by xT value"
    - "What was the home team's formation?"
    - "Which player should rest next match?"
    
    **Context:**
    - Most queries require a `match_id`
    - Optionally provide `team_id` or `player_id` for more specific queries
    
    **Response:**
    - Natural language answer
    - Structured data used to generate the answer
    - Suggested UI actions (e.g., "Open Player Metrics Dashboard")
    - Follow-up question suggestions
    """
    try:
        service = AssistantService(db)
        result = await service.handle_query(
            user_query=request.query,
            match_id=request.match_id,
            team_id=request.team_id,
            player_id=request.player_id
        )
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assistant error: {str(e)}"
        )


@router.get("/test", response_model=LLMTestResponse)
async def test_llm():
    """
    Test LLM connection and configuration.
    
    Useful for verifying that:
    - LLM_PROVIDER is set correctly
    - LLM_API_KEY is valid (for cloud providers)
    - LLM service is reachable (for local providers)
    
    **Environment Variables:**
    - `LLM_PROVIDER`: "openai", "anthropic", "local", or "mock" (default: "mock")
    - `LLM_API_KEY`: API key for cloud providers
    - `LLM_MODEL`: Model name (optional, uses defaults)
    - `LLM_BASE_URL`: Base URL for local providers (default: http://localhost:11434)
    """
    result = await test_llm_connection()
    return result


@router.get("/health")
async def health_check():
    """
    Health check endpoint for assistant service.
    
    Returns basic status information.
    """
    import os
    
    return {
        "status": "healthy",
        "service": "AI Assistant",
        "llm_provider": os.getenv("LLM_PROVIDER", "mock"),
        "llm_configured": bool(os.getenv("LLM_API_KEY") or os.getenv("LLM_PROVIDER") in ["mock", "local"])
    }
