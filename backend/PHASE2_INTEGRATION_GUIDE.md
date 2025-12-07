# Nashama Vision - Phase 2 Implementation Guide

## 📚 Table of Contents
1. [Overview](#overview)
2. [Backend Structure](#backend-structure)
3. [Database Setup](#database-setup)
4. [Backend Integration](#backend-integration)
5. [Frontend Setup](#frontend-setup)
6. [Testing the Implementation](#testing-the-implementation)
7. [API Reference](#api-reference)

---

## 🎯 Overview

Phase 2 adds comprehensive analytics capabilities to Nashama Vision:

- **Physical Metrics Engine**: Computes distance, speed, acceleration, sprints, stamina
- **Heatmap Generation**: Creates 2D spatial visualizations of player movement
- **Time Series Analytics**: Track metric evolution over match duration
- **React Dashboard**: Interactive UI for exploring analytics

---

## 📁 Backend Structure

### New Files Added

```
backend/
├── app/
│   ├── analytics/
│   │   ├── __init__.py           # Module exports
│   │   ├── models.py             # Analytics database models
│   │   ├── physical.py           # Physical metrics engine
│   │   ├── heatmap.py            # Heatmap generation engine
│   │   └── utils.py              # Utility functions
│   ├── api/
│   │   └── routers/
│   │       └── analytics/
│   │           ├── __init__.py
│   │           └── metrics.py    # Analytics API routes
│   └── schemas/
│       └── analytics_schemas.py  # Pydantic schemas for analytics
├── alembic/
│   └── versions/
│       └── 002_analytics_tables.py  # Database migration
```

---

## 🗄 Database Setup

### Step 1: Run Alembic Migration

```bash
cd backend

# Run the migration to create analytics tables
alembic upgrade head
```

This creates:
- `player_metrics` - Aggregate metrics per player
- `player_metric_timeseries` - Time series data
- `player_heatmaps` - Heatmap data
- `team_metrics` - Team-level metrics

### Step 2: Verify Tables

```sql
-- Connect to PostgreSQL
psql -U postgres -d nashama_vision

-- List new tables
\dt

-- Check player_metrics structure
\d player_metrics
```

---

## 🔧 Backend Integration

### Step 1: Update Requirements

Add to `requirements.txt`:

```txt
numpy>=1.24.0
scipy>=1.11.0
```

Install:

```bash
pip install -r requirements.txt
```

### Step 2: Verify Analytics Route Registration

The analytics router is already added to `app/main.py`:

```python
from app.api.routers.analytics import metrics_router
app.include_router(metrics_router, tags=["Analytics"])
```

### Step 3: Test Analytics Computation

The analytics task is automatically triggered after video processing completes.

To manually trigger:

```python
from app.workers.tasks import analytics_computation_task
from app.workers.celery_app import celery_app

# Trigger for a specific video
video_id = "your-video-uuid"
task = analytics_computation_task.delay(str(video_id))
```

### Step 4: Start Services

```bash
# Terminal 1: Start Redis
docker run -d -p 6379:6379 redis

# Terminal 2: Start PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres

# Terminal 3: Start Celery Worker
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 4: Start FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🎨 Frontend Setup

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

### Step 2: Configure API URL

Create `.env` file:

```env
REACT_APP_API_URL=http://localhost:8000
```

### Step 3: Start Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Step 4: Build for Production

```bash
npm run build
```

---

## 🧪 Testing the Implementation

### Backend API Tests

#### 1. Get Match Analytics

```bash
curl http://localhost:8000/api/v1/analytics/matches/{match_id}
```

Expected response:

```json
{
  "match_id": "uuid",
  "match_name": "Match Name",
  "video_id": "uuid",
  "total_players": 20,
  "home_players": 11,
  "away_players": 9,
  "total_distance_covered_km": 250.5,
  "avg_speed_kmh": 15.3,
  "max_speed_kmh": 32.8,
  "total_sprints": 145
}
```

#### 2. Get Player Metrics

```bash
curl http://localhost:8000/api/v1/analytics/players/{player_id}/metrics?match_id={match_id}
```

Expected response:

```json
{
  "player_id": "uuid",
  "track_id": 5,
  "object_class": "player",
  "team_side": "home",
  "total_distance_km": 12.5,
  "avg_speed_kmh": 15.2,
  "top_speed_kmh": 32.1,
  "high_intensity_distance_m": 2450,
  "sprint_count": 8,
  "max_acceleration_mps2": 4.2,
  "max_deceleration_mps2": -3.8,
  "stamina_index": 78.5
}
```

#### 3. Get Player Heatmap

```bash
curl http://localhost:8000/api/v1/analytics/players/{player_id}/heatmap?match_id={match_id}
```

Expected response:

```json
{
  "id": "uuid",
  "player_id": "uuid",
  "match_id": "uuid",
  "video_id": "uuid",
  "grid_width": 40,
  "grid_height": 25,
  "heatmap_data": [[0.1, 0.2, ...], ...],
  "pitch_length": 105.0,
  "pitch_width": 68.0,
  "total_positions": 5432,
  "max_intensity": 1.0
}
```

#### 4. Get Time Series Data

```bash
curl http://localhost:8000/api/v1/analytics/players/{player_id}/timeseries/speed?match_id={match_id}
```

Expected response:

```json
{
  "player_id": "uuid",
  "match_id": "uuid",
  "metric_type": "speed",
  "data_points": [
    {"timestamp": 0.5, "value": 5.2, "unit": "m/s"},
    {"timestamp": 1.0, "value": 6.8, "unit": "m/s"},
    ...
  ]
}
```

### Frontend Navigation Flow

1. **Match Details**: `/matches/{match_id}`
   - Shows match overview
   - Lists players by team
   - Quick action buttons

2. **Player Metrics**: `/matches/{match_id}/player/{player_id}/metrics`
   - Displays aggregate metrics cards
   - Shows speed over time chart
   - Shows stamina curve
   - Shows acceleration profile

3. **Heatmap View**: `/matches/{match_id}/player/{player_id}/heatmap`
   - Renders interactive pitch with heatmap overlay
   - Toggle between player and team heatmaps
   - Player/team selector dropdown

---

## 📖 API Reference

### Match Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/matches/{match_id}` | Get match analytics summary |
| GET | `/api/v1/analytics/matches/{match_id}/players` | List all players in match |

### Player Metrics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/players/{player_id}/metrics` | Get player metrics summary |
| GET | `/api/v1/analytics/players/{player_id}/metrics/all` | Get all detailed metrics |
| GET | `/api/v1/analytics/players/{player_id}/timeseries/{metric_type}` | Get time series data |

**Metric Types**: `speed`, `acceleration`, `stamina`, `distance_rolling`

### Heatmap Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/players/{player_id}/heatmap` | Get player heatmap |
| GET | `/api/v1/analytics/matches/{match_id}/heatmap/team/{team_side}` | Get team heatmap |

**Team Sides**: `home`, `away`

### Team Metrics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/teams/{team_side}/metrics` | Get team metrics |

---

## 🔍 Key Metrics Explained

### Physical Metrics

- **Total Distance**: Sum of all point-to-point movements in meters
- **Top Speed**: Maximum instantaneous speed recorded
- **Average Speed**: Mean speed across all movements
- **High Intensity Distance**: Distance covered above 5.5 m/s (~19.8 km/h)
- **Sprint Count**: Number of sustained runs above 7.0 m/s (~25.2 km/h)
- **Stamina Index**: 0-100 scale measuring performance consistency

### Time Series Metrics

- **Speed**: Instantaneous velocity at each timestamp
- **Acceleration**: Rate of change in speed
- **Stamina**: Rolling average speed over 60-second window

---

## 🚀 Integration Workflow

### Complete End-to-End Flow

1. **Upload Video**
   ```bash
   POST /api/v1/videos/upload/{match_id}
   ```

2. **Video Processing** (Automatic via Celery)
   - Frame extraction
   - Object detection (YOLO)
   - Multi-object tracking (DeepSORT)
   - Track points saved to DB

3. **Analytics Computation** (Automatic via Celery)
   - Physical metrics calculation
   - Heatmap generation
   - Time series creation
   - Results saved to DB

4. **View Analytics** (Frontend)
   - Navigate to match page
   - Select player
   - View metrics, charts, heatmaps

---

## 🎛 Configuration

### Analytics Engine Configuration

Edit thresholds in `app/analytics/physical.py`:

```python
class PhysicalMetricsEngine:
    HIGH_INTENSITY_THRESHOLD_MPS = 5.5  # ~19.8 km/h
    SPRINT_THRESHOLD_MPS = 7.0  # ~25.2 km/h
    SPRINT_MIN_DURATION = 1.0  # seconds
    STAMINA_WINDOW_SIZE = 60  # seconds
```

### Heatmap Configuration

Edit in `app/analytics/heatmap.py`:

```python
@dataclass
class HeatmapConfig:
    pitch_length: float = 105.0  # meters
    pitch_width: float = 68.0  # meters
    grid_width: int = 40  # horizontal bins
    grid_height: int = 25  # vertical bins
    smoothing_sigma: float = 1.0  # Gaussian smoothing
```

---

## 🐛 Troubleshooting

### Issue: No metrics computed

**Cause**: Track points missing metric coordinates (x_m, y_m)

**Solution**: Ensure pitch calibration runs before analytics computation

### Issue: Heatmap not displaying

**Cause**: Frontend canvas rendering issue

**Solution**: Check browser console for errors, verify heatmap data format

### Issue: Time series data missing

**Cause**: Analytics task not triggered

**Solution**: Manually trigger task or check Celery worker logs

---

## 📈 Performance Optimization

### Database Indexing

The migration includes indexes on:
- `player_id + match_id`
- `player_id + timestamp`
- `match_id`

### Query Optimization

Use `LIMIT` for large time series:

```python
timeseries = (
    db.query(PlayerMetricTimeSeries)
    .filter(PlayerMetricTimeSeries.player_id == player_id)
    .order_by(PlayerMetricTimeSeries.timestamp)
    .limit(1000)  # Limit results
    .all()
)
```

### Caching

Consider adding Redis caching for frequently accessed metrics:

```python
from redis import Redis
import json

redis_client = Redis(host='localhost', port=6379)

def get_cached_metrics(player_id):
    key = f"metrics:{player_id}"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None
```

---

## 🎓 Next Steps

### Phase 3 Enhancements

1. **Advanced Tactical Metrics**
   - Formation detection
   - Pressing intensity
   - Team compactness

2. **Expected Threat (xT)**
   - Grid-based threat model
   - Pass detection
   - Action valuation

3. **Virtual Match Engine**
   - 2D replay using Konva.js
   - 3D visualization using Three.js
   - Timeline controls

4. **AI Assistant**
   - Natural language queries
   - Automated insights
   - Report generation

---

## 📞 Support

For issues or questions:
- Check logs: `backend/logs/`
- Review API docs: `http://localhost:8000/api/docs`
- Inspect database: `psql -U postgres -d nashama_vision`

---

**Phase 2 Implementation Complete! ✅**
