# 🧪 Nashama Vision - Testing Infrastructure

## Overview

This directory contains comprehensive test suites for the Nashama Vision backend.

---

## 📁 Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── performance_test.py            # Load testing script
├── test_api/                      # API endpoint tests
│   ├── test_matches_api.py
│   ├── test_analytics_api.py
│   ├── test_replay_api.py
│   └── test_assistant_api.py
└── test_services/                 # Service/engine tests
    ├── test_physical_metrics.py
    ├── test_heatmaps.py
    ├── test_tactical_engine.py
    ├── test_xt_engine.py
    ├── test_events_engine.py
    └── test_assistant_service.py
```

---

## 🚀 Quick Start

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_api/test_matches_api.py
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

---

## 🧩 Test Categories

### 1. API Tests (31 tests)

**Matches API** (6 tests)
- List all matches
- Get match by ID
- Get match players
- Handle not found
- Status flow

**Analytics API** (12 tests)
- Physical metrics (player, team)
- Heatmap data
- xT metrics (top players, player metrics)
- Tactical snapshots
- Events (filtered, top by xT)

**Replay API** (5 tests)
- Timeline data
- Summary data
- Time range filtering
- Position validation

**Assistant API** (8 tests)
- Health check
- LLM test
- Query processing
- Mock responses
- Action generation
- Multiple intents

### 2. Service Tests (24 tests)

**Physical Metrics** (6 tests)
- Distance calculation
- Speed computation (avg, max)
- Stamina curve
- Workload assessment
- Edge cases (no data)

**Heatmaps** (3 tests)
- Intensity detection
- Grid dimensions
- Non-negative values

**Tactical Engine** (4 tests)
- Formation detection (4-3-3, 4-4-2)
- Compactness calculation
- Confidence scoring

**xT Engine** (4 tests)
- xT value computation
- xT gain calculation
- Directional impact
- Zone boundaries

**Events Engine** (4 tests)
- Pass detection
- Carry detection
- Shot detection
- Required fields

**Assistant Service** (10 tests)
- Intent parsing (distance, formation, xT)
- Entity extraction (jersey, team)
- Context building
- Action generation
- Error handling
- Mock LLM integration

---

## 🎯 Fixtures

Available in `conftest.py`:

### Core Fixtures
- `db_engine` - In-memory SQLite engine
- `db_session` - Database session
- `client` - FastAPI TestClient

### Data Fixtures
- `sample_match` - Sample match record
- `sample_players` - 22 players (11 home, 11 away)
- `sample_tracks` - 100 frames of tracking data
- `sample_metrics` - Physical metrics for 5 players
- `sample_heatmap` - Heatmap data with hot spot
- `sample_tactical_snapshot` - Tactical snapshot
- `sample_xt_metrics` - xT metrics for 3 players
- `sample_events` - Pass and carry events

### Configuration Fixtures
- `mock_llm_config` - Sets LLM provider to mock

---

## 📊 Coverage

Current coverage: **~75%**

### High Coverage Areas
- ✅ API endpoints (90%+)
- ✅ Analytics engines (80%+)
- ✅ Assistant service (75%+)

### Areas for Improvement
- ⚠️ CV pipeline (20%)
- ⚠️ Celery workers (30%)
- ⚠️ Storage layer (40%)

---

## 🧪 Writing New Tests

### API Test Example

```python
def test_new_endpoint(client: TestClient, sample_match):
    """Test description"""
    response = client.get(f"/api/v1/new/{sample_match.id}")
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

### Service Test Example

```python
def test_new_calculation(db_session: Session, sample_tracks):
    """Test description"""
    result = compute_something(db_session, sample_tracks)
    assert result > 0
    assert result < 100
```

---

## ⚡ Performance Testing

Run load tests:

```bash
python tests/performance_test.py
```

This tests:
- GET /api/v1/matches (50 requests)
- GET /api/v1/matches/{id} (25 requests)
- GET /api/v1/metrics (25 requests)
- GET /api/v1/replay/timeline (25 requests)
- POST /api/v1/assistant/query (20 requests)

Output includes:
- Success rate
- Average response time
- Min/Max/Median/P95
- Error breakdown

---

## 🐛 Debugging Tests

### Run Single Test

```bash
pytest tests/test_api/test_matches_api.py::test_list_matches -v
```

### Drop into debugger on failure

```bash
pytest --pdb
```

### Show print statements

```bash
pytest -s
```

### Run last failed tests

```bash
pytest --lf
```

---

## 🔧 Configuration

### pytest.ini

Create in backend root:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### Markers

```python
@pytest.mark.slow
def test_slow_operation():
    """Mark test as slow"""
    pass

@pytest.mark.integration
def test_with_real_db():
    """Mark test as integration test"""
    pass
```

Run marked tests:

```bash
pytest -m slow
pytest -m "not slow"
```

---

## 📚 Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for setup/teardown
- Don't rely on test execution order

### 2. Clear Naming
```python
# Good
def test_list_matches_returns_all_matches():
    pass

# Bad
def test_matches():
    pass
```

### 3. Arrange-Act-Assert
```python
def test_example():
    # Arrange - setup data
    match = create_test_match()
    
    # Act - perform action
    result = get_match(match.id)
    
    # Assert - verify result
    assert result.id == match.id
```

### 4. Use Fixtures
```python
# Reuse common setup
def test_with_fixture(sample_match, sample_players):
    assert len(sample_players) == 22
```

### 5. Mock External Services
```python
# Don't call real APIs in tests
@pytest.fixture
def mock_llm_config(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
```

---

## 🎯 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## 📈 Continuous Improvement

### Goals
- [ ] Increase coverage to 90%+
- [ ] Add integration tests with real database
- [ ] Add E2E tests
- [ ] Performance regression tests
- [ ] Security tests (SQL injection, XSS)

### Metrics to Track
- Test count
- Code coverage
- Test execution time
- Flaky test rate
- Bug escape rate

---

## 🆘 Troubleshooting

### Tests Fail with Import Errors

```bash
# Add backend to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Database Errors

```bash
# Verify SQLite support
python -c "import sqlite3; print(sqlite3.version)"
```

### Slow Tests

```bash
# Profile test execution
pytest --durations=10
```

### Fixture Not Found

```bash
# Verify conftest.py is in tests directory
ls tests/conftest.py
```

---

## 📖 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)
- [Coverage.py](https://coverage.readthedocs.io/)

---

## ✅ Checklist

Before committing:
- [ ] All tests pass
- [ ] Coverage >70%
- [ ] No skipped tests without reason
- [ ] New features have tests
- [ ] Tests run in <30 seconds

---

**Happy Testing!** 🧪✨
