# 🧪 PHASE 6 - TESTING & DEPLOYMENT

## Complete Implementation Guide

---

## Overview

Phase 6 adds **production-ready testing infrastructure** and **Docker-based deployment** to Nashama Vision, ensuring code quality and streamlined deployment.

---

## 🎯 What Was Delivered

### 1. Backend Testing Suite (Pytest)
✅ **Test Infrastructure**
- In-memory SQLite test database
- Comprehensive fixtures for all data types
- FastAPI TestClient integration
- Mock LLM client for assistant testing

✅ **API Tests** (4 test files, 30+ tests)
- Matches API
- Analytics API (Physical, xT, Tactical, Events)
- Replay API
- Assistant API

✅ **Service/Engine Tests** (6 test files, 25+ tests)
- Physical metrics engine
- Heatmap generation
- Tactical engine (formation detection)
- xT engine
- Events engine
- Assistant service

### 2. Frontend Testing Suite (Vitest)
✅ **Test Infrastructure**
- Vitest + React Testing Library
- jsdom environment
- Mock utilities for API calls

✅ **Component Tests** (4 test files, 15+ tests)
- AssistantChat component
- AssistantPage component
- MatchReplayView component
- PlayerMetricsView component

### 3. Production Docker Setup
✅ **Backend Dockerfile**
- Python 3.11 slim base
- Gunicorn + Uvicorn workers
- Health checks
- Optimized layers

✅ **Frontend Dockerfile**
- Multi-stage build (Node + Nginx)
- Optimized bundle
- Custom nginx config
- Health checks

✅ **Docker Compose**
- Complete production stack
- PostgreSQL + Redis
- Backend + Worker + Frontend
- Volume management
- Network isolation

### 4. Performance Testing
✅ **Load Testing Script**
- Async HTTP client
- Configurable request count
- Response time statistics
- Error tracking

---

## 📂 File Structure

```
nashamavision/
├── backend/
│   ├── Dockerfile.prod                    # NEW - Production backend image
│   └── tests/
│       ├── __init__.py                    # NEW
│       ├── conftest.py                    # NEW - Pytest fixtures
│       ├── performance_test.py            # NEW - Load testing
│       ├── test_api/
│       │   ├── __init__.py
│       │   ├── test_matches_api.py        # NEW
│       │   ├── test_analytics_api.py      # NEW
│       │   ├── test_replay_api.py         # NEW
│       │   └── test_assistant_api.py      # NEW
│       └── test_services/
│           ├── __init__.py
│           ├── test_physical_metrics.py   # NEW
│           ├── test_heatmaps.py           # NEW
│           ├── test_tactical_engine.py    # NEW
│           ├── test_xt_engine.py          # NEW
│           ├── test_events_engine.py      # NEW
│           └── test_assistant_service.py  # NEW
│
├── frontend/
│   ├── Dockerfile.prod                    # NEW - Production frontend image
│   ├── nginx.conf                         # NEW - Nginx configuration
│   ├── vitest.config.js                   # NEW - Vitest configuration
│   ├── package.json                       # MODIFIED - Added test scripts
│   └── src/
│       ├── test/
│       │   └── setup.js                   # NEW - Test setup
│       └── __tests__/
│           ├── AssistantChat.test.jsx     # NEW
│           ├── AssistantPage.test.jsx     # NEW
│           ├── MatchReplayView.test.jsx   # NEW
│           └── PlayerMetricsView.test.jsx # NEW
│
├── docker-compose.prod.yml                # NEW - Production stack
├── .env.prod.example                      # NEW - Environment template
└── PHASE6_COMPLETE.md                     # NEW - This file
```

---

## 🧪 BACKEND TESTING

### Setup

```bash
cd backend

# Install test dependencies (if not already in requirements.txt)
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api/test_matches_api.py

# Run with coverage
pytest --cov=app --cov-report=html
```

### Test Fixtures

All fixtures are defined in `tests/conftest.py`:

- `db_engine` - In-memory SQLite engine
- `db_session` - Database session
- `client` - FastAPI test client
- `sample_match` - Sample match data
- `sample_players` - 22 players (11 home, 11 away)
- `sample_tracks` - Tracking data
- `sample_metrics` - Physical metrics
- `sample_heatmap` - Heatmap data
- `sample_tactical_snapshot` - Tactical data
- `sample_xt_metrics` - xT metrics
- `sample_events` - Event data
- `mock_llm_config` - Mock LLM configuration

### Example Test

```python
def test_list_matches(client: TestClient, sample_match):
    """Test GET /api/v1/matches"""
    response = client.get("/api/v1/matches")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == sample_match.id
```

### Running Tests

```bash
# Quick run (quiet mode)
pytest -q

# With coverage
pytest --cov=app

# Stop on first failure
pytest -x

# Run only failed tests from last run
pytest --lf

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

---

## 🎨 FRONTEND TESTING

### Setup

```bash
cd frontend

# Install dependencies
npm install

# Run tests
npm test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

### Test Structure

Tests use:
- **Vitest** - Fast unit test framework
- **React Testing Library** - Component testing
- **@testing-library/jest-dom** - DOM assertions
- **@testing-library/user-event** - User interactions

### Example Test

```javascript
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AssistantChat from '../components/assistant/AssistantChat';

it('renders chat interface', () => {
  const queryClient = new QueryClient();
  
  render(
    <QueryClientProvider client={queryClient}>
      <AssistantChat matchId="test-match-id" />
    </QueryClientProvider>
  );

  expect(screen.getByRole('textbox')).toBeInTheDocument();
});
```

### Running Tests

```bash
# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run specific file
npm test AssistantChat

# Run with coverage
npm run test:coverage

# Update snapshots
npm test -- -u
```

---

## 🚀 DOCKER DEPLOYMENT

### Production Build

#### 1. Prepare Environment

```bash
# Copy example env file
cp .env.prod.example .env.prod

# Edit with your values
nano .env.prod
```

Required variables:
```bash
POSTGRES_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key_min_32_chars
LLM_PROVIDER=openai  # or anthropic, local, mock
LLM_API_KEY=sk-your-api-key
ALLOWED_ORIGINS=http://your-domain.com
```

#### 2. Build and Run

```bash
# Build all images
docker compose -f docker-compose.prod.yml build

# Start all services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker compose -f docker-compose.prod.yml logs -f backend
```

#### 3. Initialize Database

```bash
# Run migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create initial data (if needed)
docker compose -f docker-compose.prod.yml exec backend python -m app.scripts.seed_data
```

#### 4. Access Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

#### 5. Stop and Cleanup

```bash
# Stop all services
docker compose -f docker-compose.prod.yml down

# Stop and remove volumes (WARNING: deletes data)
docker compose -f docker-compose.prod.yml down -v

# Remove images
docker compose -f docker-compose.prod.yml down --rmi all
```

### Services

The production stack includes:

1. **postgres** - PostgreSQL 15 database
   - Port: 5432
   - Volume: `postgres_data`
   - Health check: `pg_isready`

2. **redis** - Redis 7 cache/broker
   - Port: 6379
   - Volume: `redis_data`
   - Health check: `redis-cli ping`

3. **backend** - FastAPI application
   - Port: 8000
   - 4 Gunicorn workers
   - Uvicorn async workers
   - Volumes: storage, logs, models

4. **worker** - Celery worker
   - 2 concurrent workers
   - Processes video uploads
   - Runs analytics tasks

5. **frontend** - React app (Nginx)
   - Port: 80
   - Serves static files
   - Proxies `/api/` to backend

### Scaling

```bash
# Scale workers
docker compose -f docker-compose.prod.yml up -d --scale worker=4

# Scale backend (requires load balancer)
docker compose -f docker-compose.prod.yml up -d --scale backend=3
```

---

## ⚡ PERFORMANCE TESTING

### Running Load Tests

```bash
cd backend

# Ensure backend is running
# Run performance test
python tests/performance_test.py
```

### Test Scenarios

The script tests:
1. List matches (50 requests)
2. Get match by ID (25 requests)
3. Get metrics (25 requests)
4. Get replay timeline (25 requests)
5. Assistant query (20 requests)

### Sample Output

```
============================================================
Testing: GET /api/v1/matches
Requests: 50
============================================================

Results:
  Success Rate: 100.0%
  Successful: 50 | Failed: 0

Response Times (seconds):
  Average: 0.125s
  Median:  0.120s
  Min:     0.095s
  Max:     0.180s
  P95:     0.165s

============================================================
SUMMARY
============================================================

Endpoint                                           Success %    Avg (s)
------------------------------------------------------------------------
GET /api/v1/matches                                   100.0%       0.125s
GET /api/v1/matches/{id}                               98.0%       0.145s
GET /api/v1/metrics/match/{id}                        100.0%       0.210s
GET /api/v1/replay/match/{id}/timeline                100.0%       0.450s
POST /api/v1/assistant/query                          100.0%       1.250s
```

### Customizing Tests

Edit `tests/performance_test.py`:

```python
# Change number of requests
NUM_REQUESTS = 100

# Change timeout
TIMEOUT = 60.0

# Add custom test
{
    "endpoint": "/api/v1/custom",
    "method": "POST",
    "payload": {"key": "value"},
    "num_requests": 30
}
```

---

## 🔒 SECURITY BEST PRACTICES

### Production Checklist

- [ ] Change default passwords
- [ ] Generate secure SECRET_KEY (32+ chars)
- [ ] Set DEBUG=false
- [ ] Configure ALLOWED_ORIGINS
- [ ] Use HTTPS (reverse proxy)
- [ ] Set up rate limiting
- [ ] Enable firewall
- [ ] Regular backups
- [ ] Monitor logs
- [ ] Update dependencies

### Environment Variables

**Never commit:**
- API keys (LLM_API_KEY)
- Database passwords
- Secret keys
- Production configs

**Always use:**
- `.env.prod` (gitignored)
- Environment-specific files
- Secrets management (Docker secrets, Vault, etc.)

### Nginx Security Headers

Already configured in `frontend/nginx.conf`:
```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
```

---

## 📊 CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && pytest

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: cd frontend && npm install
      - run: cd frontend && npm test
```

---

## 🐛 Troubleshooting

### Backend Tests Fail

**Issue**: Import errors
```bash
# Add backend to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

**Issue**: Database errors
```bash
# Test database setup
pytest tests/conftest.py::test_db_connection -v
```

### Frontend Tests Fail

**Issue**: Module not found
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Issue**: Canvas/Konva errors
```bash
# Mock canvas in tests (already in setup.js)
# Ensure vitest.config.js has environment: 'jsdom'
```

### Docker Issues

**Issue**: Build fails
```bash
# Clear Docker cache
docker builder prune -a

# Rebuild without cache
docker compose -f docker-compose.prod.yml build --no-cache
```

**Issue**: Services won't start
```bash
# Check logs
docker compose -f docker-compose.prod.yml logs backend

# Check health
docker compose -f docker-compose.prod.yml ps
```

**Issue**: Database connection fails
```bash
# Verify database is ready
docker compose -f docker-compose.prod.yml exec postgres pg_isready

# Check environment variables
docker compose -f docker-compose.prod.yml exec backend env | grep DATABASE
```

---

## 📈 Monitoring

### Health Checks

All services have health checks:

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost/health

# Database
docker compose -f docker-compose.prod.yml exec postgres pg_isready

# Redis
docker compose -f docker-compose.prod.yml exec redis redis-cli ping
```

### Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100

# Since specific time
docker compose -f docker-compose.prod.yml logs --since 2024-01-01T12:00:00
```

### Metrics

Consider adding:
- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **Sentry** - Error tracking
- **ELK Stack** - Log aggregation

---

## 🎯 Testing Best Practices

### Backend

1. **Test Coverage**
   - Aim for 80%+ coverage
   - Focus on business logic
   - Test edge cases

2. **Test Isolation**
   - Each test independent
   - Clean fixtures
   - No shared state

3. **Mock External Services**
   - LLM providers
   - External APIs
   - File system (when appropriate)

### Frontend

1. **User-Centric Tests**
   - Test user interactions
   - Avoid implementation details
   - Use accessible queries

2. **Mock API Calls**
   - Mock React Query hooks
   - Consistent test data
   - Error states

3. **Component Focus**
   - One component per test file
   - Test props and states
   - Snapshot sparingly

---

## 📝 Additional Configuration

### pytest.ini

Create `backend/pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

### .dockerignore

Create `backend/.dockerignore`:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.pytest_cache/
.coverage
htmlcov/
*.log
.env
.env.*
tests/
```

Create `frontend/.dockerignore`:

```
node_modules/
npm-debug.log*
.git/
.gitignore
.env*
*.md
tests/
__tests__/
.vscode/
```

---

## ✅ Phase 6 Checklist

### Testing
- [x] Backend test infrastructure (pytest + fixtures)
- [x] Backend API tests (30+ tests)
- [x] Backend service tests (25+ tests)
- [x] Frontend test infrastructure (vitest)
- [x] Frontend component tests (15+ tests)
- [x] Performance testing script

### Deployment
- [x] Backend production Dockerfile
- [x] Frontend production Dockerfile
- [x] Nginx configuration
- [x] Docker Compose production stack
- [x] Environment variable template
- [x] Health checks for all services

### Documentation
- [x] Testing guide
- [x] Deployment guide
- [x] Troubleshooting guide
- [x] Security best practices
- [x] CI/CD examples

---

## 🎉 Summary

Phase 6 successfully adds:

1. **Comprehensive Testing**
   - 55+ backend tests
   - 15+ frontend tests
   - Performance testing
   - High test coverage

2. **Production Deployment**
   - Docker containerization
   - Multi-service orchestration
   - Health monitoring
   - Scalable architecture

3. **Developer Experience**
   - Easy test execution
   - Clear documentation
   - Troubleshooting guides
   - CI/CD ready

**Result:** Nashama Vision is now production-ready with robust testing and streamlined deployment! 🚀

---

## 📖 Next Steps

### Phase 7 Ideas
- [ ] Kubernetes deployment
- [ ] Advanced monitoring (Prometheus/Grafana)
- [ ] E2E testing (Playwright/Cypress)
- [ ] Load balancer configuration
- [ ] CDN integration
- [ ] Auto-scaling policies

### Immediate Improvements
- [ ] Increase test coverage to 90%+
- [ ] Add integration tests with real database
- [ ] Set up CI/CD pipeline
- [ ] Configure production secrets management
- [ ] Add backup/restore procedures
- [ ] Performance profiling

---

**Phase 6 is complete and production-ready!** ✅
