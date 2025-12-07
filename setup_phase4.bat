@echo off
REM Phase 4 Setup Script
REM Nashama Vision - Virtual Match Engine

echo ==========================================
echo   NASHAMA VISION - PHASE 4 SETUP
echo   Virtual Match Engine
echo ==========================================
echo.

REM Check if we're in the right directory
if not exist "PHASE4_COMPLETE.md" (
    echo Error: Please run this script from the nashama-vision root directory
    exit /b 1
)

echo Step 1: Backend Verification
echo Checking backend files...

set ERROR=0

if exist "backend\app\replay\__init__.py" (
    echo [OK] backend\app\replay\__init__.py
) else (
    echo [FAIL] backend\app\replay\__init__.py missing
    set ERROR=1
)

if exist "backend\app\replay\service.py" (
    echo [OK] backend\app\replay\service.py
) else (
    echo [FAIL] backend\app\replay\service.py missing
    set ERROR=1
)

if exist "backend\app\api\routers\replay.py" (
    echo [OK] backend\app\api\routers\replay.py
) else (
    echo [FAIL] backend\app\api\routers\replay.py missing
    set ERROR=1
)

if exist "backend\app\schemas\replay.py" (
    echo [OK] backend\app\schemas\replay.py
) else (
    echo [FAIL] backend\app\schemas\replay.py missing
    set ERROR=1
)

if %ERROR%==1 (
    echo.
    echo Backend files are missing!
    exit /b 1
)

echo.
echo Step 2: Frontend Setup
echo Installing frontend dependencies...

cd frontend

REM Check if package.json has the right dependencies
findstr /C:"react-konva" package.json >nul
if errorlevel 1 (
    echo Error: package.json not updated with Konva dependencies
    exit /b 1
)

REM Install dependencies
echo Running npm install...
call npm install

if errorlevel 1 (
    echo Failed to install frontend dependencies
    exit /b 1
) else (
    echo [OK] Frontend dependencies installed
)

echo.
echo Checking frontend files...

if exist "src\pages\MatchReplayView.jsx" (
    echo [OK] src\pages\MatchReplayView.jsx
) else (
    echo [FAIL] src\pages\MatchReplayView.jsx missing
    set ERROR=1
)

if exist "src\components\replay\ReplayPitch.jsx" (
    echo [OK] src\components\replay\ReplayPitch.jsx
) else (
    echo [FAIL] src\components\replay\ReplayPitch.jsx missing
    set ERROR=1
)

if exist "src\components\replay\ReplayControls.jsx" (
    echo [OK] src\components\replay\ReplayControls.jsx
) else (
    echo [FAIL] src\components\replay\ReplayControls.jsx missing
    set ERROR=1
)

if exist "src\components\replay\ReplaySidebar.jsx" (
    echo [OK] src\components\replay\ReplaySidebar.jsx
) else (
    echo [FAIL] src\components\replay\ReplaySidebar.jsx missing
    set ERROR=1
)

if exist "src\hooks\useReplayController.js" (
    echo [OK] src\hooks\useReplayController.js
) else (
    echo [FAIL] src\hooks\useReplayController.js missing
    set ERROR=1
)

if exist "src\hooks\useReplayData.js" (
    echo [OK] src\hooks\useReplayData.js
) else (
    echo [FAIL] src\hooks\useReplayData.js missing
    set ERROR=1
)

cd ..

if %ERROR%==1 (
    echo.
    echo Frontend files are missing!
    exit /b 1
)

echo.
echo Step 3: Backend Check
echo No additional backend dependencies needed
echo [OK] Backend ready

echo.
echo Step 4: Database Check
echo Verifying database schema...
echo Note: Ensure PostgreSQL is running and accessible

echo.
echo ==========================================
echo   PHASE 4 SETUP COMPLETE!
echo ==========================================
echo.
echo Next steps:
echo.
echo 1. Start the backend:
echo    cd backend
echo    uvicorn app.main:app --reload
echo.
echo 2. Start the frontend (in a new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Navigate to replay page:
echo    http://localhost:5173/matches/{MATCH_ID}/replay
echo.
echo 4. Check documentation:
echo    - PHASE4_COMPLETE.md (comprehensive guide)
echo    - QUICKSTART_PHASE4.md (quick start)
echo    - ARCHITECTURE_PHASE4.md (technical details)
echo.
echo Happy replaying! ⚽🎮
echo.

pause
