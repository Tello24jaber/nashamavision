# Nashama Vision Backend - Phase 1

Production-grade football analytics platform backend built with FastAPI, Computer Vision (YOLO), and Celery.

## 🏗️ Architecture Overview

Phase 1 includes:

1. **Video Ingestion Layer** - FastAPI endpoints for video upload with validation
2. **Computer Vision Pipeline** - YOLO detection + DeepSORT tracking + team classification
3. **Database Layer** - PostgreSQL with SQLAlchemy models and Alembic migrations
4. **Object Storage** - S3/MinIO/Local storage integration
5. **Background Processing** - Celery workers for async video processing
6. **RESTful API** - Complete CRUD operations for matches, videos, and tracks

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routers/          # API route handlers
│   │       ├── matches.py    # Match CRUD endpoints
│   │       ├── videos.py     # Video upload & management
│   │       ├── tracks.py     # Track data retrieval
│   │       └── processing.py # Background job management
│   ├── core/
│   │   └── config.py         # Application configuration
│   ├── db/
│   │   └── session.py        # Database session management
│   ├── models/
│   │   └── models.py         # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── schemas.py        # Pydantic validation schemas
│   ├── services/
│   │   └── video_service.py  # Business logic layer
│   ├── cv_pipeline/          # Computer Vision modules
│   │   ├── frame_extractor.py      # Frame extraction from video
│   │   ├── detection/
│   │   │   └── detection_engine.py # YOLO object detection
│   │   ├── tracking/
│   │   │   └── tracking_engine.py  # Multi-object tracking
│   │   ├── classification/
│   │   │   └── team_classifier.py  # Team color classification
│   │   └── calibration/
│   │       └── pitch_calibrator.py # Pixel-to-meter calibration
│   ├── storage/
│   │   └── storage_interface.py    # Storage abstraction layer
│   ├── workers/
│   │   ├── celery_app.py     # Celery configuration
│   │   ├── tasks.py          # Background tasks
│   │   └── worker.py         # Worker entry point
│   └── main.py               # FastAPI application
├── alembic/
│   ├── versions/             # Database migrations
│   └── env.py                # Alembic environment
├── tests/                    # Unit and integration tests
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
├── alembic.ini              # Alembic configuration
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd nashamavision/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Key variables to configure:
# - DATABASE_URL
# - REDIS_URL
# - STORAGE_TYPE (local/s3/minio)
# - SECRET_KEY
```

### 5. Setup Database

```bash
# Start PostgreSQL (if using Docker)
docker run -d \
  --name nashama-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=nashama_vision \
  -p 5432:5432 \
  postgres:14

# Run migrations
alembic upgrade head
```

### 6. Setup Redis

```bash
# Start Redis (if using Docker)
docker run -d \
  --name nashama-redis \
  -p 6379:6379 \
  redis:6-alpine
```

### 7. Download YOLO Model

```bash
# Create models directory
mkdir -p models

# The model will auto-download on first use, or manually:
# Download YOLOv8x from: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8x.pt
# Place in: models/yolov8x.pt
```

### 8. Run Application

#### Start API Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Start Celery Worker

```bash
# In a separate terminal
celery -A app.workers.worker worker --loglevel=info --pool=solo

# For GPU processing (requires CUDA)
celery -A app.workers.worker worker --loglevel=info --concurrency=1
```

#### Start Flower (Celery Monitoring - Optional)

```bash
celery -A app.workers.worker flower --port=5555
```

## 📡 API Documentation

Once running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 🔑 Key Endpoints

### Matches

- `POST /api/v1/matches` - Create match
- `GET /api/v1/matches` - List matches
- `GET /api/v1/matches/{id}` - Get match details
- `PATCH /api/v1/matches/{id}` - Update match
- `DELETE /api/v1/matches/{id}` - Delete match

### Videos

- `POST /api/v1/videos/upload` - Upload video
- `GET /api/v1/videos` - List videos
- `GET /api/v1/videos/{id}` - Get video details
- `GET /api/v1/videos/{id}/status` - Get processing status
- `DELETE /api/v1/videos/{id}` - Delete video

### Processing

- `POST /api/v1/processing/start/{video_id}` - Start processing
- `GET /api/v1/processing/status/{job_id}` - Check job status
- `POST /api/v1/processing/retry/{video_id}` - Retry failed processing

### Tracks

- `GET /api/v1/tracks/video/{video_id}` - Get all tracks for video
- `GET /api/v1/tracks/{track_id}` - Get track details with points
- `GET /api/v1/tracks/{track_id}/points` - Get track points

## 🗄️ Database Models

### Core Models

1. **Match** - Football match information
2. **Video** - Uploaded video metadata
3. **Track** - Tracked object (player/ball)
4. **TrackPoint** - Frame-by-frame position data
5. **CalibrationMatrix** - Camera calibration for pixel→meter
6. **TeamColor** - Team color information for classification

### Relationships

- Match → Videos (one-to-many)
- Video → Tracks (one-to-many)
- Track → TrackPoints (one-to-many)
- Match → CalibrationMatrices (one-to-many)
- Match → TeamColors (one-to-many)

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nashama_vision

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# Storage
STORAGE_TYPE=local  # local, s3, minio
LOCAL_STORAGE_PATH=./storage
S3_BUCKET_NAME=nashama-vision-storage

# Computer Vision
YOLO_MODEL_PATH=./models/yolov8x.pt
YOLO_CONFIDENCE_THRESHOLD=0.5
TRACKING_METHOD=deepsort

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000

# Upload Limits
MAX_UPLOAD_SIZE=5368709120  # 5GB
MIN_VIDEO_DURATION=60       # seconds
MAX_VIDEO_DURATION=7200     # seconds
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_video_service.py
```

## 📦 Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure strong `SECRET_KEY`
- [ ] Setup production database (not SQLite)
- [ ] Configure S3/MinIO for storage
- [ ] Setup Redis with persistence
- [ ] Configure CORS origins
- [ ] Enable HTTPS
- [ ] Setup monitoring (Sentry, Prometheus)
- [ ] Configure log aggregation
- [ ] Setup automated backups
- [ ] Configure rate limiting
- [ ] Setup GPU worker for CV processing

## 🔍 Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
psql -h localhost -U user -d nashama_vision
```

### Redis Connection Issues

```bash
# Check Redis is running
docker ps | grep redis

# Test connection
redis-cli ping
```

### YOLO Model Not Found

The model will auto-download on first use. If issues occur:

```bash
# Manual download
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8x.pt -O models/yolov8x.pt
```

### Celery Worker Not Processing

```bash
# Check worker is running
celery -A app.workers.worker inspect active

# Purge all tasks
celery -A app.workers.worker purge

# Check Redis queue
redis-cli llen celery
```

## 📚 Next Steps (Phase 2)

- [ ] Analytics computation (speed, distance, acceleration)
- [ ] Tactical analysis (formations, compactness)
- [ ] Expected Threat (xT) computation
- [ ] Heatmap generation
- [ ] Frontend dashboard (React)
- [ ] Virtual match engine (2D/3D replay)
- [ ] AI assistant (LLM integration)
- [ ] User authentication & RBAC
- [ ] Report generation
- [ ] Real-time processing dashboard

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines]

## 📞 Support

[Add support contact information]
