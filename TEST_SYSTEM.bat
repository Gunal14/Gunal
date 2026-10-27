@echo off
REM AI Safety Monitoring - System Test Script
REM Windows Startup Script

cd /d "%~dp0"

echo.
echo ============================================================
echo  AI Safety Monitoring System - Quick Test
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo Running Detection System Test...
echo.

python test_detection_system.py

echo.
echo ============================================================
echo  Would you like to test with live camera? (60 seconds)
echo ============================================================
echo.
set /p live="Enter 'yes' or 'no': "

if /i "%live%"=="yes" (
    echo.
    echo Starting live camera test (60 seconds)...
    python test_detection_system.py --live
)

echo.
echo Test complete!
pause
