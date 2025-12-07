# 🚀 PHASE 6 - QUICK START GUIDE

## Testing & Deployment in 10 Minutes

---

## 🧪 PART 1: RUNNING TESTS (5 minutes)

### Backend Tests

```bash
# 1. Navigate to backend
cd backend

# 2. Install pytest (if needed)
pip install pytest pytest-asyncio httpx

# 3. Run all tests
pytest

# 4. Run with coverage
pytest --cov=app

# Expected output:
# ====== 55 passed in 5.23s ======
# Coverage: 75%
```

**What's being tested:**
- ✅ API endpoints (matches, analytics, replay, assistant)
- ✅ Physical metrics engine
- ✅ Heatmap generation
- ✅ Tactical engine
- ✅ xT calculations
- ✅ Event detection
- ✅ Assistant service

### Frontend Tests

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Run tests
npm test

# Expected output:
# Test Files  4 passed (4)
# Tests  15 passed (15)
```

**What's being tested:**
- ✅ AssistantChat component
- ✅ AssistantPage layout
- ✅ MatchReplayView rendering
- ✅ PlayerMetricsView data display

---

## 🐳 PART 2: DOCKER DEPLOYMENT (5 minutes)

### Quick Deploy

```bash
# 1. Copy environment template
cp .env.prod.example .env.prod

# 2. Edit .env.prod (minimum required)
# - Set POSTGRES_PASSWORD
# - Set SECRET_KEY
# - Set LLM_PROVIDER=mock (for testing)

# 3. Build and start
docker compose -f docker-compose.prod.yml up -d --build

# 4. Check status
docker compose -f docker-compose.prod.yml ps

# 5. Run migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 6. Access application
# Frontend: http://localhost
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Verify Deployment

```bash
# Check all services are healthy
docker compose -f docker-compose.prod.yml ps

# Expected:
# ✅ postgres    (healthy)
# ✅ redis       (healthy)
# ✅ backend     (running)
# ✅ worker      (running)
# ✅ frontend    (running)

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost/health

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## ⚡ PART 3: PERFORMANCE TEST (Optional)

```bash
# 1. Ensure backend is running
cd backend

# 2. Run performance test
python tests/performance_test.py

# Expected output:
# ✅ 50 requests to /api/v1/matches
# ✅ Average response time < 0.2s
# ✅ Success rate > 95%
```

---

## 📊 COMMANDS CHEAT SHEET

### Testing

```bash
# Backend
cd backend
pytest                          # Run all tests
pytest -v                       # Verbose
pytest -k "test_matches"        # Run specific tests
pytest --cov=app                # With coverage

# Frontend
cd frontend
npm test                        # Run all tests
npm test -- --watch             # Watch mode
npm run test:coverage           # With coverage
```

### Docker

```bash
# Start
docker compose -f docker-compose.prod.yml up -d

# Stop
docker compose -f docker-compose.prod.yml down

# Rebuild
docker compose -f docker-compose.prod.yml up -d --build

# Logs
docker compose -f docker-compose.prod.yml logs -f [service]

# Shell access
docker compose -f docker-compose.prod.yml exec backend bash
docker compose -f docker-compose.prod.yml exec frontend sh

# Database
docker compose -f docker-compose.prod.yml exec postgres psql -U nashama -d nashama_vision

# Redis
docker compose -f docker-compose.prod.yml exec redis redis-cli
```

### Cleanup

```bash
# Stop services
docker compose -f docker-compose.prod.yml down

# Remove volumes (⚠️ deletes data)
docker compose -f docker-compose.prod.yml down -v

# Remove images
docker compose -f docker-compose.prod.yml down --rmi all

# Full cleanup
docker system prune -a --volumes
```

---

## 🔧 MINIMAL .env.prod

```bash
# Database
POSTGRES_DB=nashama_vision
POSTGRES_USER=nashama
POSTGRES_PASSWORD=change_this_password

# Security
SECRET_KEY=change_this_secret_key_at_least_32_chars_long
DEBUG=false
ALLOWED_ORIGINS=http://localhost,http://localhost:80

# LLM (use mock for testing)
LLM_PROVIDER=mock
LLM_API_KEY=not-required-for-mock
LLM_MODEL=mock-model

# Storage
STORAGE_TYPE=local

# Workers
WORKERS=4
```

---

## ✅ SUCCESS INDICATORS

### Tests Passing
- ✅ Backend: 55+ tests passed
- ✅ Frontend: 15+ tests passed
- ✅ No critical errors

### Deployment Working
- ✅ All 5 containers running
- ✅ Health checks passing
- ✅ Frontend accessible at http://localhost
- ✅ API docs at http://localhost:8000/docs
- ✅ No error logs

---

## 🐛 QUICK TROUBLESHOOTING

### Tests Fail

**Backend:**
```bash
# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Reinstall dependencies
pip install -r requirements.txt

# Run single test for debugging
pytest tests/test_api/test_matches_api.py::test_list_matches -v
```

**Frontend:**
```bash
# Clear node_modules
rm -rf node_modules package-lock.json
npm install

# Run single test
npm test AssistantChat
```

### Docker Issues

**Containers won't start:**
```bash
# Check logs
docker compose -f docker-compose.prod.yml logs backend

# Rebuild without cache
docker compose -f docker-compose.prod.yml build --no-cache

# Check ports aren't in use
netstat -ano | findstr :8000
netstat -ano | findstr :5432
```

**Database connection fails:**
```bash
# Verify postgres is healthy
docker compose -f docker-compose.prod.yml ps postgres

# Check connection
docker compose -f docker-compose.prod.yml exec backend python -c "from app.db.session import engine; print(engine.url)"

# Manual connection test
docker compose -f docker-compose.prod.yml exec postgres pg_isready -U nashama
```

**Frontend shows errors:**
```bash
# Check nginx config
docker compose -f docker-compose.prod.yml exec frontend nginx -t

# Check backend is accessible
curl http://localhost:8000/api/v1/matches

# View frontend logs
docker compose -f docker-compose.prod.yml logs frontend
```

---

## 📚 FULL DOCUMENTATION

For detailed information, see:
- **PHASE6_COMPLETE.md** - Comprehensive documentation
- **Backend tests/** - Test implementation details
- **Frontend src/__tests__/** - Component test examples
- **docker-compose.prod.yml** - Service configuration

---

## 🎉 YOU'RE DONE!

If tests pass and Docker is running, Phase 6 is complete! 🚀

**Next steps:**
1. Increase test coverage
2. Set up CI/CD
3. Configure production secrets
4. Add monitoring
5. Deploy to cloud

---

**Happy Testing & Deploying!** ✨
