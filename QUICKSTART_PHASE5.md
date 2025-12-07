# 🚀 PHASE 5 QUICKSTART GUIDE

## AI Assistant - Get Started in 5 Minutes

---

## Prerequisites

- Nashama Vision Phases 1-4 installed and running
- PostgreSQL with match data
- Redis running
- Node.js and npm installed

---

## Option 1: Mock Mode (No API Key Required)

Perfect for testing and development without LLM costs.

### 1. Backend Setup

```bash
cd backend

# Add to .env file
echo "LLM_PROVIDER=mock" >> .env

# Restart FastAPI
uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Already includes all dependencies
npm install  # if not already done
npm run dev
```

### 3. Access Assistant

Navigate to: http://localhost:5173/assistant

Select a match and start asking questions!

**Note:** Mock mode returns placeholder responses for testing the UI flow.

---

## Option 2: OpenAI (Recommended for Production)

Best quality responses with GPT-4.

### 1. Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy the key (starts with `sk-`)

### 2. Configure Backend

```bash
cd backend

# Add to .env file
echo "LLM_PROVIDER=openai" >> .env
echo "LLM_API_KEY=sk-your-key-here" >> .env
echo "LLM_MODEL=gpt-4o" >> .env

# Restart FastAPI
uvicorn app.main:app --reload
```

### 3. Test Connection

```bash
curl http://localhost:8000/api/v1/assistant/test
```

Should return:
```json
{
  "status": "success",
  "provider": "openai",
  "model": "gpt-4o",
  "response": "Hello, I'm working!"
}
```

### 4. Access Assistant

Navigate to: http://localhost:5173/assistant

---

## Option 3: Local LLM (Free, Private)

Run LLMs locally using Ollama.

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai/download

### 2. Pull a Model

```bash
# Recommended: Llama 2 (7B)
ollama pull llama2

# Or Llama 3 (8B) - better quality
ollama pull llama3

# Or Mistral (7B) - balanced
ollama pull mistral
```

### 3. Start Ollama

```bash
ollama serve
```

### 4. Configure Backend

```bash
cd backend

# Add to .env file
echo "LLM_PROVIDER=local" >> .env
echo "LLM_BASE_URL=http://localhost:11434" >> .env
echo "LLM_MODEL=llama2" >> .env

# Restart FastAPI
uvicorn app.main:app --reload
```

### 5. Test Connection

```bash
curl http://localhost:8000/api/v1/assistant/test
```

---

## Example Queries to Try

Once the assistant is running, try these questions:

### Physical Metrics
```
Who covered the most distance?
Which player was the fastest?
Show me players with high workload
Compare Player #10 and Player #7
```

### xT & Threat
```
Which player had the highest xT?
Show me the top 5 dangerous passes
What was the total xT for the home team?
Which player created the most threat?
```

### Tactical
```
What formation was the home team using?
What was the pressing intensity?
How high was the defensive line?
Show me defensive transitions
```

### Events
```
How many shots were there?
Show me all passes from Player #10
Which player made the most carries?
List shots on goal
```

### General
```
Give me a match summary
Tell me about this match
What happened in the second half?
```

---

## Troubleshooting

### "Please select a match first"
→ Use the match selector dropdown to choose a match

### "LLM API error"
→ Check your API key is valid and has credits

### "Local LLM error"
→ Ensure Ollama is running: `ollama serve`

### Empty responses
→ Check backend logs for errors: `uvicorn app.main:app --log-level debug`

### Slow responses (local)
→ Local LLMs take longer (10-30s). Consider using a faster model or GPU acceleration.

---

## API Testing

### Test with curl

```bash
# Test query
curl -X POST http://localhost:8000/api/v1/assistant/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who covered the most distance?",
    "match_id": "your-match-id-here"
  }'

# Test LLM
curl http://localhost:8000/api/v1/assistant/test

# Health check
curl http://localhost:8000/api/v1/assistant/health
```

### Test with Python

```python
import requests

# Query
response = requests.post(
    "http://localhost:8000/api/v1/assistant/query",
    json={
        "query": "Who covered the most distance?",
        "match_id": "your-match-id"
    }
)
print(response.json())
```

---

## Cost Estimates

### OpenAI (gpt-4o)
- Input: $2.50 / 1M tokens
- Output: $10.00 / 1M tokens
- **Per query:** ~$0.01-0.03

### OpenAI (gpt-3.5-turbo)
- Input: $0.50 / 1M tokens
- Output: $1.50 / 1M tokens
- **Per query:** ~$0.001-0.005

### Anthropic (claude-3-5-sonnet)
- Input: $3.00 / 1M tokens
- Output: $15.00 / 1M tokens
- **Per query:** ~$0.01-0.02

### Local (Ollama)
- **Cost:** Free
- **Requirements:** 8GB+ RAM recommended
- **Speed:** Depends on hardware (10-30s per query)

### Mock
- **Cost:** Free
- **Use case:** Testing only

---

## Next Steps

1. **Integrate with Match Pages:**
   - Add `AssistantButton` to match detail pages
   - Pre-fill match context

2. **Customize Prompts:**
   - Edit `app/assistant/prompts.py`
   - Adjust system prompt for your use case

3. **Add Custom Queries:**
   - Add new intent patterns in `IntentParser`
   - Add corresponding query functions in `QueryBuilder`

4. **Enhance UI:**
   - Customize colors in `AssistantChat.jsx`
   - Add more quick question templates

5. **Monitor Usage:**
   - Track API costs
   - Monitor response times
   - Analyze popular queries

---

## Support

For issues or questions:
1. Check logs: `backend/logs/`
2. Review API docs: http://localhost:8000/docs
3. Test endpoints individually
4. Verify environment variables

---

## Quick Reference

### Environment Variables
```bash
# Mock (testing)
LLM_PROVIDER=mock

# OpenAI
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o

# Anthropic
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-sonnet-20241022

# Local
LLM_PROVIDER=local
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama2
```

### URLs
- Assistant Page: http://localhost:5173/assistant
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/assistant/health

---

**You're ready to go! Start asking questions and explore your match data with AI.** 🎉
