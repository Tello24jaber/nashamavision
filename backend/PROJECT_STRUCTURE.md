# 📁 Nashama Vision - Complete Project Structure

## Backend Directory Tree

```
backend/
│
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 alembic.ini                  # Alembic configuration
├── 📄 docker-compose.yml           # Multi-container deployment
├── 📄 Dockerfile                   # Backend container definition
├── 📄 requirements.txt             # Python dependencies
│
├── 📄 README.md                    # Main documentation
├── 📄 ARCHITECTURE.md              # System architecture details
├── 📄 PHASE1_COMPLETE.md           # Phase 1 completion summary
├── 📄 QUICKSTART.md                # Quick start guide
├── 📄 PROJECT_STRUCTURE.md         # This file
│
├── 📁 alembic/                     # Database Migrations
│   ├── 📄 env.py                   # Alembic environment config
│   ├── 📄 script.py.mako           # Migration template
│   └── 📁 versions/                # Migration versions
│       └── 📄 001_initial_schema.py
│
├── 📁 app/                         # Main Application
│   │
│   ├── 📄 __init__.py
│   ├── 📄 main.py                  # FastAPI application entry
│   │
│   ├── 📁 api/                     # API Layer
│   │   ├── 📄 __init__.py
│   │   └── 📁 routers/             # Route Handlers
│   │       ├── 📄 __init__.py
│   │       ├── 📄 matches.py       # Match CRUD endpoints
│   │       ├── 📄 videos.py        # Video upload & management
│   │       ├── 📄 tracks.py        # Track data retrieval
│   │       └── 📄 processing.py    # Background job control
│   │
│   ├── 📁 core/                    # Core Configuration
│   │   ├── 📄 __init__.py
│   │   └── 📄 config.py            # Settings & environment vars
│   │
│   ├── 📁 db/                      # Database Layer
│   │   ├── 📄 __init__.py
│   │   └── 📄 session.py           # SQLAlchemy session management
│   │
│   ├── 📁 models/                  # Database Models
│   │   ├── 📄 __init__.py
│   │   └── 📄 models.py            # SQLAlchemy ORM models
│   │       ├── Match
│   │       ├── Video
│   │       ├── Track
│   │       ├── TrackPoint
│   │       ├── CalibrationMatrix
│   │       └── TeamColor
│   │
│   ├── 📁 schemas/                 # Pydantic Schemas
│   │   ├── 📄 __init__.py
│   │   └── 📄 schemas.py           # Request/response validation
│   │       ├── MatchCreate/Response
│   │       ├── VideoUpload/Response
│   │       ├── TrackResponse
│   │       └── ProcessingJobResponse
│   │
│   ├── 📁 services/                # Business Logic
│   │   ├── 📄 __init__.py
│   │   └── 📄 video_service.py     # Video processing logic
│   │
│   ├── 📁 cv_pipeline/             # Computer Vision Pipeline
│   │   ├── 📄 __init__.py
│   │   ├── 📄 frame_extractor.py   # Extract frames from video
│   │   │
│   │   ├── 📁 detection/           # Object Detection
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 detection_engine.py  # YOLO detection
│   │   │
│   │   ├── 📁 tracking/            # Multi-Object Tracking
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 tracking_engine.py   # DeepSORT/ByteTrack
│   │   │
│   │   ├── 📁 classification/      # Team Classification
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 team_classifier.py   # K-means color clustering
│   │   │
│   │   └── 📁 calibration/         # Pitch Calibration
│   │       ├── 📄 __init__.py
│   │       └── 📄 pitch_calibrator.py  # Homography transformation
│   │
│   ├── 📁 storage/                 # Storage Abstraction
│   │   ├── 📄 __init__.py
│   │   └── 📄 storage_interface.py # S3/MinIO/Local storage
│   │
│   └── 📁 workers/                 # Background Tasks
│       ├── 📄 __init__.py
│       ├── 📄 celery_app.py        # Celery configuration
│       ├── 📄 tasks.py             # Task definitions
│       │   ├── process_video_task
│       │   └── analytics_computation_task
│       └── 📄 worker.py            # Worker entry point
│
├── 📁 logs/                        # Application Logs
│   └── 📄 .gitkeep
│
├── 📁 models/                      # ML Model Weights
│   └── 📄 .gitkeep                 # (yolov8x.pt goes here)
│
├── 📁 storage/                     # Local File Storage
│   └── 📄 .gitkeep                 # (videos stored here in dev)
│
└── 📁 tests/                       # Unit & Integration Tests
    └── 📄 (to be added)

```

## Directory Purpose

### `/app` - Main Application
Core application code following clean architecture principles.

### `/app/api/routers` - API Endpoints
RESTful API route handlers organized by resource:
- **matches.py** - Match CRUD operations
- **videos.py** - Video upload, list, status
- **tracks.py** - Track data queries
- **processing.py** - Job management

### `/app/core` - Configuration
Application settings and environment management using Pydantic.

### `/app/db` - Database Layer
SQLAlchemy session management and connection pooling.

### `/app/models` - ORM Models
Database table definitions with relationships and constraints.

### `/app/schemas` - Data Validation
Pydantic schemas for request/response validation and serialization.

### `/app/services` - Business Logic
Service layer containing business rules and orchestration.

### `/app/cv_pipeline` - Computer Vision
Modular CV components for video analysis:
- **frame_extractor** - Extract frames at target FPS
- **detection** - YOLO object detection
- **tracking** - DeepSORT/ByteTrack multi-object tracking
- **classification** - Team identification via color
- **calibration** - Pixel-to-meter coordinate transformation

### `/app/storage` - Storage Interface
Abstraction layer supporting multiple storage backends (S3, MinIO, Local).

### `/app/workers` - Background Jobs
Celery tasks for async video processing and analytics computation.

### `/alembic` - Database Migrations
Version-controlled database schema changes using Alembic.

### `/logs` - Application Logs
Structured logging output for debugging and monitoring.

### `/models` - ML Weights
YOLO model weights (auto-downloaded or manually placed).

### `/storage` - Local Storage
Development storage for videos when using local backend.

### `/tests` - Test Suite
Unit tests, integration tests, and fixtures.

## File Count Summary

```
Total Files: 45+
- Python Files: 28
- Config Files: 5
- Documentation: 5
- Docker Files: 2
- Other: 5+
```

## Key Files

### Entry Points
- `app/main.py` - FastAPI application
- `app/workers/worker.py` - Celery worker

### Configuration
- `.env.example` - Environment template
- `app/core/config.py` - Settings management
- `alembic.ini` - Migration config

### Core Logic
- `app/services/video_service.py` - Video processing
- `app/workers/tasks.py` - Background tasks
- `app/models/models.py` - Database schema

### CV Pipeline
- `app/cv_pipeline/frame_extractor.py` - Frame extraction
- `app/cv_pipeline/detection/detection_engine.py` - Object detection
- `app/cv_pipeline/tracking/tracking_engine.py` - Object tracking
- `app/cv_pipeline/classification/team_classifier.py` - Team identification
- `app/cv_pipeline/calibration/pitch_calibrator.py` - Camera calibration

### API Routes
- `app/api/routers/matches.py` - Match management
- `app/api/routers/videos.py` - Video operations
- `app/api/routers/tracks.py` - Track queries
- `app/api/routers/processing.py` - Job control

## Module Dependencies

```
main.py
├── api/routers/*
│   ├── models/*
│   ├── schemas/*
│   └── services/*
├── core/config.py
├── db/session.py
└── workers/tasks.py

workers/tasks.py
├── cv_pipeline/*
├── storage/*
├── models/*
└── db/session.py

cv_pipeline/*
├── detection/
├── tracking/
├── classification/
└── calibration/
```

## Import Hierarchy

```
Level 1: core, db
Level 2: models, schemas
Level 3: services, cv_pipeline, storage
Level 4: api/routers, workers
Level 5: main
```

## Technology Stack by Directory

### `/app/core`
- Pydantic v2
- python-dotenv

### `/app/db`
- SQLAlchemy 2.0
- psycopg2-binary
- Alembic

### `/app/api`
- FastAPI 0.109
- Uvicorn

### `/app/cv_pipeline`
- OpenCV 4.9
- Ultralytics (YOLO)
- PyTorch 2.1
- scikit-learn
- NumPy

### `/app/workers`
- Celery 5.3
- Redis 5.0

### `/app/storage`
- boto3 (S3)
- aiofiles

## Design Patterns Used

1. **Repository Pattern** - Database access through models
2. **Service Layer** - Business logic separation
3. **Dependency Injection** - FastAPI Depends()
4. **Factory Pattern** - Storage interface creation
5. **Strategy Pattern** - Multiple tracking algorithms
6. **Abstract Interface** - Storage abstraction
7. **Task Queue Pattern** - Celery background jobs

## Code Organization Principles

✅ **Separation of Concerns** - Each module has single responsibility
✅ **Dependency Inversion** - High-level modules don't depend on low-level
✅ **Interface Segregation** - Clients don't depend on unused interfaces
✅ **DRY (Don't Repeat Yourself)** - Reusable components
✅ **SOLID Principles** - Object-oriented best practices
✅ **Clean Architecture** - Layered structure with clear boundaries

## Next Steps

1. Review structure: `tree /F backend` (Windows) or `tree backend` (Linux/Mac)
2. Explore main.py to understand application flow
3. Check models.py for database schema
4. Review tasks.py for processing pipeline
5. Read routers/* for API endpoints

---

**This structure supports:**
- Easy testing (clear dependencies)
- Simple deployment (containerized)
- Future scaling (modular design)
- Team collaboration (organized structure)
- Code maintenance (clear responsibilities)
