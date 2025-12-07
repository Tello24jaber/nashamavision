# 🚀 Quick Start Guide - Windows

## ✅ Prerequisites
- Python 3.11+
- Node.js 18+
- **Supabase Account** (Free tier works!)

---

## 📝 Step-by-Step Setup

### 1️⃣ **Get Your Supabase Database** (2 minutes)

1. Go to https://supabase.com and sign up (free)
2. Create a new project
3. Wait for database to provision (~2 minutes)
4. Go to **Settings** → **Database**
5. Scroll to **Connection String** → **URI**
6. Copy the connection string (looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`)

### 2️⃣ **Configure Backend**

Open `backend\.env` and replace `YOUR_PASSWORD_HERE` and `YOUR_PROJECT_REF` with your actual values:

```env
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@db.YOUR_ACTUAL_REF.supabase.co:5432/postgres
```

**Example:**
```env
DATABASE_URL=postgresql://postgres:MyPass123@db.abcdefghijk.supabase.co:5432/postgres
```

### 3️⃣ **Start the Application**

#### Option A: Automatic (Easiest) ⭐
Double-click: **`start-dev.bat`**

This opens two terminal windows:
- **Backend:** http://127.0.0.1:8000
- **Frontend:** http://localhost:5173

#### Option B: Manual
```powershell
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

---

## 🌐 Access the Application

- **Frontend UI:** http://localhost:5173
- **Backend API:** http://127.0.0.1:8000
- **API Documentation:** http://127.0.0.1:8000/docs
- **Health Check:** http://127.0.0.1:8000/api/v1/health

---

## 🐛 Troubleshooting

### Backend won't start?

**Error: "ModuleNotFoundError: No module named 'app'"**
- Make sure you're in the `backend` directory when running uvicorn
- Or set PYTHONPATH: `$env:PYTHONPATH="C:\Users\hp\.m2\nashamavision\backend"`

**Error: "connection refused" or "can't connect to database"**
- Check your DATABASE_URL in `.env`
- Verify Supabase project is running (green dot in dashboard)
- Make sure password doesn't have special characters (use URL encoding if needed)

**Error: "ARRAY type not supported"**
- This means you're still using SQLite - update DATABASE_URL to use Supabase PostgreSQL

### Frontend won't start?

**Error: "npm: command not found"**
- Install Node.js from https://nodejs.org/

**Error: "Cannot find module"**
- Run: `cd frontend && npm install`

**Warning about "entry point"**
- This is harmless, frontend will work fine

---

## 📊 Test Data

The database will be empty initially. To test:

1. Go to **http://127.0.0.1:8000/docs**
2. Use the API to create a match
3. Upload a video
4. View results in the frontend

---

## 🔧 Environment Variables

### Backend (`.env`)
```env
# Database (REQUIRED)
DATABASE_URL=postgresql://...          # Your Supabase connection string

# Environment
ENVIRONMENT=development
DEBUG=true

# Storage
STORAGE_TYPE=local                     # or 's3' for production
LOCAL_STORAGE_PATH=./storage

# AI Assistant (Optional)
LLM_PROVIDER=mock                      # or 'openai', 'anthropic'
LLM_API_KEY=                          # if using real LLM
LLM_MODEL=mock-model

# Redis/Celery (Optional - for background tasks)
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Frontend
Automatically connects to backend at `http://127.0.0.1:8000`

---

## ✅ Verify Everything Works

### 1. Check Backend Health
Visit: http://127.0.0.1:8000/api/v1/health
Should see:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Check Frontend
Visit: http://localhost:5173
Should see the Nashama Vision dashboard

### 3. Check API Docs
Visit: http://127.0.0.1:8000/docs
Should see interactive Swagger UI

---

## 🎯 What's Working?

✅ **Backend API** (28 tests passing)
- Match management
- Video upload/processing
- Analytics endpoints
- AI Assistant
- Replay system

✅ **Frontend**
- Dashboard
- Match list/details
- Player metrics
- Heatmaps
- Event timeline
- AI Assistant chat

✅ **Database**
- All tables created automatically
- Migrations managed by Alembic

---

## 📦 Production Deployment

See `QUICKSTART_PHASE6.md` for:
- Docker deployment
- Azure deployment
- Environment configuration

---

## 💡 Tips

1. **Keep terminals open** while developing - they auto-reload on code changes
2. **Check the terminal output** for errors
3. **Use API docs** at `/docs` to test endpoints
4. **Supabase dashboard** to view your database tables

---

## ❓ Need Help?

- Backend logs: Check the terminal running uvicorn
- Frontend logs: Check browser console (F12)
- Database: Check Supabase dashboard
- API issues: Try endpoints at http://127.0.0.1:8000/docs

---

**You're all set! 🎉**
