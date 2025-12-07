# 🎮 Replay Module - Developer Guide

## Phase 4: Virtual Match Engine

This guide is for developers working on or extending the Replay module.

---

## 📁 Module Structure

```
backend/app/replay/
├── __init__.py          # Module initialization
└── service.py           # Core replay logic

backend/app/api/routers/
└── replay.py            # API endpoints

backend/app/schemas/
└── replay.py            # Pydantic models

frontend/src/pages/
└── MatchReplayView.jsx  # Main replay page

frontend/src/components/replay/
├── ReplayPitch.jsx      # Konva-based pitch rendering
├── ReplayControls.jsx   # Playback controls
└── ReplaySidebar.jsx    # Stats and filters

frontend/src/hooks/
├── useReplayController.js  # Playback state management
└── useReplayData.js        # Data fetching hooks

frontend/src/services/
└── api.js               # API client (replayApi section)
```

---

## 🔧 Backend Development

### ReplayService Class

**Location:** `backend/app/replay/service.py`

**Main Methods:**

```python
class ReplayService:
    def get_replay_summary(self, match_id: UUID) -> ReplaySummaryResponse:
        """
        Get match metadata, player list, and available segments.
        
        Returns:
            ReplaySummaryResponse with:
            - Match info (teams, date, duration)
            - Player list with colors
            - Segments (full, halves)
            - Event count
        """
        
    def get_replay_timeline(
        self,
        match_id: UUID,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        fps: float = 10,
        include_ball: bool = True,
        include_events: bool = True
    ) -> ReplayTimelineResponse:
        """
        Get time-series replay data.
        
        Args:
            match_id: Match UUID
            start_time: Start time in seconds (None = 0)
            end_time: End time in seconds (None = duration)
            fps: Target frames per second (1-60)
            include_ball: Include ball tracking
            include_events: Include event data
            
        Returns:
            ReplayTimelineResponse with:
            - Player positions (resampled to fps)
            - Ball positions
            - Events
        """
```

**Adding a New Feature:**

1. Add method to `ReplayService`
2. Create Pydantic schema in `schemas/replay.py`
3. Add API endpoint in `api/routers/replay.py`
4. Update frontend to consume new endpoint

**Example: Adding Player Names**

```python
# 1. Modify ReplayService._get_player_positions()
def _get_player_positions(self, ...):
    # ... existing code ...
    
    # Add player name from database
    player_name = self._get_player_name(track.id)
    
    player = ReplayPlayer(
        player_id=track.id,
        track_id=track.track_id,
        team=track.team_side,
        name=player_name,  # NEW
        # ... rest of fields
    )
```

```python
# 2. Update schema
class ReplayPlayer(BaseModel):
    player_id: UUID
    track_id: int
    team: TeamSide
    name: Optional[str] = None  # NEW
    # ... rest of fields
```

No endpoint changes needed - schema automatically includes new field!

---

## 🎨 Frontend Development

### Component Hierarchy

```
MatchReplayView (Page)
│
├─── ReplayPitch (Canvas)
│    ├─ Konva Stage
│    ├─ Background Layer (pitch)
│    ├─ Events Layer (arrows)
│    ├─ Players Layer (circles)
│    ├─ Ball Layer (circle)
│    └─ Debug Layer (text)
│
├─── ReplayControls
│    ├─ Timeline slider
│    ├─ Play/Pause/Stop buttons
│    ├─ Skip buttons
│    └─ Speed selector
│
└─── ReplaySidebar
     ├─ Event statistics
     ├─ View options
     ├─ Event filter
     ├─ Player list
     └─ Event list
```

### State Management

**useReplayController Hook:**

```javascript
const {
  isPlaying,        // boolean
  currentTime,      // number (seconds)
  playbackSpeed,    // number (0.25 - 4)
  duration,         // number (seconds)
  progress,         // number (0-100 percent)
  play,             // () => void
  pause,            // () => void
  togglePlay,       // () => void
  stop,             // () => void
  seek,             // (time: number) => void
  jumpToEvent,      // (eventTime: number) => void
  skipForward,      // (seconds: number) => void
  skipBackward,     // (seconds: number) => void
  changeSpeed,      // (speed: number) => void
} = useReplayController(duration);
```

**Usage Example:**

```javascript
function MyReplayComponent() {
  const { data: timeline } = useReplayTimeline(matchId);
  const { currentTime, play, pause } = useReplayController(timeline?.duration);
  
  return (
    <div>
      <button onClick={play}>Play</button>
      <button onClick={pause}>Pause</button>
      <p>Current time: {currentTime.toFixed(2)}s</p>
    </div>
  );
}
```

### Adding a New Feature

**Example: Adding Player Speed Overlay**

1. **Fetch speed data in useReplayData.js:**
```javascript
export const usePlayerSpeeds = (matchId) => {
  return useQuery({
    queryKey: ['playerSpeeds', matchId],
    queryFn: () => analyticsApi.getPlayerMetrics(matchId).then(res => res.data),
  });
};
```

2. **Pass to ReplayPitch:**
```javascript
<ReplayPitch
  // ... existing props
  playerSpeeds={playerSpeeds}
/>
```

3. **Render in ReplayPitch.jsx:**
```javascript
// Inside player rendering loop
const speed = playerSpeeds?.[player.player_id]?.[currentTime] || 0;

<Text
  x={x + 10}
  y={y}
  text={`${speed.toFixed(1)} km/h`}
  fontSize={10}
  fill="#ffffff"
/>
```

---

## 🎨 Konva Canvas Development

### Layer Organization

Konva uses layers for efficient rendering. Static elements should be on separate layers from dynamic elements.

**Layer Strategy:**

1. **Background Layer:** Pitch markings (static, rarely updated)
2. **Events Layer:** Event arrows (semi-dynamic, updated on time change)
3. **Players Layer:** Player circles (dynamic, updated every frame)
4. **Ball Layer:** Ball circle (dynamic, updated every frame)
5. **Debug Layer:** Debug text (optional, updated every frame)

### Coordinate System

**Pitch Space (Meters):**
- X: 0 to 105 meters (length)
- Y: 0 to 68 meters (width)

**Canvas Space (Pixels):**
```javascript
const scale = Math.min(canvasWidth / 105, canvasHeight / 68);
const canvasX = offsetX + (x_meters * scale);
const canvasY = offsetY + (y_meters * scale);
```

### Performance Tips

1. **Avoid unnecessary re-renders:**
```javascript
// Bad: Creates new object every render
<Circle fill={{ r: 255, g: 0, b: 0 }} />

// Good: Use string color
<Circle fill="#FF0000" />
```

2. **Use keys for lists:**
```javascript
{players.map(player => (
  <Circle key={player.player_id} ... />
))}
```

3. **Memoize expensive calculations:**
```javascript
const playerPositions = useMemo(
  () => getPlayerPositionsAtTime(currentTime),
  [currentTime, players]
);
```

---

## 🔍 Debugging

### Backend Debugging

**Enable debug logging:**
```python
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# In service method:
logger.debug(f"Fetched {len(points)} track points")
logger.debug(f"Resampled to {len(positions)} positions at {fps} fps")
```

**Test endpoints directly:**
```bash
# Summary
curl -v http://localhost:8000/api/v1/replay/match/{MATCH_ID}/summary

# Timeline with debug
curl -v "http://localhost:8000/api/v1/replay/match/{MATCH_ID}/timeline?fps=5&start_time=0&end_time=60"
```

### Frontend Debugging

**React DevTools:**
- Install React Developer Tools extension
- Inspect component props and state
- Profile component renders

**Console Logging:**
```javascript
useEffect(() => {
  console.log('Current time:', currentTime);
  console.log('Player count:', players.length);
  console.log('Is playing:', isPlaying);
}, [currentTime, players, isPlaying]);
```

**Debug Mode:**
Enable debug mode in the UI to see:
- Track IDs
- Current time
- FPS
- Player count

---

## 🧪 Testing

### Backend Tests

**Example test:**
```python
import pytest
from app.replay.service import ReplayService

def test_resample_positions():
    service = ReplayService(db)
    
    # Create mock track points
    points = [
        TrackPoint(timestamp=0.0, x_m=10, y_m=20),
        TrackPoint(timestamp=1.0, x_m=11, y_m=21),
    ]
    
    # Resample to 10 fps
    positions = service._resample_positions(points, 0, 1, 10)
    
    assert len(positions) == 11  # 0.0, 0.1, 0.2, ..., 1.0
    assert positions[0].t == 0.0
    assert positions[0].x == 10
```

### Frontend Tests

**Example test:**
```javascript
import { renderHook, act } from '@testing-library/react-hooks';
import { useReplayController } from '../useReplayController';

test('play/pause toggle works', () => {
  const { result } = renderHook(() => useReplayController(100));
  
  expect(result.current.isPlaying).toBe(false);
  
  act(() => {
    result.current.play();
  });
  
  expect(result.current.isPlaying).toBe(true);
  
  act(() => {
    result.current.pause();
  });
  
  expect(result.current.isPlaying).toBe(false);
});
```

---

## 📊 Performance Optimization

### Backend Optimization

**Database Query Optimization:**
```python
# Bad: N+1 query problem
for track in tracks:
    points = db.query(TrackPoint).filter_by(track_id=track.id).all()

# Good: Batch fetch with JOIN
tracks_with_points = (
    db.query(Track)
    .join(TrackPoint)
    .filter(Track.match_id == match_id)
    .options(joinedload(Track.track_points))
    .all()
)
```

**Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_pitch_dimensions():
    return {"length": 105, "width": 68}
```

### Frontend Optimization

**React Query Configuration:**
```javascript
const { data } = useReplayTimeline(matchId, {
  staleTime: 10 * 60 * 1000,  // 10 minutes
  cacheTime: 30 * 60 * 1000,  // 30 minutes
  refetchOnWindowFocus: false,
});
```

**useMemo for Expensive Calculations:**
```javascript
const activeEvents = useMemo(() => {
  return events.filter(e => Math.abs(e.t - currentTime) < 2);
}, [events, currentTime]);
```

---

## 🚀 Deployment

### Production Checklist

**Backend:**
- [ ] Set `debug=False` in config
- [ ] Configure proper CORS origins
- [ ] Enable Gzip compression
- [ ] Set up database connection pooling
- [ ] Configure logging to file
- [ ] Set up error monitoring (Sentry)

**Frontend:**
- [ ] Build for production: `npm run build`
- [ ] Serve with CDN
- [ ] Enable asset compression
- [ ] Configure proper API_BASE_URL
- [ ] Set up error boundary

---

## 📚 Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Query Docs](https://tanstack.com/query/latest)
- [Konva Docs](https://konvajs.org/docs/)
- [React-Konva Docs](https://konvajs.org/docs/react/)

### Related Modules
- Phase 1: CV Pipeline (tracking data source)
- Phase 2: Physical Analytics (potential overlays)
- Phase 3: Tactical Analytics (events source)

---

## 🤝 Contributing

### Code Style

**Backend (Python):**
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions small and focused

**Frontend (JavaScript):**
- Use ES6+ syntax
- Follow Airbnb style guide
- Use functional components
- Document complex logic

### Git Workflow

1. Create feature branch: `git checkout -b feature/replay-improvements`
2. Make changes and test
3. Commit with clear message: `git commit -m "feat: add player name display"`
4. Push and create PR: `git push origin feature/replay-improvements`

---

## 🐛 Common Issues

### "No players visible"
**Cause:** Track points missing metric coordinates
**Fix:** Ensure Phase 1 pitch calibration completed successfully

### "Choppy animation"
**Cause:** Too high FPS or too many players
**Fix:** Reduce FPS to 10 or enable hardware acceleration

### "Events not showing"
**Cause:** Phase 3 events not computed
**Fix:** Ensure `compute_xt_analysis_task` completed

---

## 📞 Support

For questions or issues:
1. Check this developer guide
2. Review PHASE4_COMPLETE.md
3. Check architecture diagram in ARCHITECTURE_PHASE4.md
4. Open an issue on GitHub

---

**Happy coding! 🚀⚽**
