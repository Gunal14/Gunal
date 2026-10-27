@echo off
REM Professional CCTV Safety Monitoring System - Windows Launcher
REM This script starts the complete CCTV system with web dashboard

cls
echo.
echo ========================================================================
echo  PROFESSIONAL CCTV SAFETY MONITORING SYSTEM - Windows Launcher
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo Python is installed and available.
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated.
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo Note: No virtual environment found. Using system Python.
)

echo.
echo ========================================================================
echo Checking dependencies...
echo ========================================================================
echo.

REM Check required packages
python -c "import cv2" >nul 2>&1
if errorlevel 1 (
    echo WARNING: OpenCV (cv2) not installed
    echo Installing: pip install opencv-python
    pip install opencv-python
)

python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Flask not installed
    echo Installing: pip install flask
    pip install flask
)

python -c "import flask_cors" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Flask-CORS not installed  
    echo Installing: pip install flask-cors
    pip install flask-cors
)

echo.
echo ========================================================================
echo CCTV System Ready!
echo ========================================================================
echo.
echo Starting Professional CCTV Safety Monitoring System...
echo.
echo URL: http://localhost:5000
echo.
echo Press Ctrl+C to stop the system
echo.
echo ========================================================================
echo.

REM Start the CCTV system with web dashboard
python start_cctv.py --web --port 5000

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start CCTV system
    echo Check that all dependencies are installed
    pause
    exit /b 1
)

pause
