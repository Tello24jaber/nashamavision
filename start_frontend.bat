@echo off
echo ========================================
echo  NASHAMA VISION - FRONTEND SERVER
echo ========================================
echo.

cd /d "%~dp0frontend"

echo Starting frontend development server...
echo.
echo Frontend will be available at: http://localhost:5173
echo.

call npm run dev
