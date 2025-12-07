"""
Pydantic Schemas for AI Assistant API
"""

from typing import Optional, List, Literal
from uuid import UUID
from pydantic import BaseModel, Field


class AssistantQueryRequest(BaseModel):
    """Request schema for assistant query"""
    
    query: str = Field(..., description="Natural language question", min_length=1, max_length=500)
    match_id: Optional[UUID] = Field(None, description="Match context (required for most queries)")
    team_id: Optional[UUID] = Field(None, description="Team context (optional)")
    player_id: Optional[UUID] = Field(None, description="Player context (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Who covered the most distance in the second half?",
                "match_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class AssistantSuggestedAction(BaseModel):
    """Suggested UI action"""
    
    type: Literal["open_page", "highlight_player", "open_replay", "open_heatmap"] = Field(
        ...,
        description="Type of action to perform"
    )
    page: Optional[str] = Field(None, description="Page name to open (for open_page type)")
    match_id: Optional[UUID] = Field(None, description="Match ID for the action")
    player_id: Optional[UUID] = Field(None, description="Player ID for the action")
    timestamp: Optional[float] = Field(None, description="Timestamp in seconds (for replay)")
    label: str = Field(..., description="Human-readable action label")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "open_page",
                "page": "player_metrics",
                "match_id": "123e4567-e89b-12d3-a456-426614174000",
                "label": "View Player Metrics Dashboard"
            }
        }


class AssistantResponse(BaseModel):
    """Response schema for assistant query"""
    
    answer: str = Field(..., description="Natural language answer from AI")
    data_used: dict = Field(default_factory=dict, description="Summary of data used to generate answer")
    suggested_actions: List[AssistantSuggestedAction] = Field(
        default_factory=list,
        description="Suggested UI actions based on the answer"
    )
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up questions"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Player #10 covered the most distance in the match with 12.5 km...",
                "data_used": {
                    "top_player": {
                        "jersey": 10,
                        "distance_km": 12.5
                    }
                },
                "suggested_actions": [
                    {
                        "type": "open_page",
                        "page": "player_metrics",
                        "match_id": "123e4567-e89b-12d3-a456-426614174000",
                        "label": "View Player Metrics Dashboard"
                    }
                ],
                "follow_up_questions": [
                    "Show me this player's heatmap",
                    "Compare this player with teammates"
                ]
            }
        }


class LLMTestResponse(BaseModel):
    """Response for LLM connection test"""
    
    status: Literal["success", "error"]
    provider: str
    model: Optional[str] = None
    response: Optional[str] = None
    error: Optional[str] = None
