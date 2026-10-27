# Installation & Deployment Guide

Complete step-by-step guide for installing and deploying the AI Smart Safety Monitoring System

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware
- **Processor**: Intel i5 or equivalent (Ryzen 5+)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free disk space
- **Camera**: USB webcam, IP camera, or integrated camera (minimum 640x480)
- **Network**: Ethernet or WiFi connection

### Software
- **Operating System**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8, 3.9, 3.10, or 3.11
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)

### Optional
- **GPU**: NVIDIA GPU with CUDA for accelerated processing
- **Docker**: For containerized deployment

## Installation

### Step 1: Install Python

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run installer
3. ✓ Check "Add Python to PATH"
4. Click "Install Now"
5. Verify: `python --version`

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python3

# Or download from https://www.python.org/downloads/
# Verify: python3 --version
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
python3 --version
```

### Step 2: Get Project Files

**Option A: Download ZIP**
1. Download project from source
2. Extract to desired location
3. Navigate to extracted folder

**Option B: Git Clone**
```bash
git clone <repository-url>
cd "major project"
```

### Step 3: Automated Installation (Recommended)

**Windows:**
```bash
python setup.py
```

**macOS/Linux:**
```bash
python3 setup.py
```

The setup wizard will:
- ✓ Create virtual environment
- ✓ Install dependencies
- ✓ Create directories
- ✓ Initialize database
- ✓ Create startup scripts

### Step 4: Manual Installation

If automated setup fails, follow these steps:

**Create Virtual Environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Install Dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Initialize Database:**
```bash
# Windows
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"

# macOS/Linux
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"
```

**Create Directories:**
```bash
mkdir dataset\helmet
mkdir dataset\no_helmet
mkdir dataset\worker
mkdir dataset\machine
mkdir logs
```

## Configuration

### Basic Configuration

Edit `config.py` to customize:

```python
class Config:
    # Camera settings
    CAMERA_ID = 0                    # 0 = default, 1 = secondary
    CAMERA_WIDTH = 640               # video width
    CAMERA_HEIGHT = 480              # video height
    CAMERA_FPS = 30                  # frames per second
    
    # Detection settings
    HELMET_THRESHOLD = 0.5           # 0.0-1.0, lower = more sensitive
    WORKER_THRESHOLD = 0.5           # 0.0-1.0
    ALERT_COOLDOWN = 5               # seconds between alerts
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///safety_monitoring.db'
```

### Advanced Configuration

**For Production:**
```python
FLASK_ENV = 'production'
DEBUG = False
TESTING = False
SECRET_KEY = 'your-random-secret-key'
```

**For HTTPS:**
```python
# Use reverse proxy (nginx) or SSL/TLS wrapper
# Or configure Flask-SSL:
app.config['SSL_REDIRECT'] = True
```

### Environment Variables

Create `.env` file:
```
FLASK_ENV=production
FLASK_DEBUG=0
CAMERA_ID=0
HELMET_THRESHOLD=0.5
DATABASE_URL=sqlite:///safety_monitoring.db
SECRET_KEY=your-secret-key-here
```

Load in app:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Running the Application

### Development Mode

**Windows:**
```bash
venv\Scripts\activate
python app.py
```

**macOS/Linux:**
```bash
source venv/bin/activate
python3 app.py
```

**Output:**
```
============================================================
AI Smart Safety Monitoring System
============================================================
Starting application on http://localhost:5000
Press Ctrl+C to stop
============================================================
```

### Using Startup Scripts

**Windows:**
```bash
run.bat
```

**macOS/Linux:**
```bash
./run.sh
```

### Access Application

1. Open browser
2. Navigate to: **http://localhost:5000**
3. Interface loads and ready to use

## Production Deployment

### Option 1: Using Gunicorn

**Install Gunicorn:**
```bash
pip install gunicorn
```

**Run with Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Parameters:
- `-w 4`: 4 worker processes
- `-b 0.0.0.0:5000`: Bind to all interfaces, port 5000
- `--timeout 120`: Request timeout in seconds
- `--access-logfile logs/access.log`: Access logging

### Option 2: Using Nginx Reverse Proxy

**Install Nginx:**
```bash
# Ubuntu
sudo apt install nginx

# macOS
brew install nginx
```

**Configure Nginx** (`/etc/nginx/sites-available/default`):
```nginx
server {
    listen 80;
    server_name your.domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /video_feed {
        proxy_pass http://127.0.0.1:5000/video_feed;
        proxy_buffering off;
    }
}
```

**Enable & Restart:**
```bash
sudo systemctl restart nginx
```

### Option 3: Docker Deployment

**Create Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

**Build Image:**
```bash
docker build -t safety-monitor .
```

**Run Container:**
```bash
docker run -p 5000:5000 --device /dev/video0 safety-monitor
```

### Option 4: Systemd Service (Linux)

Create `/etc/systemd/system/safety-monitor.service`:
```ini
[Unit]
Description=AI Safety Monitoring System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/deploy/safety-monitor
ExecStart=/home/deploy/safety-monitor/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable Service:**
```bash
sudo systemctl enable safety-monitor
sudo systemctl start safety-monitor
```

### Security Checklist for Production

- [ ] Change `SECRET_KEY` to random string
- [ ] Set `DEBUG = False`
- [ ] Use HTTPS/TLS certificate
- [ ] Enable authentication
- [ ] Setup firewall rules
- [ ] Configure log rotation
- [ ] Setup database backups
- [ ] Enable rate limiting
- [ ] Monitor system resources
- [ ] Setup alerting

### Enable HTTPS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --standalone -d your.domain.com
```

Update Nginx config:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/your.domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your.domain.com/privkey.pem;
    
    # ... rest of config
}
```

## Database Setup

### SQLite (Default)
```bash
# Already configured
# Database file: safety_monitoring.db
```

### PostgreSQL Production

**Install PostgreSQL:**
```bash
pip install psycopg2-binary
```

**Configure Connection:**
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost:5432/safety_monitor'
```

**Create Database:**
```bash
createdb safety_monitor
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Backup & Restore

### Backup Database

```bash
# SQLite
cp safety_monitoring.db backups/safety_monitoring_$(date +%Y%m%d).db

# PostgreSQL
pg_dump safety_monitor > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
# SQLite
cp backups/safety_monitoring_20240317.db safety_monitoring.db

# PostgreSQL
psql safety_monitor < backup_20240317.sql
```

## Monitoring and Logging

### Application Logs

```bash
# View logs
tail -f logs/app.log

# Access logs
tail -f logs/access.log
```

### System Monitoring

```bash
# CPU and Memory
top

# Disk usage
df -h

# Process info
ps aux | grep python
```

### Health Check

```bash
curl http://localhost:5000/health
```

## Updating Application

```bash
# Stop application
Ctrl+C

# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run database migrations (if any)
python -c "from app import app, db; app.app_context().push(); db.upgrade()"

# Restart application
python app.py
```

## Troubleshooting

### Port 5000 Already in Use

```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
python app.py --port 5001
```

### Camera Permission Denied (Linux)

```bash
# Add user to video group
sudo usermod -a -G video $USER
newgrp video
```

### Out of Memory

```bash
# Reduce processes
gunicorn -w 2 -b 0.0.0.0:5000 app:app

# Monitor memory
free -h
```

### Database Locked

```bash
# SQLite database locked
# Restart application
# Backup and restore database if needed
```

## Performance Tuning

### Optimize Detection
- Reduce frame resolution (640x480)
- Lower frame rate (15-30 FPS)
- Adjust detection thresholds

### Optimize Server
- Use multiple worker processes (gunicorn -w 4)
- Enable caching
- Use database indexing
- Monitor CPU/memory

### Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test performance
ab -n 100 -c 10 http://localhost:5000/
```

## Next Steps

1. Read [QUICK_START.md](QUICK_START.md) for common tasks
2. Check [README.md](README.md) for full documentation
3. Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API reference
4. Configure monitoring and alerting
5. Setup automated backups

---

**Installation Complete!** 🎉

Your AI Smart Safety Monitoring System is ready to deploy.
