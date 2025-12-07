# Nashama Vision - Complete Architecture Documentation

## System Overview

Nashama Vision is a production-grade football analytics platform that uses computer vision and machine learning to analyze match videos and generate comprehensive tactical insights.

## Architecture Layers

### 1. INGESTION LAYER

**Purpose**: Handle video uploads and initial processing

**Components**:
- FastAPI endpoint (`POST /api/v1/videos/upload`)
- File validation (format, size, duration)
- Metadata extraction (OpenCV)
- Object storage upload (S3/MinIO/Local)
- Job dispatching (Celery)

**Flow**:
```
User uploads video → Validate file → Extract metadata → 
Store in S3 → Create DB record → Dispatch processing job
```

**Models**: `Video`, `Match`

---

### 2. PROCESSING LAYER (Computer Vision Pipeline)

**Purpose**: Extract tracking data from video

#### 2.1 Frame Extraction
- **Module**: `cv_pipeline/frame_extractor.py`
- **Function**: Extract frames at specified FPS
- **Technology**: OpenCV
- **Output**: Frame generator (frame_number, frame_image)

#### 2.2 Object Detection
- **Module**: `cv_pipeline/detection/detection_engine.py`
- **Model**: YOLOv8/YOLOv9
- **Classes**: Person (0), Sports Ball (32)
- **Output**: Bounding boxes, confidence scores, class labels

#### 2.3 Multi-Object Tracking
- **Module**: `cv_pipeline/tracking/tracking_engine.py`
- **Algorithm**: DeepSORT / ByteTrack
- **Function**: Maintain stable IDs across frames
- **Output**: Track ID, bounding box per frame

#### 2.4 Team Classification
- **Module**: `cv_pipeline/classification/team_classifier.py`
- **Method**: K-means clustering on jersey colors
- **Function**: Classify players into teams
- **Output**: Team assignment (home/away/referee)

#### 2.5 Pitch Calibration
- **Module**: `cv_pipeline/calibration/pitch_calibrator.py`
- **Method**: Homography transformation
- **Function**: Convert pixel coordinates to meters
- **Output**: Calibration matrix, real-world coordinates

**Flow**:
```
Video → Extract Frames → Detect Objects → Track Objects →
Classify Teams → Calibrate Pitch → Store Track Data
```

**Models**: `Track`, `TrackPoint`, `CalibrationMatrix`, `TeamColor`

---

### 3. ANALYTICS LAYER (Phase 2)

**Purpose**: Compute advanced metrics and insights

**Modules** (To be implemented):

#### 3.1 Physical Metrics
- Speed calculation
- Distance covered
- Acceleration
- Sprint count
- Stamina curve

#### 3.2 Tactical Analysis
- Formation detection
- Team compactness
- Line spacing
- Block dimensions
- Pressing intensity

#### 3.3 Expected Threat (xT)
- Grid-based threat values
- Pass detection
- Carry detection
- xT gain per action

#### 3.4 Heatmaps
- Player heatmap
- Team heatmap
- Ball possession zones
- Zone occupancy

---

### 4. PRESENTATION LAYER

**Purpose**: Expose data via API and dashboard

#### 4.1 API Gateway
- **Framework**: FastAPI
- **Endpoints**: REST API for all operations
- **Documentation**: Auto-generated (Swagger/ReDoc)
- **Authentication**: JWT (Phase 2)

#### 4.2 Dashboard (Phase 2)
- **Framework**: React + Tailwind CSS
- **Features**:
  - Match list
  - Player statistics
  - Tactical analysis views
  - Heatmap visualization
  - Video playback with annotations

#### 4.3 Virtual Match Engine (Phase 2)
- **2D Replay**: Konva.js/Canvas
- **3D Simulation**: Three.js
- **Features**: Timeline, speed control, camera angles

#### 4.4 AI Assistant (Phase 2)
- **Technology**: LLM + Vector Database
- **Function**: Natural language → SQL queries → Insights
- **Examples**: "Show me all sprints by player 10"

---

## Data Flow Diagram

```
┌─────────────────┐
│   User Upload   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Video Stored   │
│  (S3/MinIO)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Celery Worker  │
│  (Background)   │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┬──────────┐
    │          │          │          │
    ▼          ▼          ▼          ▼
┌───────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│ YOLO  │ │ Track  │ │ Classify│ │Calibrate │
│Detect │ │Objects │ │ Teams  │ │  Pitch   │
└───┬───┘ └───┬────┘ └───┬────┘ └────┬─────┘
    │         │          │           │
    └─────────┴──────────┴───────────┘
                     │
                     ▼
            ┌────────────────┐
            │  PostgreSQL    │
            │  (Track Data)  │
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │   Analytics    │
            │  Computation   │
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │   API/Frontend │
            └────────────────┘
```

---

## Database Schema

### Matches Table
```sql
- id (UUID, PK)
- name (String)
- home_team (String)
- away_team (String)
- match_date (DateTime)
- venue (String)
- competition (String)
- season (String)
- created_at (DateTime)
- updated_at (DateTime)
```

### Videos Table
```sql
- id (UUID, PK)
- match_id (UUID, FK → matches)
- filename (String)
- file_size (Integer)
- file_extension (String)
- storage_path (String)
- duration (Float)
- fps (Float)
- width (Integer)
- height (Integer)
- codec (String)
- total_frames (Integer)
- status (Enum: pending, processing, completed, failed)
- processing_started_at (DateTime)
- processing_completed_at (DateTime)
- processing_error (Text)
- created_at (DateTime)
- updated_at (DateTime)
```

### Tracks Table
```sql
- id (UUID, PK)
- video_id (UUID, FK → videos)
- track_id (Integer)
- object_class (Enum: player, ball, referee, goalkeeper)
- team_side (Enum: home, away, referee, unknown)
- player_number (Integer)
- player_name (String)
- first_frame (Integer)
- last_frame (Integer)
- total_detections (Integer)
- created_at (DateTime)
- updated_at (DateTime)
```

### TrackPoints Table
```sql
- id (UUID, PK)
- track_id (UUID, FK → tracks)
- frame_number (Integer)
- timestamp (Float)
- bbox_x1, bbox_y1, bbox_x2, bbox_y2 (Integer)
- confidence (Float)
- x_px, y_px (Float) -- pixel coordinates
- x_m, y_m (Float)   -- meter coordinates
- keypoints (JSON)
- created_at (DateTime)
```

### CalibrationMatrices Table
```sql
- id (UUID, PK)
- match_id (UUID, FK → matches)
- matrix (JSON) -- 3x3 homography matrix
- source_points (JSON)
- target_points (JSON)
- pitch_length (Float)
- pitch_width (Float)
- reprojection_error (Float)
- created_at (DateTime)
- updated_at (DateTime)
```

### TeamColors Table
```sql
- id (UUID, PK)
- match_id (UUID, FK → matches)
- team_side (Enum: home, away)
- team_name (String)
- primary_color_rgb (Array[Integer])
- secondary_color_rgb (Array[Integer])
- color_cluster_centers (JSON)
- created_at (DateTime)
- updated_at (DateTime)
```

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 14+ with SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Task Queue**: Celery + Redis
- **Storage**: S3/MinIO/Local

### Computer Vision
- **Detection**: YOLOv8/YOLOv9 (Ultralytics)
- **Tracking**: DeepSORT / ByteTrack
- **Image Processing**: OpenCV 4.9+
- **ML Framework**: PyTorch 2.1+
- **Clustering**: scikit-learn

### Infrastructure
- **Container**: Docker + Docker Compose
- **Web Server**: Uvicorn (ASGI)
- **Monitoring**: Flower (Celery), Prometheus (Phase 2)
- **Logging**: Structlog

---

## Security Architecture

### Phase 1
- CORS configuration
- Input validation (Pydantic)
- File upload validation
- SQL injection prevention (SQLAlchemy ORM)

### Phase 2 (To be implemented)
- JWT authentication
- RBAC (Role-Based Access Control)
  - Admin: Full access
  - Coach: View all, upload videos
  - Analyst: View all
  - Viewer: Limited view
- API rate limiting
- Encryption at rest
- Encryption in transit (HTTPS)

---

## Deployment Architecture

### Development
```
Local Machine
├── FastAPI (localhost:8000)
├── PostgreSQL (localhost:5432)
├── Redis (localhost:6379)
├── Celery Worker (local process)
└── Local Storage (./storage)
```

### Production
```
Cloud Infrastructure
├── Frontend: Vercel/Netlify
├── Backend API: Render/Railway/Cloud Run
├── Database: Supabase/Neon/AWS RDS
├── Cache: Redis Cloud/AWS ElastiCache
├── Storage: AWS S3/Supabase Storage
├── Worker: GPU Instance (RunPod/AWS/GCP)
└── Monitoring: Sentry + Prometheus
```

---

## Performance Considerations

### Video Processing
- **Batch Processing**: Process frames in batches for efficiency
- **GPU Acceleration**: Use CUDA for YOLO inference
- **Async I/O**: Non-blocking file operations
- **Queue Management**: Separate queues for priority jobs

### Database
- **Indexes**: On video_id, track_id, frame_number
- **Connection Pooling**: SQLAlchemy connection pool
- **Partitioning**: Consider partitioning track_points by video_id

### API
- **Caching**: Redis caching for frequently accessed data
- **Pagination**: Limit query results
- **Rate Limiting**: Prevent abuse

---

## Monitoring & Observability

### Metrics (Phase 2)
- API response times
- Video processing times
- Queue lengths
- Error rates
- Database query performance

### Logging
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log aggregation (ELK stack / CloudWatch)

### Alerts
- Processing failures
- Queue backlog
- Database connection issues
- Storage capacity

---

## Scaling Strategy

### Horizontal Scaling
- Multiple API instances behind load balancer
- Multiple Celery workers for parallel processing
- Database read replicas

### Vertical Scaling
- GPU workers for CV processing
- Database optimization (indexes, queries)
- Redis clustering

---

## Phase Roadmap

### ✅ Phase 1 (Current)
- Video ingestion
- CV pipeline skeleton
- Database models
- Basic API

### 🔄 Phase 2 (Next)
- Analytics computation
- Heatmap generation
- Frontend dashboard
- Authentication

### 🔮 Phase 3 (Future)
- Real-time processing
- Advanced AI assistant
- Multi-camera support
- Mobile app

---

## API Reference

See `README.md` for complete API documentation and examples.

---

## Contributing

See `CONTRIBUTING.md` for development guidelines and code standards.
