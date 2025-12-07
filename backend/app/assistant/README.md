# AI Assistant Module

Natural language query interface for Nashama Vision football analytics.

## Overview

The assistant module enables users to query match analytics using conversational language. It includes:

- **Intent parsing** - Understands user questions
- **SQL query building** - Retrieves relevant data
- **LLM integration** - Generates natural language answers
- **Action suggestions** - Provides navigation to relevant dashboards

## Architecture

```
service.py          # Main service (IntentParser, AssistantService)
sql_builder.py      # Database query functions
llm_client.py       # LLM provider clients (OpenAI, Anthropic, Local, Mock)
prompts.py          # System prompts and context templates
```

## Supported Intents

| Intent | Example Queries |
|--------|----------------|
| `player_distance` | "Who covered the most distance?" |
| `player_speed` | "Which player was the fastest?" |
| `player_stamina` | "Who needs rest?" |
| `player_xt` | "Which player had the highest xT?" |
| `tactical` | "What was the formation?" |
| `events` | "Show me the top passes" |
| `team_comparison` | "Compare both teams" |
| `player_comparison` | "Compare Player #10 and #7" |
| `general` | "Give me a match summary" |

## LLM Providers

### OpenAI
```bash
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o
```

### Anthropic
```bash
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-sonnet-20241022
```

### Local (Ollama)
```bash
LLM_PROVIDER=local
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama2
```

### Mock (Testing)
```bash
LLM_PROVIDER=mock
```

## Usage

### Basic Query
```python
from app.assistant.service import AssistantService
from app.db.session import get_db

db = next(get_db())
service = AssistantService(db)

response = await service.handle_query(
    user_query="Who covered the most distance?",
    match_id="abc-123"
)

print(response["answer"])
```

### Custom LLM Client
```python
from app.assistant.llm_client import create_llm_client

client = create_llm_client(
    provider="openai",
    api_key="sk-...",
    model="gpt-4o"
)

service = AssistantService(db, llm_client=client)
```

## Query Builder

### Available Functions

**Physical Metrics:**
- `get_top_distance_players(match_id, team_side, limit)`
- `get_top_speed_players(match_id, team_side, limit)`
- `get_workload_analysis(match_id, team_side, threshold)`
- `get_player_metrics(player_id, match_id)`

**xT Metrics:**
- `get_top_xt_players(match_id, team_side, limit)`
- `get_player_xt_metrics(player_id, match_id)`

**Tactical:**
- `get_latest_tactical_snapshot(match_id, team_side)`
- `get_pressing_timeline(match_id, team_side)`
- `get_transitions(match_id, team_side, type)`

**Events:**
- `get_events(match_id, event_type, player_id, team_side, limit)`
- `get_top_events_by_xt(match_id, event_type, limit)`

**Meta:**
- `get_match_info(match_id)`
- `compare_teams(match_id)`

## Extending

### Add New Intent

1. **Add pattern** (`service.py`):
```python
PATTERNS = {
    "my_intent": r"pattern regex here"
}
```

2. **Add query** (`sql_builder.py`):
```python
def get_my_data(self, match_id):
    # Query logic
    return results
```

3. **Add retrieval** (`service.py`):
```python
if intent == "my_intent":
    data = self.query_builder.get_my_data(match_id)
    result["my_data"] = data
```

4. **Add action** (`service.py`):
```python
if intent == "my_intent":
    actions.append({
        "type": "open_page",
        "page": "my_page",
        "label": "View My Page"
    })
```

### Add New LLM Provider

1. **Create client** (`llm_client.py`):
```python
class MyLLMClient(LLMClient):
    async def generate_answer(self, system_prompt, user_prompt):
        # Implementation
        return answer
```

2. **Add to factory** (`llm_client.py`):
```python
def create_llm_client(...):
    if provider == "myprovider":
        return MyLLMClient(...)
```

## Testing

### Test Intent Parsing
```python
from app.assistant.service import IntentParser

result = IntentParser.parse("Who covered the most distance?")
assert result["intent"] == "player_distance"
```

### Test Query Builder
```python
from app.assistant.sql_builder import QueryBuilder

builder = QueryBuilder(db)
players = builder.get_top_distance_players(match_id, limit=5)
assert len(players) <= 5
```

### Test LLM Connection
```bash
curl http://localhost:8000/api/v1/assistant/test
```

## Configuration

### Required
- `LLM_PROVIDER` - Provider name (openai/anthropic/local/mock)

### Optional
- `LLM_API_KEY` - API key (cloud providers)
- `LLM_MODEL` - Model name (provider-specific)
- `LLM_BASE_URL` - Base URL (local provider)

## Error Handling

The assistant handles various error scenarios:

- **No match context** → "Please select a match first"
- **No data found** → "I don't have enough data..."
- **LLM error** → "I encountered an error: [details]"
- **Invalid query** → Attempts to understand and suggests rephrasing

## Performance

Typical response times:
- Intent parsing: 5-10ms
- Database query: 50-200ms
- Context building: 10-20ms
- LLM generation: 500-2000ms
- **Total: 1-3 seconds**

## Security

- API keys stored in environment (never committed)
- Input validation (query length, UUID format)
- SQL injection prevention (SQLAlchemy)
- No sensitive data in error messages

## Dependencies

- SQLAlchemy (database queries)
- httpx (LLM API calls)
- Pydantic (request/response validation)

## API Endpoints

See `app/api/routers/assistant.py` for endpoint definitions:
- `POST /api/v1/assistant/query`
- `GET /api/v1/assistant/test`
- `GET /api/v1/assistant/health`

## License

Part of Nashama Vision - Advanced Football Analytics Platform
