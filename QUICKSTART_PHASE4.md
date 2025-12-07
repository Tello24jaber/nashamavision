# 🚀 PHASE 4 - QUICK START GUIDE

## Virtual Match Engine (2D Tactical Replay)

This guide will help you get Phase 4 up and running quickly.

---

## Prerequisites

Before starting Phase 4, ensure:
- ✅ Phase 1-3 are complete and working
- ✅ At least one match has been processed with tracking data
- ✅ Track points have metric coordinates (x_m, y_m) populated
- ✅ Events have been detected (Phase 3)
- ✅ PostgreSQL, Redis, and Celery are running

---

## Backend Setup (5 minutes)

### 1. Router is Already Integrated

The replay router is automatically included in `app/main.py`. No additional setup needed.

### 2. Verify Installation

Start the backend:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check the API documentation:
```
http://localhost:8000/docs
```

You should see three new endpoints under "Replay":
- `GET /api/v1/replay/match/{match_id}/summary`
- `GET /api/v1/replay/match/{match_id}/timeline`
- `GET /api/v1/replay/pitch/dimensions`

---

## Frontend Setup (5 minutes)

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This will install:
- `react-konva` (^18.2.10) - React wrapper for Konva
- `konva` (^9.2.3) - Canvas rendering library

### 2. Start Development Server

```bash
npm run dev
```

Frontend should start at:
```
http://localhost:5173
```

---

## Testing the Replay (10 minutes)

### 1. Find a Processed Match

Get a list of matches:
```bash
curl http://localhost:8000/api/v1/matches
```

Pick a match ID that has been fully processed (Phase 1-3 complete).

### 2. Test the API

Test replay summary:
```bash
curl http://localhost:8000/api/v1/replay/match/{YOUR_MATCH_ID}/summary
```

Expected response:
```json
{
  "match_id": "...",
  "match_name": "...",
  "home_team": "...",
  "away_team": "...",
  "duration": 5400.0,
  "players": [...],
  "segments": [...],
  "total_events": 123
}
```

Test replay timeline (first 60 seconds):
```bash
curl "http://localhost:8000/api/v1/replay/match/{YOUR_MATCH_ID}/timeline?fps=10&start_time=0&end_time=60"
```

### 3. Open the Replay Page

Navigate to:
```
http://localhost:5173/matches/{YOUR_MATCH_ID}/replay
```

You should see:
- Green football pitch with markings
- Players as colored circles
- Ball as white circle (if tracked)
- Playback controls at bottom
- Sidebar with player list and events on the right

### 4. Interact with the Replay

**Basic Controls:**
- Click **Play** button to start animation
- Drag the **timeline slider** to seek
- Click **speed buttons** to change playback speed (0.25x - 4x)
- Use **skip forward/backward** buttons

**Player Interaction:**
- Click a player in the sidebar to highlight them
- Highlighted player will have a white border and show trail
- Click again to deselect

**Event Interaction:**
- Events appear as colored arrows:
  - **Blue** = Pass
  - **Yellow** = Carry
  - **Red** = Shot
- Click an event in the sidebar to jump to that time
- xT gain is displayed above the arrow

**View Options:**
- Toggle "Show Ball Trail" to see ball movement
- Toggle "Debug Mode" to see track IDs and technical info

---

## Common Setup Issues

### Issue: "Cannot find module 'react-konva'"

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: "No players visible on pitch"

**Possible causes:**
1. Match has no tracking data
2. Track points missing metric coordinates
3. API returning empty player array

**Debug:**
```bash
# Check if tracks exist
curl http://localhost:8000/api/v1/tracks/video/{VIDEO_ID}

# Check timeline API response
curl http://localhost:8000/api/v1/replay/match/{MATCH_ID}/timeline?fps=10
```

### Issue: "Events not showing"

**Possible causes:**
1. Phase 3 events not computed
2. Events table empty for this match

**Debug:**
```bash
# Check events via Phase 3 API
curl http://localhost:8000/api/v1/events/match/{MATCH_ID}
```

### Issue: "Replay page shows loading forever"

**Possible causes:**
1. Backend not running
2. API error (check browser console)
3. Match ID invalid

**Debug:**
1. Open browser DevTools (F12)
2. Check Network tab for failed requests
3. Check Console tab for errors
4. Verify backend is running: `curl http://localhost:8000/health`

---

## Minimal Test Data Requirements

For Phase 4 to work, you need:

1. **Match record** in database
2. **Video record** linked to match
3. **Track records** (players + ball)
4. **TrackPoint records** with:
   - `x_m` and `y_m` populated (metric coordinates)
   - `timestamp` values
5. **Event records** (optional but recommended)

### Verify Data Exists

```sql
-- Check match
SELECT * FROM matches WHERE id = '{MATCH_ID}';

-- Check video
SELECT * FROM videos WHERE match_id = '{MATCH_ID}';

-- Check tracks
SELECT object_class, COUNT(*) 
FROM tracks 
WHERE match_id = '{MATCH_ID}' 
GROUP BY object_class;

-- Check track points have coordinates
SELECT COUNT(*) 
FROM track_points tp
JOIN tracks t ON tp.track_id = t.id
WHERE t.match_id = '{MATCH_ID}' 
  AND tp.x_m IS NOT NULL 
  AND tp.y_m IS NOT NULL;

-- Check events
SELECT event_type, COUNT(*) 
FROM events 
WHERE match_id = '{MATCH_ID}' 
GROUP BY event_type;
```

---

## Performance Tips

### Backend

- Use lower FPS for large matches: `?fps=10` instead of `?fps=30`
- Limit time range: `?start_time=0&end_time=600` for first 10 minutes
- Consider caching timeline responses for frequently accessed matches

### Frontend

- Enable hardware acceleration in browser
- Close other tabs/applications if performance is poor
- Use lower playback speeds (0.5x or 1x) for smoother rendering
- Reduce number of concurrent animations (disable trails if slow)

---

## Next Steps

Once Phase 4 is working:

1. **Test with multiple matches** to ensure robustness
2. **Collect user feedback** on UI/UX
3. **Profile performance** with large datasets
4. **Plan Phase 5 features**:
   - 3D visualization
   - Video synchronization
   - Advanced analytics overlays
   - Mobile optimization

---

## Architecture Overview

```
Frontend (React)
    │
    ├─ useReplayController (playback state)
    │
    ├─ useReplayData (data fetching)
    │     └─ React Query
    │           └─ replayApi
    │
    ├─ MatchReplayView (main page)
    │     ├─ ReplayPitch (Konva canvas)
    │     ├─ ReplayControls (playback UI)
    │     └─ ReplaySidebar (stats & filters)
    │
    └─ HTTP Requests
          │
          ▼
Backend (FastAPI)
    │
    ├─ /api/v1/replay/match/{id}/summary
    ├─ /api/v1/replay/match/{id}/timeline
    │
    └─ ReplayService
          ├─ Position resampling
          ├─ Data aggregation
          └─ Database queries
                │
                ▼
          PostgreSQL
          ├─ matches
          ├─ videos
          ├─ tracks
          ├─ track_points
          └─ events
```

---

## Key Files Reference

### Backend
- `app/replay/service.py` - Core replay logic
- `app/api/routers/replay.py` - API endpoints
- `app/schemas/replay.py` - Pydantic models
- `app/main.py` - Router registration

### Frontend
- `src/pages/MatchReplayView.jsx` - Main page
- `src/components/replay/ReplayPitch.jsx` - Pitch rendering
- `src/components/replay/ReplayControls.jsx` - Controls
- `src/components/replay/ReplaySidebar.jsx` - Sidebar
- `src/hooks/useReplayController.js` - Playback hook
- `src/hooks/useReplayData.js` - Data fetching hook
- `src/services/api.js` - API client
- `src/App.jsx` - Routing

---

## Support & Troubleshooting

If you encounter issues:

1. **Check logs:**
   - Backend: Console output or logs/app.log
   - Frontend: Browser DevTools console

2. **Verify data:**
   - Use SQL queries above
   - Check API responses with curl

3. **Test incrementally:**
   - Backend API first
   - Then frontend components
   - Finally full integration

4. **Common fixes:**
   - Restart backend: `Ctrl+C` then restart uvicorn
   - Clear browser cache: `Ctrl+Shift+R`
   - Reinstall dependencies: `npm install`

---

## Success Checklist

- [ ] Backend running without errors
- [ ] Frontend running without errors
- [ ] Replay endpoints visible in API docs
- [ ] Match has tracking data in database
- [ ] Replay summary API returns data
- [ ] Replay timeline API returns positions
- [ ] Replay page loads without errors
- [ ] Players visible and moving on pitch
- [ ] Ball visible (if tracked)
- [ ] Events displayed as arrows
- [ ] Controls work (play/pause/seek)
- [ ] Speed changes work
- [ ] Player highlight works
- [ ] Event jump works

---

## Congratulations! 🎉

If all checks pass, Phase 4 is successfully deployed! You now have a working 2D virtual match replay system.

**Enjoy exploring your match data in a whole new way!** ⚽🎮
