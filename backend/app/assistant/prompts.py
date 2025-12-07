"""
LLM Prompts and Templates for AI Assistant
"""

SYSTEM_PROMPT = """You are Nashama Vision Assistant, an advanced football analytics AI assistant specialized in analyzing match data, player performance, and tactical insights.

**Your Role:**
- Provide insightful, data-driven answers about football matches, players, and teams
- Base all answers strictly on the provided context data
- Never hallucinate or invent statistics not present in the context
- Use concrete numbers, names, and timestamps when available
- Provide coach-friendly explanations that are actionable

**Available Data Types:**
1. **Physical Metrics**: Distance covered, speed, sprints, stamina, workload
2. **Tactical Data**: Formations, pressing intensity, defensive lines, team shape, transitions
3. **Expected Threat (xT)**: Zone-based threat analysis, xT gain per action, danger scores
4. **Events**: Passes, carries, shots with spatial coordinates and xT values
5. **Tracking Data**: Player and ball positions over time

**Response Guidelines:**
- Keep answers concise (2-4 sentences for simple queries, more for complex analysis)
- Always mention player names and jersey numbers when available
- Include specific metrics with units (meters, km/h, seconds, etc.)
- Suggest follow-up questions or related insights
- If data is insufficient, clearly state what's missing

**Example Response Style:**
"Player #10 (Jordan Smith) covered the most distance in the second half with 6.2 km, including 3 high-intensity sprints. His stamina remained at 78% by the 90th minute, suggesting good endurance. You might want to check his heatmap to see his coverage areas."

Remember: You are helping coaches and analysts make better decisions. Be precise, helpful, and insightful.
"""

CONTEXT_TEMPLATE = """
# Match Context

## Match Information
{match_info}

## Query Context
User Question: {user_query}
Scope: {scope}

## Retrieved Data

{data_context}

## Instructions
Based on the above context, answer the user's question. If the data is insufficient, explain what's missing. Suggest related insights or follow-up questions when appropriate.
"""

def format_match_info(match_data: dict) -> str:
    """Format match metadata for context"""
    if not match_data:
        return "No specific match selected."
    
    return f"""
- Match ID: {match_data.get('match_id', 'N/A')}
- Teams: {match_data.get('home_team', 'N/A')} vs {match_data.get('away_team', 'N/A')}
- Date: {match_data.get('date', 'N/A')}
- Duration: {match_data.get('duration', 'N/A')} minutes
"""

def format_scope(match_id, team_id, player_id) -> str:
    """Format query scope"""
    scopes = []
    if match_id:
        scopes.append(f"Match: {match_id}")
    if team_id:
        scopes.append(f"Team: {team_id}")
    if player_id:
        scopes.append(f"Player: {player_id}")
    return ", ".join(scopes) if scopes else "All available data"

def format_player_metrics(players: list[dict]) -> str:
    """Format player physical metrics for context"""
    if not players:
        return "No player metrics available."
    
    lines = ["### Physical Metrics (Top Players)\n"]
    for p in players[:10]:  # Top 10
        lines.append(
            f"- **{p.get('name', 'Unknown')} (#{p.get('jersey', 'N/A')})**: "
            f"{p.get('distance_km', 0):.2f} km, "
            f"Max Speed: {p.get('max_speed', 0):.1f} km/h, "
            f"Sprints: {p.get('sprint_count', 0)}, "
            f"Stamina: {p.get('stamina_pct', 0):.0f}%"
        )
    return "\n".join(lines)

def format_xt_metrics(players: list[dict]) -> str:
    """Format xT metrics for context"""
    if not players:
        return "No xT metrics available."
    
    lines = ["### Expected Threat (xT) Metrics\n"]
    for p in players[:10]:  # Top 10
        lines.append(
            f"- **{p.get('name', 'Unknown')} (#{p.get('jersey', 'N/A')})**: "
            f"xT Gain: {p.get('xt_gain', 0):.3f}, "
            f"Danger Score: {p.get('danger_score', 0):.0f}, "
            f"Passes: {p.get('pass_count', 0)}, "
            f"Carries: {p.get('carry_count', 0)}, "
            f"Shots: {p.get('shot_count', 0)}"
        )
    return "\n".join(lines)

def format_tactical_summary(tactical_data: dict) -> str:
    """Format tactical analysis for context"""
    if not tactical_data:
        return "No tactical data available."
    
    lines = ["### Tactical Analysis\n"]
    
    if "formation" in tactical_data:
        lines.append(f"- **Formation**: {tactical_data['formation']} (confidence: {tactical_data.get('formation_confidence', 0):.0%})")
    
    if "pressing_intensity" in tactical_data:
        lines.append(f"- **Pressing Intensity**: {tactical_data['pressing_intensity']:.0f}/100")
    
    if "team_compactness" in tactical_data:
        lines.append(f"- **Team Compactness**: {tactical_data['team_compactness']:.1f} m²")
    
    if "defensive_line_height" in tactical_data:
        lines.append(f"- **Defensive Line Height**: {tactical_data['defensive_line_height']:.1f} m from own goal")
    
    if "block_type" in tactical_data:
        lines.append(f"- **Block Type**: {tactical_data['block_type']}")
    
    return "\n".join(lines)

def format_events_summary(events: list[dict]) -> str:
    """Format events summary for context"""
    if not events:
        return "No events data available."
    
    event_counts = {}
    total_xt = 0.0
    
    for e in events:
        event_type = e.get('event_type', 'unknown')
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
        total_xt += e.get('xt_value', 0.0)
    
    lines = ["### Events Summary\n"]
    lines.append(f"- **Total Events**: {len(events)}")
    for event_type, count in event_counts.items():
        lines.append(f"- **{event_type.capitalize()}s**: {count}")
    lines.append(f"- **Total xT Generated**: {total_xt:.3f}")
    
    return "\n".join(lines)

def build_context(
    user_query: str,
    match_id,
    team_id,
    player_id,
    match_info: dict,
    player_metrics: list[dict],
    xt_metrics: list[dict],
    tactical_data: dict,
    events: list[dict],
    custom_data: dict = None
) -> str:
    """Build complete context for LLM"""
    
    data_sections = []
    
    if player_metrics:
        data_sections.append(format_player_metrics(player_metrics))
    
    if xt_metrics:
        data_sections.append(format_xt_metrics(xt_metrics))
    
    if tactical_data:
        data_sections.append(format_tactical_summary(tactical_data))
    
    if events:
        data_sections.append(format_events_summary(events))
    
    if custom_data:
        data_sections.append(f"### Additional Data\n{custom_data}")
    
    if not data_sections:
        data_sections.append("No relevant data found for this query.")
    
    return CONTEXT_TEMPLATE.format(
        match_info=format_match_info(match_info),
        user_query=user_query,
        scope=format_scope(match_id, team_id, player_id),
        data_context="\n\n".join(data_sections)
    )

# Follow-up question suggestions
FOLLOW_UP_SUGGESTIONS = {
    "player_summary": [
        "Show me this player's heatmap",
        "Compare this player with teammates",
        "What were this player's key events?"
    ],
    "team_summary": [
        "Show me the tactical dashboard",
        "Which players contributed most to xT?",
        "How did the pressing intensity change over time?"
    ],
    "xt_question": [
        "Which zones generated the most threat?",
        "Show me the xT dashboard",
        "What were the top xT events?"
    ],
    "tactical_question": [
        "How did the formation change during the match?",
        "Show me the defensive transitions",
        "What was the pressing intensity timeline?"
    ]
}
