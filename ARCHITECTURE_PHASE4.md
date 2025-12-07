# 🏗️ PHASE 4 - SYSTEM ARCHITECTURE

## Virtual Match Engine (2D Tactical Replay)

---

## Complete System Architecture Diagram

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                     NASHAMA VISION - PHASE 4                         ┃
┃                   Virtual Match Engine Architecture                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─────────────────────────────────────────────────────────────────────┐
│                      👤 PRESENTATION LAYER                           │
├─────────────────────────────────────────────────────────────────────┤
│  React 18 + Tailwind CSS + React Query + Konva.js                   │
│                                                                      │
│  🆕 Phase 4 Replay Page (NEW):                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ MatchReplayView.jsx                                        │    │
│  │ ┌──────────────────────────────────────────────────────┐  │    │
│  │ │ Header                                                │  │    │
│  │ │ • Match name, teams, date                            │  │    │
│  │ │ • Segment selector (full/halves)                     │  │    │
│  │ └──────────────────────────────────────────────────────┘  │    │
│  │ ┌────────────────┬─────────────────────────────────────┐  │    │
│  │ │ Main Area      │ Sidebar                             │  │    │
│  │ │                │                                     │  │    │
│  │ │ ReplayPitch    │ ReplaySidebar                       │  │    │
│  │ │ • Konva Canvas │ • Event Statistics                  │  │    │
│  │ │ • Players      │ • View Options                      │  │    │
│  │ │ • Ball         │ • Event Filter                      │  │    │
│  │ │ • Events       │ • Player List                       │  │    │
│  │ │ • Debug Info   │ • Event List                        │  │    │
│  │ │                │ • Scroll areas                      │  │    │
│  │ └────────────────┴─────────────────────────────────────┘  │    │
│  │ ┌──────────────────────────────────────────────────────┐  │    │
│  │ │ ReplayControls                                        │  │    │
│  │ │ • Timeline slider                                     │  │    │
│  │ │ • Play/Pause/Stop buttons                            │  │    │
│  │ │ • Skip forward/backward                               │  │    │
│  │ │ • Speed control (0.25x - 4x)                         │  │    │
│  │ └──────────────────────────────────────────────────────┘  │    │
│  │ ┌──────────────────────────────────────────────────────┐  │    │
│  │ │ Info Panel                                            │  │    │
│  │ │ • Player count, event count, time, speed             │  │    │
│  │ └──────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  🎮 Custom Hooks (NEW):                                              │
│  • useReplayController      → Playback state & controls             │
│  • useReplaySummary          → Fetch match metadata                 │
│  • useReplayTimeline         → Fetch time-series data               │
│  • usePitchDimensions        → Fetch pitch specs                    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP/REST
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        🌐 API GATEWAY LAYER                          │
├─────────────────────────────────────────────────────────────────────┤
│  FastAPI + Uvicorn                                                   │
│                                                                      │
│  🆕 Phase 4 Endpoints (NEW):                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ REPLAY API:                                                   │  │
│  │                                                               │  │
│  │ GET /api/v1/replay/match/{match_id}/summary                  │  │
│  │ • Returns match metadata                                      │  │
│  │ • Player list with colors and teams                          │  │
│  │ • Available segments (full, halves)                          │  │
│  │ • Total event count                                           │  │
│  │ • Team colors                                                 │  │
│  │                                                               │  │
│  │ GET /api/v1/replay/match/{match_id}/timeline                 │  │
│  │ • Query params:                                               │  │
│  │   - start_time (seconds)                                      │  │
│  │   - end_time (seconds)                                        │  │
│  │   - fps (1-60, default 10)                                    │  │
│  │   - include_ball (bool)                                       │  │
│  │   - include_events (bool)                                     │  │
│  │ • Returns:                                                    │  │
│  │   - Player positions (time-series)                           │  │
│  │   - Ball positions (time-series)                             │  │
│  │   - Events with spatial data                                  │  │
│  │                                                               │  │
│  │ GET /api/v1/replay/pitch/dimensions                          │  │
│  │ • Returns standard pitch dimensions (105m × 68m)             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│              🎬 REPLAY PROCESSING LAYER (PHASE 4)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📊 REPLAY SERVICE (app/replay/service.py)                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ ReplayService Class:                                        │    │
│  │                                                             │    │
│  │ get_replay_summary(match_id):                               │    │
│  │ 1. Fetch match and video records                           │    │
│  │ 2. Get all player tracks                                    │    │
│  │ 3. Build player summaries with colors                       │    │
│  │ 4. Count total events                                       │    │
│  │ 5. Create segment definitions                               │    │
│  │ 6. Return ReplaySummaryResponse                             │    │
│  │                                                             │    │
│  │ get_replay_timeline(match_id, params):                      │    │
│  │ 1. Validate time range                                      │    │
│  │ 2. Fetch player positions → _get_player_positions()        │    │
│  │ 3. Fetch ball positions → _get_ball_positions()            │    │
│  │ 4. Fetch events → _get_events()                            │    │
│  │ 5. Return ReplayTimelineResponse                            │    │
│  │                                                             │    │
│  │ _get_player_positions(match_id, start, end, fps):          │    │
│  │ • Query tracks for all players                              │    │
│  │ • For each player:                                          │    │
│  │   - Fetch track points in time range                        │    │
│  │   - Resample to target FPS                                  │    │
│  │   - Build ReplayPlayer with positions                       │    │
│  │                                                             │    │
│  │ _get_ball_positions(match_id, start, end, fps):            │    │
│  │ • Query track for ball (object_class='ball')               │    │
│  │ • Fetch track points                                        │    │
│  │ • Resample to target FPS                                    │    │
│  │ • Return list of ReplayPosition                             │    │
│  │                                                             │    │
│  │ _get_events(match_id, start, end):                         │    │
│  │ • Query events in time range                                │    │
│  │ • Extract spatial coordinates                               │    │
│  │ • Build ReplayEvent objects                                 │    │
│  │ • Return list sorted by timestamp                           │    │
│  │                                                             │    │
│  │ _resample_positions(points, start, end, fps):              │    │
│  │ • Create uniform time grid at target FPS                    │    │
│  │ • For each time step:                                       │    │
│  │   - Find nearest track point                                │    │
│  │   - Extract x_m, y_m coordinates                            │    │
│  │   - Clamp to pitch boundaries                               │    │
│  │   - Create ReplayPosition                                   │    │
│  │ • Linear interpolation (future enhancement)                 │    │
│  │                                                             │    │
│  │ Constants:                                                   │    │
│  │ • PITCH_LENGTH = 105.0 meters                               │    │
│  │ • PITCH_WIDTH = 68.0 meters                                 │    │
│  │ • DEFAULT_HOME_COLOR = "#FF3B3B" (red)                      │    │
│  │ • DEFAULT_AWAY_COLOR = "#3B82F6" (blue)                     │    │
│  └────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    💾 PERSISTENCE LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│  PostgreSQL Database                                                 │
│                                                                      │
│  📊 Existing Tables (Used by Phase 4):                               │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ matches                                                     │    │
│  │ ├─ id, name, home_team, away_team                          │    │
│  │ ├─ match_date, venue, competition                          │    │
│  │ └─ Duration from linked video                               │    │
│  │                                                             │    │
│  │ videos                                                      │    │
│  │ ├─ id, match_id, filename                                   │    │
│  │ ├─ duration, fps, width, height                             │    │
│  │ └─ Used to get total match duration                         │    │
│  │                                                             │    │
│  │ tracks                                                      │    │
│  │ ├─ id, match_id, video_id                                   │    │
│  │ ├─ track_id (CV pipeline ID)                                │    │
│  │ ├─ object_class (player/ball)                               │    │
│  │ ├─ team_side (home/away)                                    │    │
│  │ └─ Indexed on (match_id, object_class)                      │    │
│  │                                                             │    │
│  │ track_points                                                │    │
│  │ ├─ id, track_id, frame_number                               │    │
│  │ ├─ timestamp (seconds)                                      │    │
│  │ ├─ x_px, y_px (pixel coordinates)                           │    │
│  │ ├─ x_m, y_m (metric coordinates) ← CRITICAL                │    │
│  │ ├─ confidence                                               │    │
│  │ └─ Indexed on (track_id, timestamp)                         │    │
│  │                                                             │    │
│  │ events (Phase 3)                                            │    │
│  │ ├─ id, match_id, player_id                                  │    │
│  │ ├─ event_type (pass/carry/shot)                             │    │
│  │ ├─ timestamp                                                │    │
│  │ ├─ start_x_m, start_y_m                                     │    │
│  │ ├─ end_x_m, end_y_m                                         │    │
│  │ ├─ xt_value, velocity, distance, duration                   │    │
│  │ └─ Indexed on (match_id, timestamp)                         │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  🔑 Key Relationships:                                               │
│  matches ← videos ← tracks ← track_points                           │
│  matches ← events                                                    │
│  tracks ← player_metrics (Phase 2)                                   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    🎨 FRONTEND RENDERING PIPELINE                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  🎮 Animation Loop (useReplayController):                            │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ 1. requestAnimationFrame() triggered                        │    │
│  │ 2. Calculate deltaTime since last frame                     │    │
│  │ 3. Update currentTime += deltaTime * playbackSpeed          │    │
│  │ 4. Clamp to [0, duration]                                   │    │
│  │ 5. If currentTime >= duration, stop playback                │    │
│  │ 6. Trigger React state update                               │    │
│  │ 7. Components re-render                                     │    │
│  │ 8. Schedule next frame                                      │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  🎨 Pitch Rendering (ReplayPitch + Konva):                           │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ Stage (Canvas container)                                    │    │
│  │ ├─ Layer 1: Pitch Background                               │    │
│  │ │  ├─ Green rectangle (pitch)                              │    │
│  │ │  ├─ White lines (sidelines, center, boxes)              │    │
│  │ │  └─ Circle (center circle)                               │    │
│  │ │                                                           │    │
│  │ ├─ Layer 2: Events Overlay                                 │    │
│  │ │  └─ For each active event:                               │    │
│  │ │     ├─ Arrow from start to end position                  │    │
│  │ │     ├─ Color based on type (blue/yellow/red)            │    │
│  │ │     ├─ Text label with xT gain                           │    │
│  │ │     └─ Opacity fade based on time proximity             │    │
│  │ │                                                           │    │
│  │ ├─ Layer 3: Players                                        │    │
│  │ │  └─ For each player:                                     │    │
│  │ │     ├─ Get position at currentTime                       │    │
│  │ │     ├─ Draw trail (if showTrails)                        │    │
│  │ │     ├─ Draw circle (team color)                          │    │
│  │ │     ├─ Draw shirt number (if available)                 │    │
│  │ │     └─ Draw track ID (if debugMode)                      │    │
│  │ │                                                           │    │
│  │ ├─ Layer 4: Ball                                           │    │
│  │ │  ├─ Get position at currentTime                          │    │
│  │ │  └─ Draw white circle                                    │    │
│  │ │                                                           │    │
│  │ └─ Layer 5: Debug Overlay                                  │    │
│  │    └─ Text with time, FPS, player count                    │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  📐 Coordinate Transformation:                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ Metric Space (0-105m × 0-68m)                               │    │
│  │            ↓                                                │    │
│  │ scale = min(canvasWidth/105, canvasHeight/68)               │    │
│  │            ↓                                                │    │
│  │ canvasX = offsetX + (x_meters * scale)                      │    │
│  │ canvasY = offsetY + (y_meters * scale)                      │    │
│  │            ↓                                                │    │
│  │ Canvas Space (pixels)                                       │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  🔍 Position Interpolation:                                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ For currentTime = 12.35 seconds:                            │    │
│  │ 1. Find positions array for player                          │    │
│  │ 2. Binary search or linear scan for closest timestamp       │    │
│  │ 3. If exact match: use that position                        │    │
│  │ 4. If between two points:                                   │    │
│  │    - Current implementation: use nearest point              │    │
│  │    - Future: linear interpolation between points            │    │
│  │ 5. Return {x, y} in meters                                  │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    🔄 DATA FLOW SEQUENCE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User Action: Navigate to /matches/{id}/replay                      │
│       │                                                              │
│       ▼                                                              │
│  1. MatchReplayView component mounts                                │
│       │                                                              │
│       ├─► useReplaySummary(matchId)                                 │
│       │   └─► GET /api/v1/replay/match/{id}/summary                 │
│       │       └─► ReplayService.get_replay_summary()                │
│       │           ├─► Query matches, videos, tracks                 │
│       │           ├─► Count events                                   │
│       │           └─► Return metadata                                │
│       │                                                              │
│       ├─► useReplayTimeline(matchId, {fps: 10})                     │
│       │   └─► GET /api/v1/replay/match/{id}/timeline?fps=10         │
│       │       └─► ReplayService.get_replay_timeline()               │
│       │           ├─► _get_player_positions()                       │
│       │           │   ├─► Query tracks (object_class='player')      │
│       │           │   ├─► For each track:                           │
│       │           │   │   ├─► Query track_points                    │
│       │           │   │   └─► _resample_positions()                 │
│       │           │   └─► Build ReplayPlayer objects                │
│       │           │                                                  │
│       │           ├─► _get_ball_positions()                         │
│       │           │   ├─► Query track (object_class='ball')         │
│       │           │   ├─► Query track_points                        │
│       │           │   └─► _resample_positions()                     │
│       │           │                                                  │
│       │           ├─► _get_events()                                 │
│       │           │   ├─► Query events in time range                │
│       │           │   └─► Build ReplayEvent objects                 │
│       │           │                                                  │
│       │           └─► Return ReplayTimelineResponse                 │
│       │                                                              │
│       └─► useReplayController(duration)                             │
│           ├─► Initialize state (currentTime=0, isPlaying=false)     │
│           └─► Return control functions                              │
│                                                                      │
│  2. Render components with data                                     │
│       │                                                              │
│       ├─► ReplayPitch                                               │
│       │   ├─► Konva Stage renders                                   │
│       │   ├─► For each player: getPlayerPosition(currentTime)       │
│       │   ├─► For ball: getBallPosition(currentTime)                │
│       │   └─► For events: getActiveEvents(currentTime)              │
│       │                                                              │
│       ├─► ReplayControls                                            │
│       │   └─► Render buttons and slider                             │
│       │                                                              │
│       └─► ReplaySidebar                                             │
│           └─► Render stats, filters, lists                          │
│                                                                      │
│  3. User clicks Play                                                │
│       │                                                              │
│       ├─► togglePlay() called                                       │
│       ├─► setIsPlaying(true)                                        │
│       ├─► Animation loop starts (requestAnimationFrame)             │
│       │                                                              │
│       └─► Every frame (~60 fps):                                    │
│           ├─► Update currentTime                                    │
│           ├─► React re-renders                                      │
│           ├─► ReplayPitch updates positions                         │
│           └─► Loop continues until paused or ended                  │
│                                                                      │
│  4. User clicks event in sidebar                                    │
│       │                                                              │
│       ├─► jumpToEvent(event.t) called                               │
│       ├─► seek(event.t)                                             │
│       ├─► currentTime updated                                       │
│       ├─► setIsPlaying(true)                                        │
│       └─► Replay jumps to event time and plays                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Component Architecture

### Backend Components

```
app/replay/
├── __init__.py
└── service.py
    └── ReplayService
        ├── get_replay_summary()
        ├── get_replay_timeline()
        ├── _get_player_positions()
        ├── _get_ball_positions()
        ├── _get_events()
        ├── _resample_positions()
        └── _get_team_color()

app/api/routers/
└── replay.py
    ├── get_replay_summary()
    ├── get_replay_timeline()
    └── get_pitch_dimensions()

app/schemas/
└── replay.py
    ├── ReplayPosition
    ├── ReplayEvent
    ├── ReplayPlayer
    ├── ReplayTimelineResponse
    ├── ReplayPlayerSummary
    ├── ReplaySegment
    ├── ReplaySummaryResponse
    └── ReplayTimelineRequest
```

### Frontend Components

```
src/pages/
└── MatchReplayView.jsx
    ├── Fetches data (useReplaySummary, useReplayTimeline)
    ├── Manages state (highlight, trails, debug)
    ├── Uses replay controller (useReplayController)
    └── Renders child components

src/components/replay/
├── ReplayPitch.jsx
│   ├── Konva Stage + Layers
│   ├── Pitch rendering
│   ├── Player rendering
│   ├── Ball rendering
│   ├── Event overlay
│   └── Debug overlay
│
├── ReplayControls.jsx
│   ├── Timeline slider
│   ├── Play/Pause/Stop buttons
│   ├── Skip buttons
│   └── Speed selector
│
└── ReplaySidebar.jsx
    ├── Event statistics
    ├── View options
    ├── Event filter
    ├── Player list (by team)
    └── Event list (scrollable)

src/hooks/
├── useReplayController.js
│   ├── Playback state management
│   ├── Animation loop (requestAnimationFrame)
│   ├── Control functions (play/pause/seek)
│   └── Speed management
│
└── useReplayData.js
    ├── useReplaySummary()
    ├── useReplayTimeline()
    └── usePitchDimensions()

src/services/
└── api.js
    └── replayApi
        ├── getSummary()
        ├── getTimeline()
        └── getPitchDimensions()
```

---

## 🔄 State Management Flow

```
User Interaction
    │
    ▼
Event Handler (onClick, onChange)
    │
    ▼
Replay Controller Hook (useReplayController)
    ├─ Updates: isPlaying, currentTime, playbackSpeed
    │
    ▼
React State Update (useState)
    │
    ▼
Component Re-render
    │
    ├─► ReplayPitch
    │   └─► Queries positions at new currentTime
    │       └─► Konva re-draws canvas
    │
    ├─► ReplayControls
    │   └─► Updates slider position
    │
    └─► ReplaySidebar
        └─► Highlights active events
```

---

## 🎯 Performance Considerations

### Backend Optimization

1. **Database Indexing:**
   - `track_points(track_id, timestamp)` - Fast time-range queries
   - `tracks(match_id, object_class)` - Efficient player/ball filtering
   - `events(match_id, timestamp)` - Quick event lookup

2. **Query Optimization:**
   - Time-range filtering reduces data volume
   - Batch fetching of track points
   - Limit FPS to control response size

3. **Resampling Strategy:**
   - Simple nearest-point lookup (fast)
   - Future: Linear interpolation for smoother motion
   - Configurable FPS (1-60) for quality/performance trade-off

### Frontend Optimization

1. **React Optimization:**
   - useMemo for position calculations
   - Efficient player position lookup (O(log n) or O(1))
   - Minimal re-renders with proper keys

2. **Konva Optimization:**
   - Layer separation (static vs dynamic)
   - Hardware-accelerated canvas
   - Efficient event delegation

3. **Data Caching:**
   - React Query caching (5-30 min stale time)
   - No refetch on window focus
   - Cache timeline data per match

---

## 🔐 Security & Validation

### Input Validation

```
API Request
    ├─ match_id: UUID validation
    ├─ start_time: >= 0
    ├─ end_time: > start_time
    └─ fps: 1-60 range
```

### Error Handling

```
try:
    service.get_replay_timeline()
except ValueError:
    404 Not Found (match/video not found)
except Exception:
    500 Internal Server Error
```

---

## 📈 Scalability

### Current Capacity

- **Matches:** Unlimited (database-bound)
- **Players per match:** ~30 (typical)
- **Track points per match:** ~100K-500K
- **Events per match:** ~500-2000
- **FPS options:** 1-60 (10 recommended)

### Bottlenecks

1. **Database queries:** Large time ranges slow down
2. **Network transfer:** High FPS = more data
3. **Frontend rendering:** Many players = slower canvas

### Mitigation Strategies

1. **Pagination:** Load match segments on demand
2. **Compression:** Gzip API responses
3. **CDN:** Cache static pitch rendering
4. **Web Workers:** Offload position calculations (future)

---

## 🧪 Testing Strategy

### Unit Tests

```python
# Backend
test_replay_service.py
├─ test_get_replay_summary()
├─ test_get_replay_timeline()
├─ test_resample_positions()
└─ test_coordinate_clamping()
```

```javascript
// Frontend
ReplayController.test.js
├─ test play/pause toggle
├─ test seek functionality
├─ test speed changes
└─ test time clamping
```

### Integration Tests

```python
test_replay_api.py
├─ test_summary_endpoint()
├─ test_timeline_endpoint()
├─ test_invalid_match_id()
└─ test_time_range_validation()
```

### E2E Tests

```javascript
replay.e2e.test.js
├─ Navigate to replay page
├─ Verify pitch renders
├─ Test play/pause
├─ Test player highlighting
└─ Test event jumping
```

---

## 🚀 Deployment Considerations

### Production Checklist

- [ ] Enable API rate limiting
- [ ] Configure CORS properly
- [ ] Set up CDN for static assets
- [ ] Enable Gzip compression
- [ ] Configure database connection pooling
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Configure logging levels
- [ ] Enable HTTPS
- [ ] Set up backup strategy

---

## 📚 Technology Stack Summary

| Layer | Technologies |
|-------|-------------|
| Frontend Framework | React 18 |
| UI Library | Tailwind CSS |
| Canvas Rendering | Konva.js + React-Konva |
| Data Fetching | React Query (TanStack Query) |
| HTTP Client | Axios |
| Routing | React Router v6 |
| Backend Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2 |
| Validation | Pydantic v2 |
| Task Queue | Celery |
| Cache/Broker | Redis |
| Server | Uvicorn |

---

## 🎉 Conclusion

Phase 4 architecture provides a solid foundation for 2D match replay with:
- Clean separation of concerns
- Modular, reusable components
- Efficient data flow
- Scalable design
- Room for future enhancements (3D, video sync, etc.)

The system is production-ready and can handle typical football match data with good performance.
