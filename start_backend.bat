@echo off
echo ========================================
echo  NASHAMA VISION - BACKEND SERVER
echo ========================================
echo.

cd /d "%~dp0backend"

echo Starting backend server...
echo.
echo Backend will be available at: http://127.0.0.1:8000
echo API Documentation: http://127.0.0.1:8000/docs
echo.

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
