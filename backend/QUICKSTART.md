# 🚀 Nashama Vision - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- Git

## Option 1: Docker (Fastest - Recommended)

### Step 1: Start Services
```bash
cd backend
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- MinIO (ports 9000, 9001)
- FastAPI Backend (port 8000)
- Celery Worker
- Flower (port 5555)

### Step 2: Run Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### Step 3: Access Services
- **API Docs**: http://localhost:8000/api/docs
- **API Health**: http://localhost:8000/health
- **Flower (Tasks)**: http://localhost:5555
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

### Step 4: Test Upload

Using the interactive docs at http://localhost:8000/api/docs:

1. Create a match:
   ```json
   POST /api/v1/matches
   {
     "name": "Test Match",
     "home_team": "Team A",
     "away_team": "Team B"
   }
   ```

2. Upload video:
   ```
   POST /api/v1/videos/upload
   match_id: <uuid-from-step-1>
   file: <select-video-file>
   ```

3. Check processing:
   ```
   GET /api/v1/videos/{video_id}/status
   ```

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f celery-worker
```

### Stop Services
```bash
docker-compose down
```

---

## Option 2: Local Development

### Step 1: Setup Environment
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Setup Services

**PostgreSQL:**
```bash
docker run -d --name nashama-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=nashama_vision \
  -p 5432:5432 postgres:14
```

**Redis:**
```bash
docker run -d --name nashama-redis -p 6379:6379 redis:6-alpine
```

### Step 3: Configure Environment
```bash
cp .env.example .env

# Edit .env:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/nashama_vision
# REDIS_URL=redis://localhost:6379/0
# STORAGE_TYPE=local
```

### Step 4: Run Migrations
```bash
alembic upgrade head
```

### Step 5: Start Services

**Terminal 1 - API Server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
celery -A app.workers.worker worker --loglevel=info --pool=solo
```

**Terminal 3 - Flower (Optional):**
```bash
celery -A app.workers.worker flower --port=5555
```

### Step 6: Access Services
- **API Docs**: http://localhost:8000/api/docs
- **Flower**: http://localhost:5555

---

## 🧪 Test the System

### Using cURL

1. **Create Match:**
```bash
curl -X POST "http://localhost:8000/api/v1/matches" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Match",
    "home_team": "Team A",
    "away_team": "Team B",
    "match_date": "2024-01-01T15:00:00"
  }'
```

2. **Upload Video:**
```bash
curl -X POST "http://localhost:8000/api/v1/videos/upload" \
  -F "match_id=<MATCH_ID>" \
  -F "file=@/path/to/video.mp4"
```

3. **Check Status:**
```bash
curl "http://localhost:8000/api/v1/videos/<VIDEO_ID>/status"
```

4. **List Videos:**
```bash
curl "http://localhost:8000/api/v1/videos"
```

### Using Python

```python
import requests

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# 1. Create match
match_data = {
    "name": "Test Match",
    "home_team": "Team A",
    "away_team": "Team B"
}
response = requests.post(f"{BASE_URL}/matches", json=match_data)
match = response.json()
match_id = match["id"]

# 2. Upload video
files = {"file": open("match_video.mp4", "rb")}
data = {"match_id": match_id}
response = requests.post(f"{BASE_URL}/videos/upload", files=files, data=data)
video = response.json()
video_id = video["video_id"]

# 3. Check processing status
response = requests.get(f"{BASE_URL}/videos/{video_id}/status")
status = response.json()
print(f"Status: {status['status']}")

# 4. Get tracks (after processing completes)
response = requests.get(f"{BASE_URL}/tracks/video/{video_id}")
tracks = response.json()
print(f"Total tracks: {len(tracks)}")
```

---

## 🎯 What to Try

### 1. Upload a Video
- Use any football match video (MP4, AVI, MOV, MKV)
- Minimum 60 seconds, maximum 2 hours
- Max file size: 5GB

### 2. Monitor Processing
- Watch logs in terminal
- Check Flower dashboard
- Query video status endpoint

### 3. Retrieve Data
- Get list of tracks
- View track points
- Filter by object class (player/ball)

### 4. Explore API
- Interactive docs: http://localhost:8000/api/docs
- Try all endpoints
- View request/response schemas

---

## 🐛 Troubleshooting

### Docker Issues

**Services won't start:**
```bash
docker-compose down -v
docker-compose up -d
```

**Check service health:**
```bash
docker-compose ps
docker-compose logs backend
```

**Reset everything:**
```bash
docker-compose down -v
docker volume prune -f
docker-compose up -d
```

### Database Issues

**Connection refused:**
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Check port 5432 is available

**Migration errors:**
```bash
# Downgrade and re-upgrade
alembic downgrade base
alembic upgrade head
```

### Redis Issues

**Connection refused:**
- Check Redis is running
- Verify REDIS_URL in .env
- Test: `redis-cli ping`

### Celery Issues

**Worker not processing:**
```bash
# Check worker status
celery -A app.workers.worker inspect active

# Purge queue
celery -A app.workers.worker purge
```

### YOLO Model Issues

**Model not found:**
The model auto-downloads on first use. If it fails:
```bash
mkdir models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8x.pt -O models/yolov8x.pt
```

---

## 📚 Next Steps

1. ✅ **System is running** - Test with sample video
2. 📖 **Read README.md** - Complete documentation
3. 🏗️ **Read ARCHITECTURE.md** - Understand system design
4. 🔧 **Extend functionality** - Add custom features
5. 🚀 **Deploy to production** - Follow deployment guide

---

## 💡 Tips

- **Use Swagger UI** for testing (http://localhost:8000/api/docs)
- **Monitor with Flower** for task visibility
- **Check logs** for debugging
- **Start with small videos** for faster testing
- **Use local storage** for development

---

## 🎓 Learning Path

1. Upload a video and watch it process
2. Check database for created records
3. Explore track data structure
4. Modify CV pipeline parameters
5. Add custom analytics (Phase 2)

---

**Need Help?**
- Check logs: `docker-compose logs -f`
- API docs: http://localhost:8000/api/docs
- Architecture: Read ARCHITECTURE.md

**Ready to build amazing football analytics!** 🚀⚽
