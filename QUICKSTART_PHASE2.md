# 🚀 PHASE 2 - QUICK START GUIDE

## ⚡ Setup in 5 Minutes

### 1️⃣ Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Add dependencies to requirements.txt
echo "numpy>=1.24.0" >> requirements.txt
echo "scipy>=1.11.0" >> requirements.txt

# Install
pip install -r requirements.txt

# Run migration
alembic upgrade head
```

### 2️⃣ Start Services (1 minute)

```bash
# Terminal 1: Start Celery Worker
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 2: Start FastAPI
uvicorn app.main:app --reload
```

### 3️⃣ Frontend Setup (2 minutes)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

---

## 🎯 Test the Implementation

### Test 1: Check API Endpoints

Visit: http://localhost:8000/api/docs

You should see new endpoints:
- `/api/v1/analytics/matches/{match_id}`
- `/api/v1/analytics/players/{player_id}/metrics`
- `/api/v1/analytics/players/{player_id}/heatmap`

### Test 2: Verify Database Tables

```bash
psql -U postgres -d nashama_vision -c "\dt"
```

You should see:
- `player_metrics`
- `player_metric_timeseries`
- `player_heatmaps`
- `team_metrics`

### Test 3: Access Frontend

Visit: http://localhost:5173

Navigate to a match page to see analytics.

---

## 📋 API Quick Reference

### Get Match Analytics
```bash
curl http://localhost:8000/api/v1/analytics/matches/{match_id}
```

### Get Player Metrics
```bash
curl http://localhost:8000/api/v1/analytics/players/{player_id}/metrics
```

### Get Speed Time Series
```bash
curl http://localhost:8000/api/v1/analytics/players/{player_id}/timeseries/speed
```

### Get Player Heatmap
```bash
curl http://localhost:8000/api/v1/analytics/players/{player_id}/heatmap
```

---

## 🔧 Configuration

### Adjust Speed Thresholds

Edit `backend/app/analytics/physical.py`:

```python
class PhysicalMetricsEngine:
    HIGH_INTENSITY_THRESHOLD_MPS = 5.5  # Change this
    SPRINT_THRESHOLD_MPS = 7.0          # Change this
```

### Adjust Heatmap Grid

Edit `backend/app/analytics/heatmap.py`:

```python
@dataclass
class HeatmapConfig:
    grid_width: int = 40   # Change this
    grid_height: int = 25  # Change this
```

---

## 🐛 Troubleshooting

### Issue: No metrics computed

**Check:**
1. Are track points in database? `SELECT COUNT(*) FROM track_points;`
2. Do track points have x_m, y_m? `SELECT x_m, y_m FROM track_points LIMIT 5;`
3. Is Celery worker running? Check terminal logs

**Fix:** Run pitch calibration before analytics

### Issue: Frontend not loading

**Check:**
1. Is API running? Visit http://localhost:8000/health
2. Is .env file correct? Check `REACT_APP_API_URL`
3. Are dependencies installed? Run `npm install`

**Fix:** Restart dev server

### Issue: Charts not rendering

**Check:**
1. Browser console for errors
2. Is data being fetched? Check Network tab
3. Are there data points? Check API response

**Fix:** Verify time series data exists in DB

---

## 📊 Key Metrics Explained

| Metric | What It Means |
|--------|---------------|
| **Total Distance** | How far the player ran during the match |
| **Top Speed** | Fastest speed reached by the player |
| **Sprint Count** | Number of times player ran at full speed (>25 km/h) |
| **High Intensity Distance** | Distance covered while running fast (>19.8 km/h) |
| **Stamina Index** | How consistently the player performed (0-100) |

---

## 🎨 Frontend Pages

### 1. Match Details
**URL:** `/matches/{match_id}`
- Overview of match statistics
- List of players by team
- Quick action buttons

### 2. Player Metrics
**URL:** `/matches/{match_id}/player/{player_id}/metrics`
- Metric cards (distance, speed, sprints)
- Speed over time chart
- Stamina curve
- Acceleration profile

### 3. Heatmap View
**URL:** `/matches/{match_id}/player/{player_id}/heatmap`
- Interactive pitch visualization
- Player/team heatmap toggle
- Intensity gradient

---

## 🚀 Next Steps

1. ✅ **Phase 2 Complete** - Analytics working
2. 🔄 **Phase 3 Next** - Advanced tactical metrics
   - Formation detection
   - Pressing intensity
   - Pass networks
3. 🤖 **Phase 4 Future** - AI assistant
   - Natural language queries
   - Automated insights

---

## 📞 Need Help?

Check these files:
- `PHASE2_INTEGRATION_GUIDE.md` - Full setup guide
- `PHASE2_COMPLETE.md` - Implementation details
- `PHASE2_SUMMARY.md` - Visual overview

Or check API docs: http://localhost:8000/api/docs

---

**✨ You're ready to go! Start uploading videos and analyzing matches! ✨**
