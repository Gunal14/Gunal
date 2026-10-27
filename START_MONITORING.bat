@echo off
REM AI Safety Monitoring - Real-Time Helmet Detection
REM Windows Startup Script

cd /d "%~dp0"

echo.
echo ============================================================
echo  AI Safety Monitoring System - Real-Time Helmet Detection
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [OK] Python found
echo [OK] Starting Real-Time Monitoring System
echo.
echo.

python real_time_monitoring.py

pause
