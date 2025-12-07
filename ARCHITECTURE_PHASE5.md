# 🏗️ PHASE 5 - SYSTEM ARCHITECTURE

## AI Assistant / Coach Bot - Technical Architecture

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                    React + Tailwind CSS                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  AssistantPage (Full Page)                             │    │
│  │  ┌──────────────┬──────────────────────────────────┐  │    │
│  │  │ Sidebar      │ AssistantChat                    │  │    │
│  │  │ • Match      │ • AssistantMessage (messages)    │  │    │
│  │  │   Selector   │ • Input + Send                   │  │    │
│  │  │ • AI Status  │ • Loading states                 │  │    │
│  │  │ • Help Info  │ • Error handling                 │  │    │
│  │  └──────────────┴──────────────────────────────────┘  │    │
│  │                                                         │    │
│  │  useAssistant Hook                                     │    │
│  │  • messages state                                      │    │
│  │  • sendQuery()                                         │    │
│  │  • React Query integration                            │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP/REST
                       │ POST /api/v1/assistant/query
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API GATEWAY                                │
│                    FastAPI + Uvicorn                             │
│                                                                  │
│  📍 /api/v1/assistant/query                                     │
│     • Accepts: AssistantQueryRequest                            │
│     • Returns: AssistantResponse                                │
│     • Handler: query_assistant()                                │
│                                                                  │
│  📍 /api/v1/assistant/test                                      │
│     • Tests LLM connection                                      │
│     • Returns: LLMTestResponse                                  │
│                                                                  │
│  📍 /api/v1/assistant/health                                    │
│     • Health check                                              │
│     • Returns: status + config                                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ASSISTANT SERVICE LAYER                        │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ AssistantService.handle_query()                           │ │
│  │                                                           │ │
│  │  Step 1: Parse Intent                                    │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │ IntentParser.parse(user_query)                     │  │ │
│  │  │ • Regex pattern matching                           │  │ │
│  │  │ • Entity extraction (jersey #, team, event type)   │  │ │
│  │  │ • Returns: intent + entities + confidence          │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │                                                           │ │
│  │  Step 2: Build SQL Queries                               │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │ QueryBuilder (SQLAlchemy)                          │  │ │
│  │  │                                                     │  │ │
│  │  │ Physical Metrics:                                  │  │ │
│  │  │ • get_top_distance_players()                       │  │ │
│  │  │ • get_top_speed_players()                          │  │ │
│  │  │ • get_workload_analysis()                          │  │ │
│  │  │ • get_player_metrics()                             │  │ │
│  │  │                                                     │  │ │
│  │  │ xT Metrics:                                        │  │ │
│  │  │ • get_top_xt_players()                             │  │ │
│  │  │ • get_player_xt_metrics()                          │  │ │
│  │  │                                                     │  │ │
│  │  │ Tactical:                                          │  │ │
│  │  │ • get_latest_tactical_snapshot()                   │  │ │
│  │  │ • get_pressing_timeline()                          │  │ │
│  │  │ • get_transitions()                                │  │ │
│  │  │                                                     │  │ │
│  │  │ Events:                                            │  │ │
│  │  │ • get_events()                                     │  │ │
│  │  │ • get_top_events_by_xt()                           │  │ │
│  │  │                                                     │  │ │
│  │  │ Meta:                                              │  │ │
│  │  │ • get_match_info()                                 │  │ │
│  │  │ • compare_teams()                                  │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │                                                           │ │
│  │  Step 3: Execute Queries                                 │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │ PostgreSQL Database                                │  │ │
│  │  │ • PlayerMetrics                                    │  │ │
│  │  │ • XTMetrics                                        │  │ │
│  │  │ • TacticalSnapshot                                 │  │ │
│  │  │ • Event                                            │  │ │
│  │  │ • PlayerTrack                                      │  │ │
│  │  │ • Match                                            │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │                                                           │ │
│  │  Step 4: Build Context                                   │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │ Context Builder (prompts.py)                       │  │ │
│  │  │                                                     │  │ │
│  │  │ build_context():                                   │  │ │
│  │  │ • format_match_info()                              │  │ │
│  │  │ • format_player_metrics()                          │  │ │
│  │  │ • format_xt_metrics()                              │  │ │
│  │  │ • format_tactical_summary()                        │  │ │
│  │  │ • format_events_summary()                          │  │ │
│  │  │                                                     │  │ │
│  │  │ Output: Structured context string                  │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │                                                           │ │
│  │  Step 5: Call LLM                                        │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │ LLMClient.generate_answer()                        │  │ │
│  │  │ • system_prompt: SYSTEM_PROMPT                     │  │ │
│  │  │ • user_prompt: context                             │  │ │
│  │  │ • Returns: natural language answer                 │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │                                                           │ │
│  │  Step 6: Generate Actions                                │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │ _generate_actions()                                │  │ │
│  │  │ • Maps intent to UI actions                        │  │ │
│  │  │ • Creates navigation suggestions                   │  │ │
│  │  │ • Links to dashboards/replay                       │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │                                                           │ │
│  │  Step 7: Assemble Response                               │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │ AssistantResponse                                  │  │ │
│  │  │ • answer: str                                      │  │ │
│  │  │ • data_used: dict                                  │  │ │
│  │  │ • suggested_actions: list                          │  │ │
│  │  │ • follow_up_questions: list                        │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                       LLM PROVIDER LAYER                         │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ LLMClient (Abstract Base)                                 │ │
│  │ • async generate_answer(system, user) -> str              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐ │
│  │ OpenAIClient │AnthropicClient│LocalLLMClient│MockLLMClient│ │
│  │              │              │              │             │ │
│  │ GPT-4o       │ Claude 3.5   │ Ollama       │ Testing     │ │
│  │ GPT-3.5      │ Claude 3     │ Llama2/3     │ No API Key  │ │
│  │              │              │ Mistral      │             │ │
│  └──────────────┴──────────────┴──────────────┴─────────────┘ │
│                                                                  │
│  Factory: create_llm_client(provider, api_key, model)           │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL LLM SERVICES                        │
│                                                                  │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ OpenAI API      │  │ Anthropic API    │  │ Local Ollama │  │
│  │ api.openai.com  │  │ api.anthropic.com│  │ localhost    │  │
│  └─────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Diagram

### Backend Components

```
┌────────────────────────────────────────────────────────────┐
│                     Backend Structure                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  app/assistant/                                            │
│  ├── __init__.py                                           │
│  ├── service.py                 (350 lines)                │
│  │   ├── IntentParser class                               │
│  │   │   └── parse(query) -> intent + entities            │
│  │   └── AssistantService class                           │
│  │       ├── handle_query()                               │
│  │       ├── _retrieve_data()                             │
│  │       └── _generate_actions()                          │
│  │                                                         │
│  ├── sql_builder.py             (600 lines)                │
│  │   └── QueryBuilder class                               │
│  │       ├── Physical: get_top_distance_players()         │
│  │       ├── Physical: get_top_speed_players()            │
│  │       ├── Physical: get_workload_analysis()            │
│  │       ├── Physical: get_player_metrics()               │
│  │       ├── xT: get_top_xt_players()                     │
│  │       ├── xT: get_player_xt_metrics()                  │
│  │       ├── Tactical: get_latest_tactical_snapshot()     │
│  │       ├── Tactical: get_pressing_timeline()            │
│  │       ├── Tactical: get_transitions()                  │
│  │       ├── Events: get_events()                         │
│  │       ├── Events: get_top_events_by_xt()               │
│  │       ├── Meta: get_match_info()                       │
│  │       └── Meta: compare_teams()                        │
│  │                                                         │
│  ├── llm_client.py              (200 lines)                │
│  │   ├── LLMClient (ABC)                                  │
│  │   ├── OpenAIClient                                     │
│  │   ├── AnthropicClient                                  │
│  │   ├── LocalLLMClient                                   │
│  │   ├── MockLLMClient                                    │
│  │   ├── create_llm_client()                              │
│  │   └── test_llm_connection()                            │
│  │                                                         │
│  └── prompts.py                 (250 lines)                │
│      ├── SYSTEM_PROMPT                                     │
│      ├── CONTEXT_TEMPLATE                                  │
│      ├── format_match_info()                              │
│      ├── format_player_metrics()                          │
│      ├── format_xt_metrics()                              │
│      ├── format_tactical_summary()                        │
│      ├── format_events_summary()                          │
│      ├── build_context()                                  │
│      └── FOLLOW_UP_SUGGESTIONS                            │
│                                                            │
│  app/api/routers/                                          │
│  └── assistant.py               (100 lines)                │
│      ├── query_assistant()                                │
│      ├── test_llm()                                       │
│      └── health_check()                                   │
│                                                            │
│  app/schemas/                                              │
│  └── assistant_schemas.py       (80 lines)                 │
│      ├── AssistantQueryRequest                            │
│      ├── AssistantSuggestedAction                         │
│      ├── AssistantResponse                                │
│      └── LLMTestResponse                                  │
└────────────────────────────────────────────────────────────┘
```

### Frontend Components

```
┌────────────────────────────────────────────────────────────┐
│                    Frontend Structure                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  src/hooks/                                                │
│  └── useAssistant.js            (100 lines)                │
│      ├── useAssistant()                                    │
│      │   ├── messages state                               │
│      │   ├── sendQuery()                                  │
│      │   ├── clearMessages()                              │
│      │   └── isLoading, error                             │
│      ├── useLLMTest()                                     │
│      └── useAssistantHealth()                             │
│                                                            │
│  src/components/assistant/                                 │
│  ├── AssistantMessage.jsx       (120 lines)                │
│  │   ├── Message bubble rendering                         │
│  │   ├── User vs assistant styling                        │
│  │   ├── Data summary display                             │
│  │   ├── Action buttons                                   │
│  │   ├── Follow-up questions                              │
│  │   └── Timestamp                                        │
│  │                                                         │
│  ├── AssistantChat.jsx          (250 lines)                │
│  │   ├── Chat interface                                   │
│  │   ├── Message list                                     │
│  │   ├── Input + send button                              │
│  │   ├── Loading indicator                                │
│  │   ├── Welcome screen                                   │
│  │   ├── Quick questions                                  │
│  │   ├── Action handler (navigation)                      │
│  │   └── Auto-scroll                                      │
│  │                                                         │
│  └── AssistantButton.jsx        (50 lines)                 │
│      ├── Compact mode                                     │
│      ├── Full button mode                                 │
│      └── Navigation with context                          │
│                                                            │
│  src/pages/                                                │
│  └── AssistantPage.jsx          (300 lines)                │
│      ├── Full-page layout                                 │
│      ├── Sidebar:                                         │
│      │   ├── Match selector                               │
│      │   ├── AI status display                            │
│      │   └── Help section                                 │
│      └── Main area: AssistantChat                         │
│                                                            │
│  src/services/                                             │
│  └── api.js                     (updated)                  │
│      └── assistantApi                                     │
│          ├── query()                                      │
│          ├── testLLM()                                    │
│          └── health()                                     │
└────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

### Query Processing Flow

```
1. USER INPUT
   ↓
   "Who covered the most distance?"
   ↓
   
2. FRONTEND (useAssistant)
   ↓
   sendQuery(query, { matchId })
   ↓
   POST /api/v1/assistant/query
   {
     "query": "Who covered the most distance?",
     "match_id": "abc-123"
   }
   ↓

3. FASTAPI ROUTER
   ↓
   query_assistant(request, db)
   ↓
   AssistantService(db)
   ↓

4. INTENT PARSING
   ↓
   IntentParser.parse(query)
   ↓
   {
     "intent": "player_distance",
     "entities": {},
     "confidence": 0.8
   }
   ↓

5. SQL QUERY BUILDING
   ↓
   QueryBuilder.get_top_distance_players(match_id, limit=10)
   ↓
   SQLAlchemy Query:
   SELECT PlayerMetrics.*, PlayerTrack.jersey_number
   FROM player_metrics
   JOIN player_tracks ...
   WHERE match_id = 'abc-123'
   ORDER BY total_distance_m DESC
   LIMIT 10
   ↓

6. DATABASE QUERY
   ↓
   PostgreSQL Execution
   ↓
   Results: [
     {player_id, jersey, distance_km, ...},
     ...
   ]
   ↓

7. CONTEXT BUILDING
   ↓
   build_context(
     user_query,
     match_info,
     player_metrics=[...]
   )
   ↓
   """
   # Match Context
   ## Match Information
   - Match ID: abc-123
   ...
   
   ## Retrieved Data
   ### Physical Metrics
   - Player #10: 12.5 km, ...
   - Player #7: 11.8 km, ...
   """
   ↓

8. LLM GENERATION
   ↓
   LLMClient.generate_answer(SYSTEM_PROMPT, context)
   ↓
   [API Call to OpenAI/Anthropic/Local]
   ↓
   "Player #10 covered the most distance in the match with 12.5 km. 
    This included 15 high-intensity sprints and a maximum speed of 
    32.1 km/h. Their stamina remained at 78% by the end of the match..."
   ↓

9. ACTION GENERATION
   ↓
   _generate_actions(intent, data, match_id)
   ↓
   [
     {
       "type": "open_page",
       "page": "player_metrics",
       "match_id": "abc-123",
       "label": "View Player Metrics Dashboard"
     },
     {
       "type": "open_page",
       "page": "heatmap",
       "player_id": "...",
       "label": "View Heatmap for Player #10"
     }
   ]
   ↓

10. RESPONSE ASSEMBLY
    ↓
    AssistantResponse {
      answer: "Player #10...",
      data_used: {top_player: {...}},
      suggested_actions: [...],
      follow_up_questions: [...]
    }
    ↓

11. FRONTEND DISPLAY
    ↓
    useAssistant receives response
    ↓
    Updates messages state
    ↓
    AssistantMessage renders:
    • Answer text
    • Data summary
    • Action buttons
    • Follow-up suggestions
```

---

## Database Schema Usage

### Tables Queried by Assistant

```sql
-- Physical Metrics (Phase 2)
player_metrics
  ├─ total_distance_m
  ├─ max_speed_ms
  ├─ avg_speed_ms
  ├─ sprint_count
  ├─ stamina_index
  └─ high_intensity_distance_m

-- xT Metrics (Phase 3)
xt_metrics
  ├─ total_xt_gain
  ├─ danger_score
  ├─ pass_xt, carry_xt, shot_xt
  └─ pass_count, carry_count, shot_count

-- Tactical (Phase 3)
tactical_snapshots
  ├─ formation
  ├─ formation_confidence
  ├─ pressing_intensity
  ├─ team_compactness
  ├─ defensive_line_height
  └─ block_type

transition_metrics
  ├─ transition_type
  ├─ duration_seconds
  ├─ distance_covered_m
  └─ avg_speed_ms

-- Events (Phase 3)
events
  ├─ event_type (pass/carry/shot)
  ├─ start_x_m, start_y_m
  ├─ end_x_m, end_y_m
  ├─ distance_m
  ├─ velocity_ms
  └─ xt_value

-- Tracks (Phase 1)
player_tracks
  ├─ jersey_number
  ├─ team_side
  └─ object_class

-- Matches (Phase 1)
matches
  ├─ match_name
  ├─ match_date
  ├─ home_team_name
  └─ away_team_name
```

---

## Intent Classification

### Intent → Query Mapping

| Intent | Patterns | Query Functions | Tables |
|--------|----------|----------------|--------|
| `player_distance` | "most distance", "ran", "covered" | `get_top_distance_players` | player_metrics, player_tracks |
| `player_speed` | "fastest", "quickest", "max speed" | `get_top_speed_players` | player_metrics, player_tracks |
| `player_stamina` | "stamina", "tired", "fatigue" | `get_workload_analysis` | player_metrics, player_tracks |
| `player_xt` | "xT", "threat", "danger" | `get_top_xt_players` | xt_metrics, player_tracks |
| `tactical` | "formation", "pressing", "defensive" | `get_latest_tactical_snapshot` | tactical_snapshots |
| `events` | "pass", "shot", "carry" | `get_events`, `get_top_events_by_xt` | events, player_tracks |
| `team_comparison` | "compare", "teams", "versus" | `compare_teams` | All metrics tables |
| `general` | "summary", "overview", "tell me" | Multiple queries | All tables |

---

## LLM Provider Architecture

### Provider Selection Flow

```
Environment Variable: LLM_PROVIDER
    ↓
create_llm_client(provider, api_key, model)
    ↓
    ├─ "openai" → OpenAIClient
    │   ├─ Base URL: https://api.openai.com/v1/chat/completions
    │   ├─ Models: gpt-4o, gpt-3.5-turbo, gpt-4-turbo
    │   └─ Auth: Bearer token
    │
    ├─ "anthropic" → AnthropicClient
    │   ├─ Base URL: https://api.anthropic.com/v1/messages
    │   ├─ Models: claude-3-5-sonnet, claude-3-opus
    │   └─ Auth: x-api-key header
    │
    ├─ "local" → LocalLLMClient
    │   ├─ Base URL: http://localhost:11434 (Ollama)
    │   ├─ Models: llama2, llama3, mistral, codellama
    │   └─ Auth: None
    │
    └─ "mock" → MockLLMClient
        └─ Returns: Placeholder response for testing
```

### LLM Client Interface

```python
class LLMClient(ABC):
    """Abstract base for all LLM providers"""
    
    @abstractmethod
    async def generate_answer(
        self, 
        system_prompt: str,
        user_prompt: str
    ) -> str:
        """Generate answer from LLM"""
        pass

# All providers implement this interface
# Switching providers = changing environment variable
```

---

## API Endpoint Specification

### POST /api/v1/assistant/query

**Request:**
```json
{
  "query": "Who covered the most distance?",
  "match_id": "uuid",
  "team_id": "uuid (optional)",
  "player_id": "uuid (optional)"
}
```

**Response:**
```json
{
  "answer": "Player #10 covered the most distance...",
  "data_used": {
    "top_player": {
      "jersey": 10,
      "distance_km": 12.5,
      "sprint_count": 15
    }
  },
  "suggested_actions": [
    {
      "type": "open_page",
      "page": "player_metrics",
      "match_id": "uuid",
      "label": "View Player Metrics Dashboard"
    }
  ],
  "follow_up_questions": [
    "Show me this player's heatmap",
    "Compare this player with teammates"
  ]
}
```

### GET /api/v1/assistant/test

**Response:**
```json
{
  "status": "success",
  "provider": "openai",
  "model": "gpt-4o",
  "response": "Hello, I'm working!"
}
```

### GET /api/v1/assistant/health

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Assistant",
  "llm_provider": "openai",
  "llm_configured": true
}
```

---

## Performance Considerations

### Response Time Breakdown

```
Total Time: 1-3 seconds (typical)

├─ Intent Parsing: 5-10ms
├─ SQL Query: 50-200ms
├─ Context Building: 10-20ms
├─ LLM Generation: 500-2000ms (varies by provider)
└─ Response Assembly: 5-10ms

Factors:
• Database size
• LLM provider speed
• Network latency
• Query complexity
```

### Optimization Strategies

1. **Database Indexing**
   - Index on `match_id` (all tables)
   - Index on `player_id` (all tables)
   - Index on `timestamp_seconds` (events, tactical_snapshots)

2. **Query Limits**
   - Default limit: 10 results
   - Prevents excessive data retrieval

3. **LLM Token Limits**
   - Max context: ~2000 tokens
   - Max response: ~1000 tokens
   - Prevents slow/expensive responses

4. **Caching (Future)**
   - Cache frequent queries
   - Cache LLM responses for identical queries
   - Redis integration

---

## Security Considerations

### API Key Management

```
Environment Variables (Never commit):
  ├─ LLM_API_KEY → Stored in .env
  ├─ Access → Backend only
  └─ Frontend → Never exposed

Backend validates all requests
Frontend cannot access API keys directly
```

### Input Validation

```
Request Validation:
  ├─ Query length: max 500 characters
  ├─ UUIDs: validated format
  └─ SQL injection: Prevented by SQLAlchemy
```

### Rate Limiting (Recommended)

```
Implement rate limiting:
  ├─ Per user: 10 queries/minute
  ├─ Per IP: 20 queries/minute
  └─ Global: 100 queries/minute
```

---

## Monitoring & Logging

### Logged Events

```
Assistant Query:
  ├─ User query
  ├─ Intent detected
  ├─ Match context
  ├─ LLM provider
  ├─ Response time
  └─ Success/error

LLM Calls:
  ├─ Provider
  ├─ Model
  ├─ Token usage
  ├─ Cost (estimated)
  └─ Latency
```

### Metrics to Track

```
• Total queries
• Queries per intent type
• Average response time
• LLM success rate
• Error rate
• Popular queries
• Cost per query (cloud providers)
```

---

## Error Handling

### Backend Error Scenarios

| Error | Cause | Response |
|-------|-------|----------|
| No match context | `match_id` not provided | "Please select a match first." |
| Match not found | Invalid `match_id` | "Match not found: {id}" |
| No data | Query returns empty | "I don't have enough data..." |
| LLM error | API failure | "I encountered an error: {error}" |
| Timeout | LLM too slow | "Request timed out. Try again." |

### Frontend Error Handling

```
useAssistant hook:
  ├─ onError → Add error message to chat
  ├─ Display → Red error bubble
  └─ Retry → User can resend query
```

---

## Extensibility

### Adding New Intent Types

1. Add pattern to `IntentParser.PATTERNS`
2. Add query function to `QueryBuilder`
3. Add case to `AssistantService._retrieve_data()`
4. Add action mapping to `_generate_actions()`
5. Update prompts if needed

### Adding New LLM Providers

1. Create new client class inheriting `LLMClient`
2. Implement `generate_answer()` method
3. Add case to `create_llm_client()` factory
4. Document provider setup

### Adding Custom Queries

```python
# sql_builder.py
def get_custom_metric(self, match_id):
    # Your custom query
    pass

# service.py
if intent == "custom":
    data = self.query_builder.get_custom_metric(match_id)
```

---

## Testing Strategy

### Unit Tests

```
• IntentParser.parse() → All intent types
• QueryBuilder methods → Mock database
• LLMClient → Mock responses
• Context builders → Format validation
```

### Integration Tests

```
• Full query flow → End-to-end
• Database queries → Real data
• LLM calls → Mock provider
```

### E2E Tests

```
• Frontend → Backend → LLM → Frontend
• User journey scenarios
• Error scenarios
```

---

## Deployment

### Environment Setup

```bash
# Production
LLM_PROVIDER=openai
LLM_API_KEY=sk-prod-key
LLM_MODEL=gpt-4o

# Staging
LLM_PROVIDER=openai
LLM_API_KEY=sk-staging-key
LLM_MODEL=gpt-3.5-turbo

# Development
LLM_PROVIDER=mock
```

### Docker Support

```dockerfile
# Add to backend Dockerfile
ENV LLM_PROVIDER=${LLM_PROVIDER}
ENV LLM_API_KEY=${LLM_API_KEY}
ENV LLM_MODEL=${LLM_MODEL}
```

---

**Phase 5 architecture complete and ready for production!** 🚀
