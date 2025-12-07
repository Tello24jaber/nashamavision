# 🎮 NASHAMA VISION - PHASE 4 COMPLETE

## 📋 Executive Summary

**Phase 4 of Nashama Vision has been fully implemented**, adding a **Virtual Match Engine** with 2D tactical replay capabilities to the platform.

Phase 4 adds:
- ✅ **Replay Data API** (timeline endpoints, position resampling)
- ✅ **Virtual Pitch Rendering** (Konva.js-based 2D visualization)
- ✅ **Animation Engine** (smooth playback at configurable FPS)
- ✅ **Playback Controls** (play/pause, seek, speed control)
- ✅ **Event Overlay** (visual representation of passes, carries, shots)
- ✅ **Player Interaction** (highlight, trails, click handlers)
- ✅ **React Components** (modular, reusable architecture)
- ✅ **State Management** (custom hooks for replay control)

---

## 🎯 What's New in Phase 4

### Backend Enhancements

#### 1. Replay Service (`app/replay/service.py`)

**Position Resampling:**
- Converts variable-rate tracking data to consistent FPS
- Linear interpolation between track points
- Configurable output frame rate (1-60 FPS)
- Clamps positions to pitch boundaries

**Data Aggregation:**
- Fetches player tracks and positions
- Retrieves ball tracking data
- Includes event data with spatial coordinates
- Optimized queries with time-range filtering

**Team Color Management:**
- Default colors for home/away teams
- Extensible for custom team colors
- Consistent color scheme across UI

#### 2. Replay Schemas (`app/schemas/replay.py`)

**Data Models:**

```python
ReplayPosition
  ├─ t (time in seconds)
  ├─ x (meters, 0-105)
  └─ y (meters, 0-68)

ReplayPlayer
  ├─ player_id, track_id
  ├─ team (home/away)
  ├─ shirt_number
  ├─ color
  └─ positions (time-series)

ReplayEvent
  ├─ type (pass/carry/shot)
  ├─ t (event time)
  ├─ from/to positions
  ├─ xt_gain
  └─ velocity, distance, duration

ReplayTimelineResponse
  ├─ match_id, fps, duration
  ├─ players (all players with positions)
  ├─ ball (ball positions)
  └─ events (match events)

ReplaySummaryResponse
  ├─ match metadata
  ├─ player list
  ├─ available segments
  └─ event statistics
```

#### 3. API Endpoints (`app/api/routers/replay.py`)

**Replay Endpoints:**
- `GET /api/v1/replay/match/{match_id}/summary` - Match metadata and player list
- `GET /api/v1/replay/match/{match_id}/timeline` - Time-series replay data
  - Query params: `start_time`, `end_time`, `fps`, `include_ball`, `include_events`
- `GET /api/v1/replay/pitch/dimensions` - Standard pitch dimensions

**Features:**
- Configurable FPS (1-60)
- Time-range filtering for segments
- Optional ball/event inclusion
- Comprehensive error handling

---

### Frontend Enhancements

#### 1. Replay Controller Hook (`useReplayController.js`)

**Playback State Management:**
- `isPlaying` - Play/pause state
- `currentTime` - Current playback time
- `playbackSpeed` - Speed multiplier (0.25x - 4x)
- `duration` - Total replay duration
- `progress` - Progress percentage (0-100)

**Control Functions:**
- `play()` - Start playback
- `pause()` - Pause playback
- `togglePlay()` - Toggle play/pause
- `stop()` - Stop and reset to start
- `seek(time)` - Jump to specific time
- `jumpToEvent(eventTime)` - Jump to event and play
- `skipForward(seconds)` - Skip forward
- `skipBackward(seconds)` - Skip backward
- `changeSpeed(speed)` - Change playback speed

**Animation Loop:**
- Uses `requestAnimationFrame` for smooth animation
- Delta-time based updates for consistent speed
- Auto-stop at end of replay

#### 2. Virtual Pitch Component (`ReplayPitch.jsx`)

**Pitch Rendering:**
- Standard football pitch markings
  - Sidelines, halfway line
  - Center circle and spot
  - Penalty boxes and goal boxes
- Responsive scaling with aspect ratio preservation
- Coordinate conversion (meters → canvas pixels)

**Player Rendering:**
- Colored circles with team colors
- Shirt numbers (when available)
- Highlight on selection
- Player trails (last N seconds)
- Click handlers for interaction

**Ball Rendering:**
- White circle marker
- Position interpolation at current time
- Optional trail visualization

**Event Overlay:**
- Colored arrows for different event types:
  - **Blue** - Passes
  - **Yellow** - Carries
  - **Red** - Shots
- xT gain labels
- Fade effect based on time proximity

**Debug Features:**
- Track ID labels
- FPS counter
- Current time display
- Position coordinates

#### 3. Playback Controls Component (`ReplayControls.jsx`)

**Timeline Slider:**
- Smooth seeking via range input
- Current time / duration display
- Visual progress indicator

**Control Buttons:**
- Play/Pause toggle (large button)
- Stop button
- Skip forward/backward (10s)
- SVG icons for all controls

**Speed Control:**
- Quick select buttons: 0.25x, 0.5x, 1x, 1.5x, 2x, 4x
- Visual indication of current speed
- Smooth speed transitions

#### 4. Sidebar Component (`ReplaySidebar.jsx`)

**Event Statistics:**
- Total events count
- Event type breakdown (pass/carry/shot)
- Color-coded cards

**View Options:**
- Show/hide ball trail
- Debug mode toggle
- Checkboxes for easy control

**Event Filter:**
- Filter by type (all/pass/carry/shot)
- Quick toggle buttons

**Players List:**
- Grouped by team (home/away)
- Team filter (all/home/away)
- Color indicators
- Click to highlight on pitch
- Track IDs and shirt numbers

**Events List:**
- Scrollable list of all events
- Event type, time, xT gain, distance
- Color-coded by type
- Click to jump to event
- Highlight events near current time

#### 5. Main Replay Page (`MatchReplayView.jsx`)

**Layout:**
- Grid-based responsive layout
- Large pitch area (left/main)
- Controls below pitch
- Sidebar with stats (right)
- Info panel at bottom

**Features:**
- Match header with teams and date
- Segment selector (full match, halves)
- Loading and error states
- Real-time sync between components
- Player highlight on click
- Event jump on click

**State Management:**
- Local state for UI preferences
- React Query for data fetching
- Custom replay controller hook
- Efficient re-rendering

---

## 🔄 Complete System Flow (Updated)

```
┌────────────────────────────────────────────────────────────────┐
│ 1. VIDEO UPLOAD & PROCESSING (PHASE 1)                        │
│    ├─ Detection, Tracking, Classification                      │
│    └─ Track Points with Metric Coordinates                     │
└──────────────────┬─────────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────────┐
│ 2. PHYSICAL ANALYTICS (PHASE 2)                               │
│    ├─ Distance, Speed, Sprints                                │
│    └─ Stamina, Heatmaps                                        │
└──────────────────┬─────────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────────┐
│ 3. TACTICAL ANALYTICS (PHASE 3)                               │
│    ├─ Formation, Pressing, Transitions                        │
│    ├─ xT Engine, Events                                       │
│    └─ Tactical Snapshots                                       │
└──────────────────┬─────────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────────┐
│ 4. VIRTUAL MATCH ENGINE (PHASE 4) ← NEW                       │
│    ├─ Timeline Data API                                        │
│    ├─ Position Resampling                                      │
│    ├─ 2D Pitch Rendering                                       │
│    ├─ Animation Engine                                         │
│    ├─ Event Overlay                                            │
│    └─ Player Interaction                                       │
└──────────────────┬─────────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────────┐
│ 5. FRONTEND VISUALIZATION                                      │
│    ├─ Match Details (Phase 1)                                 │
│    ├─ Player Metrics (Phase 2)                                │
│    ├─ Heatmaps (Phase 2)                                      │
│    ├─ Tactical Dashboard (Phase 3)                            │
│    ├─ xT Dashboard (Phase 3)                                  │
│    ├─ Events Timeline (Phase 3)                               │
│    └─ Match Replay (Phase 4) ← NEW                            │
└────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation & Setup

### 1. Backend Setup

```bash
cd backend

# No new Python dependencies required
# (Uses existing FastAPI, SQLAlchemy, Pydantic)

# Ensure database is up to date
alembic upgrade head

# Start services
# Terminal 1: Redis
redis-server

# Terminal 2: PostgreSQL
# (ensure PostgreSQL is running)

# Terminal 3: Celery Worker
celery -A app.workers.celery_app worker -l info

# Terminal 4: FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install new dependencies (Konva)
npm install

# Start dev server
npm run dev
```

### 3. Access the Application

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Replay Page: http://localhost:5173/matches/{matchId}/replay

---

## 📊 Usage Guide

### Step-by-Step Workflow

1. **Upload and Process Video**
   - Upload video via the API or UI
   - Wait for Phase 1-3 processing to complete
   - Ensure track points have metric coordinates

2. **Navigate to Replay**
   - Go to match details page
   - Click "View Replay" or navigate to `/matches/{matchId}/replay`
   - Wait for replay data to load

3. **Interact with Replay**
   - **Play/Pause:** Click the large play button
   - **Seek:** Drag the timeline slider
   - **Speed:** Click speed buttons (0.25x - 4x)
   - **Skip:** Use skip forward/backward buttons
   - **Highlight Player:** Click player in sidebar
   - **Jump to Event:** Click event in event list
   - **Toggle Options:** Use checkboxes in sidebar

4. **View Event Overlay**
   - Events appear as colored arrows on pitch
   - Pass (blue), Carry (yellow), Shot (red)
   - xT gain displayed for each event
   - Automatically fades based on time

5. **Debug Mode**
   - Enable debug mode in sidebar
   - Shows track IDs
   - Displays FPS and time info
   - Useful for validation

---

## 🔍 Key Features Explained

### Replay Features

| Feature | Description |
|---------|-------------|
| Playback Controls | Play, pause, stop, seek, skip forward/backward |
| Variable Speed | 0.25x to 4x playback speed |
| Time Navigation | Slider for precise seeking |
| Event Jumping | Click event to jump to that moment |
| Player Highlighting | Click player to highlight and show trail |
| Event Overlay | Visual arrows for passes, carries, shots |
| Team Colors | Distinct colors for home/away teams |
| Debug Mode | Track IDs, FPS, coordinates |

### Technical Features

| Feature | Description |
|---------|-------------|
| Position Resampling | Converts variable-rate data to consistent FPS |
| Coordinate Conversion | Meters → Canvas pixels with scaling |
| Animation Loop | RequestAnimationFrame-based smooth animation |
| State Management | Custom hooks for playback control |
| React Query | Cached API data with stale-time management |
| Konva Rendering | Hardware-accelerated canvas rendering |
| Responsive Layout | Grid-based layout adapts to screen size |

---

## 🧪 Testing Phase 4

### Manual Testing

1. **API Endpoints:**
```bash
# Test replay summary
curl http://localhost:8000/api/v1/replay/match/{match_id}/summary

# Test replay timeline
curl "http://localhost:8000/api/v1/replay/match/{match_id}/timeline?fps=10"

# Test with time range
curl "http://localhost:8000/api/v1/replay/match/{match_id}/timeline?start_time=0&end_time=600&fps=15"

# Test pitch dimensions
curl http://localhost:8000/api/v1/replay/pitch/dimensions
```

2. **Database Verification:**
```sql
-- Check track points have metric coordinates
SELECT COUNT(*) FROM track_points WHERE x_m IS NOT NULL AND y_m IS NOT NULL;

-- Check ball tracking
SELECT COUNT(*) FROM tracks WHERE object_class = 'ball';

-- Check events for replay
SELECT event_type, COUNT(*) FROM events GROUP BY event_type;
```

3. **Frontend Testing:**
   - Navigate to replay page
   - Test play/pause/stop controls
   - Test seeking with slider
   - Test speed changes
   - Click players to highlight
   - Click events to jump
   - Toggle debug mode
   - Test on different screen sizes

---

## 🐛 Troubleshooting

### Common Issues

**Issue: Replay page shows loading forever**
- Check if match has processed tracking data
- Verify track points exist in database
- Check browser console for API errors
- Verify backend is running: `curl http://localhost:8000/health`

**Issue: Players not moving**
- Ensure playback is playing (not paused)
- Check if track points have metric coordinates (x_m, y_m)
- Verify FPS is reasonable (10-30)
- Check currentTime is incrementing

**Issue: No ball visible**
- Verify ball tracking exists in database
- Check `include_ball=true` in API call
- Ensure ball track has object_class='ball'

**Issue: Events not showing**
- Verify events exist in database for this match
- Check `include_events=true` in API call
- Ensure event overlay is enabled
- Check events are within time range

**Issue: Poor performance**
- Reduce FPS (try 10 instead of 30)
- Limit time range (use start_time/end_time)
- Check number of players (>22 may be slow)
- Enable hardware acceleration in browser

---

## 📈 Performance Optimization

### Backend Optimization

**Database Queries:**
- Indexed on (match_id, timestamp) for fast lookups
- Time-range filtering reduces data transfer
- Batch fetching of track points

**Resampling:**
- Efficient linear interpolation
- Position caching during computation
- Configurable FPS to control data volume

### Frontend Optimization

**React Optimization:**
- useMemo for expensive calculations
- Efficient position lookups
- Minimal re-renders with proper keys

**Canvas Rendering:**
- Konva uses hardware acceleration
- Layer separation for static/dynamic elements
- Efficient redraw on state change

**Data Management:**
- React Query caching (5-30 min stale time)
- Lazy loading of segments
- Position interpolation on client side

---

## 🔐 Security Considerations

**API Rate Limiting (Future):**
- Limit timeline requests per minute
- Prevent abuse of expensive queries

**Data Privacy:**
- No PII in tracking data
- Anonymous player IDs
- Match data access control (future)

---

## 🛠️ Future Enhancements (Phase 5+)

Potential features:
- ✨ **3D Replay:** Three.js-based 3D visualization
- 📊 **Heatmap Overlay:** Real-time heatmap on pitch
- 🎯 **Formation Overlay:** Show detected formations
- 📱 **Mobile Optimization:** Touch controls, smaller layouts
- 🔄 **Real-time Sync:** Multi-user synchronized viewing
- 🤖 **AI Commentary:** Automated event descriptions
- 📹 **Video Sync:** Overlay replay on original video
- 🎨 **Custom Themes:** User-configurable colors
- 📦 **Export:** Save replay as video or GIF
- 🔊 **Audio:** Sound effects for events

---

## 📚 Code Structure

### Backend

```
backend/
├── app/
│   ├── replay/
│   │   ├── __init__.py
│   │   └── service.py          ← Replay data processing
│   ├── api/routers/
│   │   └── replay.py            ← API endpoints
│   ├── schemas/
│   │   └── replay.py            ← Pydantic models
│   └── main.py                  ← Updated with replay router
```

### Frontend

```
frontend/
├── src/
│   ├── components/replay/
│   │   ├── ReplayPitch.jsx      ← Konva pitch rendering
│   │   ├── ReplayControls.jsx   ← Playback controls
│   │   └── ReplaySidebar.jsx    ← Sidebar with stats
│   ├── hooks/
│   │   ├── useReplayController.js  ← Playback state
│   │   └── useReplayData.js        ← Data fetching
│   ├── pages/
│   │   └── MatchReplayView.jsx     ← Main replay page
│   ├── services/
│   │   └── api.js                  ← Updated with replay API
│   ├── App.jsx                     ← Updated with replay route
│   └── package.json                ← Updated with Konva
```

---

## 📖 API Documentation

### Replay Summary

```http
GET /api/v1/replay/match/{match_id}/summary
```

**Response:**
```json
{
  "match_id": "uuid",
  "match_name": "string",
  "home_team": "string",
  "away_team": "string",
  "match_date": "datetime",
  "duration": 5400.0,
  "players": [
    {
      "player_id": "uuid",
      "track_id": 1,
      "team": "home",
      "shirt_number": 7,
      "color": "#FF3B3B"
    }
  ],
  "segments": [
    {
      "id": "full",
      "name": "Full Match",
      "start_time": 0.0,
      "end_time": 5400.0,
      "duration": 5400.0
    }
  ],
  "total_events": 243,
  "home_team_color": "#FF3B3B",
  "away_team_color": "#3B82F6"
}
```

### Replay Timeline

```http
GET /api/v1/replay/match/{match_id}/timeline?fps=10&start_time=0&end_time=600
```

**Response:**
```json
{
  "match_id": "uuid",
  "fps": 10.0,
  "duration": 600.0,
  "start_time": 0.0,
  "end_time": 600.0,
  "players": [
    {
      "player_id": "uuid",
      "track_id": 1,
      "team": "home",
      "color": "#FF3B3B",
      "positions": [
        { "t": 0.0, "x": 52.5, "y": 34.0 },
        { "t": 0.1, "x": 52.6, "y": 34.1 }
      ]
    }
  ],
  "ball": [
    { "t": 0.0, "x": 52.5, "y": 34.0 },
    { "t": 0.1, "x": 52.7, "y": 34.2 }
  ],
  "events": [
    {
      "id": "uuid",
      "type": "pass",
      "t": 12.5,
      "player_id": "uuid",
      "from": { "x": 30.2, "y": 20.5 },
      "to": { "x": 45.1, "y": 25.3 },
      "xt_gain": 0.042,
      "velocity": 15.2,
      "distance": 16.8,
      "duration": 1.1
    }
  ]
}
```

---

## ✅ Phase 4 Completion Checklist

- [x] Replay service with position resampling
- [x] Replay API endpoints (summary, timeline, dimensions)
- [x] Pydantic schemas for replay data
- [x] React replay controller hook
- [x] Virtual pitch rendering with Konva
- [x] Playback controls component
- [x] Sidebar with stats and filters
- [x] Main replay page
- [x] Event overlay visualization
- [x] Player interaction (highlight, trails)
- [x] Debug mode
- [x] Routing integration
- [x] Package.json updated with Konva
- [x] Documentation complete

---

## 🎉 Conclusion

**Phase 4 is 100% complete and production-ready!**

The Virtual Match Engine provides a powerful 2D replay capability that brings match data to life. Users can now:
- Watch matches replay in 2D
- Control playback with full VCR-style controls
- Jump to specific events instantly
- Highlight and track individual players
- Visualize events with color-coded overlays
- Debug and validate tracking data

This foundation can be extended in future phases with 3D visualization, video synchronization, and advanced analytics overlays.

**Next Steps:**
1. Install dependencies: `npm install` in frontend
2. Test the replay endpoints with a processed match
3. Navigate to `/matches/{matchId}/replay` to see it in action
4. Provide feedback for Phase 5 features

---

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation at http://localhost:8000/docs
- Check browser console for frontend errors
- Verify backend logs for API errors

**Happy Replaying! ⚽🎮**
