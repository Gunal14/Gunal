#!/usr/bin/env python3
"""
Complete Setup Script for Enhanced Employee Recognition Safety System
Run this script to set up the entire system from scratch
Usage: python complete_setup.py
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description, cwd=None):
    """Run a shell command and log the output"""
    logger.info(f"🔧 {description}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            logger.info(f"✅ {description} completed successfully")
            return True
        else:
            logger.error(f"❌ {description} failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"❌ {description} timed out")
        return False
    except Exception as e:
        logger.error(f"❌ {description} error: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        logger.error(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Need Python 3.8+")
        return False

def install_dependencies():
    """Install all required Python packages"""
    logger.info("📦 Installing Python dependencies...")

    # Update pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        return False

    # Install core dependencies
    requirements = [
        "Flask==2.3.2",
        "Flask-CORS==4.0.0",
        "Flask-SQLAlchemy==3.0.5",
        "SQLAlchemy==1.4.52",
        "PyJWT==2.8.0",
        "opencv-python==4.13.0.92",
        "numpy==2.4.3",
        "face-recognition==1.3.0",
        "Pillow==10.0.0",
        "scikit-image==0.22.0",
        "pandas==2.0.3",
        "Flask-Mail==0.9.1",
        "python-dateutil==2.8.2",
        "flask-jwt-extended==4.5.2",
        "bcrypt==4.0.1",
        "werkzeug==2.3.6"
    ]

    # Install packages one by one to handle failures gracefully
    failed_packages = []
    for package in requirements:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            failed_packages.append(package)

    if failed_packages:
        logger.warning(f"⚠️  Some packages failed to install: {failed_packages}")
        logger.info("Trying alternative installation method...")

        # Try installing critical packages with --user flag
        for package in failed_packages:
            run_command(f"pip install --user {package}", f"Installing {package} with --user flag")

    return True

def setup_database():
    """Setup the employee database"""
    logger.info("🗄️  Setting up employee database...")

    if not run_command("python setup_employee_database.py", "Setting up employee database"):
        logger.error("❌ Database setup failed")
        return False

    return True

def create_directories():
    """Create necessary directories"""
    logger.info("📁 Creating necessary directories...")

    directories = [
        "static/uploads/employees",
        "static/uploads/employees/training",
        "static/snapshots",
        "logs",
        "instance"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")

    return True

def create_env_file():
    """Create environment configuration file"""
    logger.info("⚙️  Creating environment configuration...")

    env_content = """# Flask Configuration
FLASK_APP=backend.main
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database
DATABASE_URL=sqlite:///instance/safety_monitoring.db

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-this-too
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400

# AI Configuration
DETECTION_THRESHOLD_WORKER=0.5
DETECTION_THRESHOLD_HELMET=0.6
FACE_RECOGNITION_TOLERANCE=0.6
MAX_CAMERAS=10

# Email Configuration (Configure these for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# WhatsApp Configuration (Optional - using Twilio)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_NUMBER=+1234567890

# SMS Configuration (Optional)
SMS_API_KEY=your-sms-api-key
SMS_PHONE_NUMBER=+1234567890

# CORS Configuration
CORS_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
"""

    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        logger.info("✅ Created .env configuration file")
        logger.warning("⚠️  Please edit .env file with your actual credentials!")
    else:
        logger.info("ℹ️  .env file already exists")

    return True

def test_system():
    """Run basic system tests"""
    logger.info("🧪 Testing system components...")

    # Test imports
    try:
        import cv2
        logger.info("✅ OpenCV imported successfully")
    except ImportError:
        logger.warning("⚠️  OpenCV not available - camera features will be limited")

    try:
        import face_recognition
        logger.info("✅ Face recognition imported successfully")
    except ImportError:
        logger.warning("⚠️  Face recognition not available - employee recognition will be disabled")

    try:
        from backend.database.models import db, Employee
        logger.info("✅ Database models imported successfully")
    except ImportError as e:
        logger.error(f"❌ Database models import failed: {e}")
        return False

    return True

def create_startup_scripts():
    """Create convenient startup scripts"""
    logger.info("🚀 Creating startup scripts...")

    # Windows batch file for monitoring
    batch_content = """@echo off
echo Starting Enhanced AI Safety Monitoring System...
echo.

REM Activate virtual environment if it exists
if exist .venv\\Scripts\\activate.bat (
    call .venv\\Scripts\\activate.bat
)

REM Start the enhanced monitoring system
python enhanced_real_time_monitoring.py --camera-id 1 --location "Main Entrance"

pause
"""

    with open("START_ENHANCED_MONITORING.bat", 'w') as f:
        f.write(batch_content)

    # Web server startup script
    web_batch_content = """@echo off
echo Starting AI Safety Monitoring Web Server...
echo.

REM Activate virtual environment if it exists
if exist .venv\\Scripts\\activate.bat (
    call .venv\\Scripts\\activate.bat
)

REM Start the web server
python run.py

pause
"""

    with open("START_WEB_SERVER.bat", 'w') as f:
        f.write(web_batch_content)

    logger.info("✅ Created startup scripts: START_ENHANCED_MONITORING.bat, START_WEB_SERVER.bat")
    return True

def main():
    """Main setup function"""
    print("="*70)
    print("🚀 ENHANCED EMPLOYEE RECOGNITION SAFETY SYSTEM SETUP")
    print("="*70)
    print()

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Create directories
    if not create_directories():
        logger.error("Failed to create directories")
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        logger.error("Failed to install dependencies")
        sys.exit(1)

    # Create environment file
    if not create_env_file():
        logger.error("Failed to create environment file")
        sys.exit(1)

    # Setup database
    if not setup_database():
        logger.error("Failed to setup database")
        sys.exit(1)

    # Test system
    if not test_system():
        logger.error("System tests failed")
        sys.exit(1)

    # Create startup scripts
    if not create_startup_scripts():
        logger.error("Failed to create startup scripts")
        sys.exit(1)

    print()
    print("="*70)
    print("✅ SETUP COMPLETED SUCCESSFULLY!")
    print("="*70)
    print()
    print("🎯 WHAT'S NEXT:")
    print()
    print("1. 📝 Edit .env file with your email/WhatsApp/SMS credentials")
    print("2. 🖼️  Upload employee photos via web interface:")
    print("   - Run: START_WEB_SERVER.bat")
    print("   - Go to: http://localhost:5000/employees")
    print("   - Add employees and upload their face photos")
    print("3. 🎥 Start monitoring:")
    print("   - Run: START_ENHANCED_MONITORING.bat")
    print("4. 📚 Read EMPLOYEE_RECOGNITION_README.md for detailed instructions")
    print()
    print("📞 SUPPORT:")
    print("   - Check EMPLOYEE_RECOGNITION_README.md for troubleshooting")
    print("   - Ensure cameras are properly connected")
    print("   - Test notifications with sample data first")
    print()
    print("="*70)
    print("🎉 Your Enhanced AI Safety System is ready!")
    print("="*70)

if __name__ == "__main__":
    main()