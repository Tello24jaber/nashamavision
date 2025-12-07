@echo off
echo ========================================
echo  Nashama Vision - Local Development
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend\app\main.py" (
    echo ERROR: Please run this script from the project root directory
    echo Expected to find: backend\app\main.py
    pause
    exit /b 1
)

echo [1/3] Starting Backend Server...
echo.
start "Backend - Nashama Vision" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend Server...
echo.
start "Frontend - Nashama Vision" cmd /k "cd frontend && npm run dev"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo  Servers Started!
echo ========================================
echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Press any key to stop all servers...
pause >nul

echo.
echo Stopping servers...
taskkill /FI "WindowTitle eq Backend - Nashama Vision*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Frontend - Nashama Vision*" /T /F >nul 2>&1

echo Servers stopped.
pause
