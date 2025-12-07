"""
AI Assistant Service

Main service that orchestrates query understanding, data retrieval, 
LLM generation, and response formatting.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
import re
from sqlalchemy.orm import Session

from .sql_builder import QueryBuilder
from .llm_client import create_llm_client, LLMClient
from .prompts import (
    SYSTEM_PROMPT,
    build_context,
    FOLLOW_UP_SUGGESTIONS
)


class IntentParser:
    """Parse user queries to extract intent and entities"""
    
    # Question type patterns
    PATTERNS = {
        "player_distance": r"(who|which player).*(most|highest|top).*(distance|ran|covered)",
        "player_speed": r"(who|which player).*(fastest|quickest|top speed|max speed)",
        "player_stamina": r"(stamina|tired|fatigue|rest|workload)",
        "player_xt": r"(xT|threat|danger|dangerous)",
        "player_comparison": r"compare|versus|vs|between",
        "team_comparison": r"(team|teams).*(compare|better|more)",
        "tactical": r"(formation|pressing|defensive|tactical|shape|compact)",
        "events": r"(pass|shot|carry|event)",
        "general": r"(summary|overview|tell me about|what happened)"
    }
    
    # Entity patterns
    ENTITY_PATTERNS = {
        "jersey_number": r"#(\d+)|number (\d+)|player (\d+)",
        "team_side": r"\b(home|away)\s+team\b",
        "time_range": r"(first|second)\s+half|last\s+(\d+)\s+minutes?|minute\s+(\d+)",
        "event_type": r"\b(pass|passes|shot|shots|carry|carries|dribbl)\w*\b"
    }
    
    @classmethod
    def parse(cls, query: str) -> Dict[str, Any]:
        """
        Parse query to extract intent and entities
        
        Returns:
            {
                "intent": str,
                "entities": dict,
                "confidence": float
            }
        """
        query_lower = query.lower()
        
        # Determine intent
        intent = "general"
        confidence = 0.5
        
        for intent_type, pattern in cls.PATTERNS.items():
            if re.search(pattern, query_lower, re.IGNORECASE):
                intent = intent_type
                confidence = 0.8
                break
        
        # Extract entities
        entities = {}
        
        # Jersey number
        jersey_match = re.search(cls.ENTITY_PATTERNS["jersey_number"], query_lower)
        if jersey_match:
            entities["jersey_number"] = int(jersey_match.group(1) or jersey_match.group(2) or jersey_match.group(3))
        
        # Team side
        team_match = re.search(cls.ENTITY_PATTERNS["team_side"], query_lower)
        if team_match:
            entities["team_side"] = team_match.group(1)
        
        # Event type
        event_match = re.search(cls.ENTITY_PATTERNS["event_type"], query_lower)
        if event_match:
            event_word = event_match.group(1).lower()
            if "pass" in event_word:
                entities["event_type"] = "pass"
            elif "shot" in event_word:
                entities["event_type"] = "shot"
            elif "carr" in event_word or "dribbl" in event_word:
                entities["event_type"] = "carry"
        
        return {
            "intent": intent,
            "entities": entities,
            "confidence": confidence
        }


class AssistantService:
    """Main AI Assistant service"""
    
    def __init__(self, db: Session, llm_client: Optional[LLMClient] = None):
        self.db = db
        self.query_builder = QueryBuilder(db)
        self.llm_client = llm_client or create_llm_client()
    
    async def handle_query(
        self,
        user_query: str,
        match_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        player_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for handling user queries
        
        Args:
            user_query: Natural language question
            match_id: Optional match context
            team_id: Optional team context
            player_id: Optional player context
        
        Returns:
            {
                "answer": str,
                "data_used": dict,
                "suggested_actions": list,
                "follow_up_questions": list
            }
        """
        # Step 1: Parse intent
        parsed = IntentParser.parse(user_query)
        intent = parsed["intent"]
        entities = parsed["entities"]
        
        # Step 2: Retrieve data based on intent
        retrieval_result = await self._retrieve_data(
            intent, entities, match_id, team_id, player_id
        )
        
        if not retrieval_result["found_data"]:
            return {
                "answer": retrieval_result.get("message", "I don't have enough data to answer this question."),
                "data_used": {},
                "suggested_actions": [],
                "follow_up_questions": []
            }
        
        # Step 3: Build context for LLM
        context = build_context(
            user_query=user_query,
            match_id=match_id,
            team_id=team_id,
            player_id=player_id,
            match_info=retrieval_result.get("match_info", {}),
            player_metrics=retrieval_result.get("player_metrics", []),
            xt_metrics=retrieval_result.get("xt_metrics", []),
            tactical_data=retrieval_result.get("tactical_data", {}),
            events=retrieval_result.get("events", []),
            custom_data=retrieval_result.get("custom_data")
        )
        
        # Step 4: Generate answer with LLM
        try:
            answer = await self.llm_client.generate_answer(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=context
            )
        except Exception as e:
            answer = f"I encountered an error generating the response: {str(e)}"
        
        # Step 5: Generate suggested actions
        suggested_actions = self._generate_actions(
            intent, retrieval_result, match_id, player_id
        )
        
        # Step 6: Get follow-up suggestions
        follow_ups = FOLLOW_UP_SUGGESTIONS.get(intent, [])
        
        return {
            "answer": answer,
            "data_used": retrieval_result.get("summary", {}),
            "suggested_actions": suggested_actions,
            "follow_up_questions": follow_ups[:3]  # Top 3
        }
    
    async def _retrieve_data(
        self,
        intent: str,
        entities: dict,
        match_id: Optional[UUID],
        team_id: Optional[UUID],
        player_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Retrieve data based on intent and entities"""
        
        if not match_id:
            return {
                "found_data": False,
                "message": "Please select a match first. I need a match context to answer this question."
            }
        
        # Get match info (always needed)
        match_info = self.query_builder.get_match_info(match_id)
        if not match_info:
            return {
                "found_data": False,
                "message": f"Match not found: {match_id}"
            }
        
        result = {
            "found_data": True,
            "match_info": match_info,
            "summary": {}
        }
        
        team_side = entities.get("team_side")
        
        # Route to appropriate data retrieval
        if intent == "player_distance":
            players = self.query_builder.get_top_distance_players(match_id, team_side, limit=10)
            result["player_metrics"] = players
            result["summary"]["top_player"] = players[0] if players else None
        
        elif intent == "player_speed":
            players = self.query_builder.get_top_speed_players(match_id, team_side, limit=10)
            result["player_metrics"] = players
            result["summary"]["top_player"] = players[0] if players else None
        
        elif intent == "player_stamina":
            players = self.query_builder.get_workload_analysis(match_id, team_side, threshold=0.7)
            result["player_metrics"] = players
            result["summary"]["high_workload_count"] = len(players)
        
        elif intent == "player_xt":
            players = self.query_builder.get_top_xt_players(match_id, team_side, limit=10)
            result["xt_metrics"] = players
            result["summary"]["top_xt_player"] = players[0] if players else None
        
        elif intent == "team_comparison":
            comparison = self.query_builder.compare_teams(match_id)
            result["custom_data"] = comparison
            result["summary"] = comparison
        
        elif intent == "tactical":
            # Get tactical data for both teams
            home_tactical = self.query_builder.get_latest_tactical_snapshot(match_id, "home")
            away_tactical = self.query_builder.get_latest_tactical_snapshot(match_id, "away")
            
            if team_side == "home":
                result["tactical_data"] = home_tactical or {}
            elif team_side == "away":
                result["tactical_data"] = away_tactical or {}
            else:
                result["tactical_data"] = {
                    "home": home_tactical or {},
                    "away": away_tactical or {}
                }
        
        elif intent == "events":
            event_type = entities.get("event_type")
            events = self.query_builder.get_events(
                match_id, event_type=event_type, team_side=team_side, limit=50
            )
            result["events"] = events
            result["summary"]["event_count"] = len(events)
            
            # Also get top xT events
            if event_type:
                top_events = self.query_builder.get_top_events_by_xt(match_id, event_type, limit=5)
                result["summary"]["top_xt_events"] = top_events
        
        elif intent == "player_comparison" and player_id:
            # Get specific player data
            player_metrics = self.query_builder.get_player_metrics(player_id, match_id)
            player_xt = self.query_builder.get_player_xt_metrics(player_id, match_id)
            
            result["player_metrics"] = [player_metrics] if player_metrics else []
            result["xt_metrics"] = [player_xt] if player_xt else []
        
        else:  # general
            # Get summary of everything
            result["player_metrics"] = self.query_builder.get_top_distance_players(match_id, limit=5)
            result["xt_metrics"] = self.query_builder.get_top_xt_players(match_id, limit=5)
            result["tactical_data"] = {
                "home": self.query_builder.get_latest_tactical_snapshot(match_id, "home") or {},
                "away": self.query_builder.get_latest_tactical_snapshot(match_id, "away") or {}
            }
            result["events"] = self.query_builder.get_top_events_by_xt(match_id, limit=10)
        
        return result
    
    def _generate_actions(
        self,
        intent: str,
        data: dict,
        match_id: Optional[UUID],
        player_id: Optional[UUID]
    ) -> List[Dict[str, Any]]:
        """Generate suggested UI actions based on intent and data"""
        actions = []
        
        if not match_id:
            return actions
        
        # Action mappings
        if intent in ["player_distance", "player_speed", "player_stamina"]:
            actions.append({
                "type": "open_page",
                "page": "player_metrics",
                "match_id": str(match_id),
                "label": "View Player Metrics Dashboard"
            })
            
            # If we have a top player, suggest viewing their details
            top_player = data.get("summary", {}).get("top_player")
            if top_player:
                actions.append({
                    "type": "open_page",
                    "page": "heatmap",
                    "match_id": str(match_id),
                    "player_id": top_player.get("player_id"),
                    "label": f"View Heatmap for Player #{top_player.get('jersey')}"
                })
        
        elif intent == "player_xt":
            actions.append({
                "type": "open_page",
                "page": "xt_dashboard",
                "match_id": str(match_id),
                "label": "View xT Dashboard"
            })
        
        elif intent == "tactical":
            actions.append({
                "type": "open_page",
                "page": "tactical_dashboard",
                "match_id": str(match_id),
                "label": "View Tactical Dashboard"
            })
        
        elif intent == "events":
            actions.append({
                "type": "open_page",
                "page": "events_timeline",
                "match_id": str(match_id),
                "label": "View Events Timeline"
            })
            
            # If we have a top event, suggest jumping to replay
            top_events = data.get("summary", {}).get("top_xt_events", [])
            if top_events:
                top_event = top_events[0]
                actions.append({
                    "type": "open_replay",
                    "match_id": str(match_id),
                    "timestamp": top_event.get("timestamp"),
                    "label": f"Watch top xT event in replay ({top_event.get('event_type')})"
                })
        
        elif intent == "general":
            # Suggest main dashboards
            actions.extend([
                {
                    "type": "open_page",
                    "page": "match_details",
                    "match_id": str(match_id),
                    "label": "View Match Overview"
                },
                {
                    "type": "open_page",
                    "page": "replay",
                    "match_id": str(match_id),
                    "label": "Watch Match Replay"
                }
            ])
        
        return actions[:3]  # Limit to 3 actions
