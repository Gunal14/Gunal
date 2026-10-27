# Server Architecture & Configuration Details

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Flask Application Server                     │
│                         (Port: 5000)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│  │   FRONTEND       │  │   BACKEND API    │  │   AI SERVICES   │
│  │   (Templates)    │  │   (Flask Routes) │  │  (Detection)    │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘
│         |                      |                      |          │
│  • index.html          • /api/auth/*         • Detector       │
│  • live_monitoring     • /api/incidents/*    • ModelManager    │
│  • static files        • /api/analytics/*    • MultiCamera     │
│  • CSS/JS              • /api/monitoring/*   • Detection       │
│                        • /health                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ FRONTEND SERVER

### Location
```
frontend/
├── templates/
│   ├── index.html              (Main dashboard)
│   └── live_monitoring.html    (24/7 monitoring interface)
└── static/
    ├── css/
    ├── js/
    └── images/
```

### Routes Available
| Route | Template | Purpose |
|-------|----------|---------|
| `/` | `index.html` | Main dashboard |
| `/dashboard` | `index.html` | Dashboard alias |
| `/index.html` | `index.html` | Direct access |
| `/monitoring` | `live_monitoring.html` | Live monitoring |
| `/live` | `live_monitoring.html` | Live monitoring alias |

### Static Assets Location
```
frontend/static/
├── css/
│   ├── style.css          (Main stylesheet)
│   ├── dashboard.css      (Dashboard styles)
│   └── monitoring.css     (Monitoring styles)
├── js/
│   ├── app.js             (Main app logic)
│   ├── dashboard.js       (Dashboard functionality)
│   ├── monitoring.js      (Monitoring functionality)
│   └── auth.js            (Authentication)
└── images/
    ├── logo.png
    └── icons/
```

### Server Configuration
```python
Template Folder:  ../frontend/templates
Static Folder:    ../frontend/static
CORS Enabled:     Yes (for /api/*)
Max Upload Size:  Not set (default 16MB)
```

### Access Points
```
# Dashboard
http://localhost:5000/
http://localhost:5000/dashboard
http://localhost:5000/index.html

# Monitoring
http://localhost:5000/monitoring
http://localhost:5000/live
```

---

## 🔌 BACKEND API SERVER

### Framework
```
Framework:        Flask 2.3.2+
Python:           3.12+
Port:             5000 (default)
Host:             0.0.0.0 (accessible from any interface)
Debug Mode:       True (development)
Reloader:         Enabled
```

### Core Services

#### 1. **Authentication Service**
```
Class:            AuthenticationService
Module:           backend/services/auth_service.py
JWT Secret:       ${JWT_SECRET_KEY} from config
Access Token:     Expires in 1 hour
Refresh Token:    Expires in 30 days
Routes:           /api/auth/*
```

**Endpoints:**
```
POST   /api/auth/login           - User login
POST   /api/auth/logout          - User logout
POST   /api/auth/refresh         - Refresh token
GET    /api/auth/validate        - Validate token
POST   /api/auth/register        - User registration
```

#### 2. **Session Management Service**
```
Class:            SessionManagementService
Module:           backend/services/auth_service.py
Session Storage:  In-memory (development)
Cookie Secure:    True (production)
Cookie HttpOnly:  True
Session Lifetime: 7 days
```

#### 3. **Incident Management Service**
```
Class:            IncidentManagementService
Module:           backend/services/incident_service.py
Routes:           /api/incidents/*
```

**Endpoints:**
```
GET    /api/incidents            - List all incidents
GET    /api/incidents/<id>       - Get incident details
POST   /api/incidents            - Create incident
PUT    /api/incidents/<id>       - Update incident
DELETE /api/incidents/<id>       - Delete incident
GET    /api/incidents/search     - Search incidents
```

#### 4. **Analytics Service**
```
Class:            AnalyticsService
Module:           backend/services/analytics_service.py
Routes:           /api/analytics/*
```

**Endpoints:**
```
GET    /api/analytics/dashboard  - Dashboard metrics
GET    /api/analytics/trends     - Trend analysis
GET    /api/analytics/reports    - Generate reports
GET    /api/analytics/export     - Export data
```

#### 5. **Continuous Monitoring Service**
```
Class:            ContinuousMonitoringService
Module:           backend/services/monitoring_service.py
Max Cameras:      16 (configurable)
Detection Thread: Per-second intervals
Capture Thread:   Continuous FPS
Routes:           /api/monitoring/*
```

**Endpoints:**
```
GET    /api/monitoring/status         - Monitoring status
GET    /api/monitoring/cameras        - List cameras
GET    /api/monitoring/cameras/<id>   - Camera details
POST   /api/monitoring/cameras/add    - Add camera
POST   /api/monitoring/cameras/remove - Remove camera
GET    /api/monitoring/stream/<id>    - MJPEG stream (1-sec)
GET    /api/monitoring/frame/<id>     - Snapshot JPEG
GET    /api/monitoring/detections     - Get detections
POST   /api/monitoring/start          - Start monitoring
POST   /api/monitoring/stop           - Stop monitoring
```

#### 6. **Notification Service**
```
Class:            NotificationService
Module:           backend/services/notification_service.py
Email Support:    Yes (SMTP)
SMS Support:      No (configured but disabled)
Webhooks:         Yes
```

#### 7. **Reporting Service**
```
Class:            ReportingService
Module:           backend/services/analytics_service.py
Report Formats:   PDF, CSV, JSON
Date Range:       Configurable
Scheduling:       Supported
```

#### 8. **Audit Service**
```
Class:            AuditService
Module:           backend/services/incident_service.py
Logging:          All API calls
Retention:        90 days (configurable)
```

### Database Configuration
```
Default:          SQLite (sqlite:///safety_monitoring.db)
Production:       PostgreSQL (via DATABASE_URL env var)

Settings:
- Pool Size:      10
- Pool Recycle:   3600 seconds
- Pool Pre-ping:  True
- Echo:           True (development)
```

### Security Configuration
```
SECRET_KEY:              ${SECRET_KEY} or 'dev-secret-key'
JWT_SECRET_KEY:          ${JWT_SECRET_KEY} or SECRET_KEY
SESSION_COOKIE_SECURE:   True (production)
SESSION_COOKIE_HTTPONLY: True
SESSION_COOKIE_SAMESITE: Lax
CORS Origins:            Configurable
```

### Health Check
```
Endpoint:   GET /health
Response:   {
  "status": "healthy",
  "timestamp": "2026-03-17T20:00:00Z",
  "environment": "development",
  "version": "2.0.0",
  "components": {
    "api": "operational",
    "ai_engine": "operational",
    "database": "operational",
    "notification_service": "operational"
  }
}
```

### API Welcome
```
Endpoint:   GET /api
Response:   System info and available endpoints
```

---

## 🤖 AI SERVICES

### Core Components
```
Module:           ai/
Version:          2.0.0
Location:         d:\major project\ai\
```

### 1. Advanced Safety Detector
```
Class:            AdvancedSafetyDetector
Module:           ai/detection/advanced_detector.py
Model Type:       Ensemble (multiple models)
Confidence:       0.5 (50% threshold, configurable)

Detection Types:
- Helmet Detection
- Worker Detection
- PPE Compliance
- Unsafe Postures
```

**Configuration:**
```python
model_type='ensemble'           # Multi-model approach
confidence_threshold=0.5        # 50% minimum
detection_interval=1            # Every 1 second
frame_processing='concurrent'   # Parallel processing
```

**Methods:**
```python
detector.detect(frame, camera_id)
detector.batch_detect(frames)
detector.get_detection_results()
detector.update_model(model_path)
detector.get_confidence_stats()
```

### 2. Multi-Camera Manager
```
Class:            MultiCameraManager
Module:           ai/detection/multi_camera_manager.py
Max Cameras:      16 (configurable)

Features:
- Dynamic camera addition/removal
- Per-camera detection tracking
- Concurrent frame processing
- Load balancing
```

**Methods:**
```python
manager.add_camera(camera_id, source, location)
manager.remove_camera(camera_id)
manager.get_camera_status(camera_id)
manager.process_frame(camera_id, frame)
manager.get_aggregate_stats()
```

### 3. Model Manager
```
Class:            ModelManager
Module:           ai/models/model_manager.py

Features:
- Model loading/caching
- Version management
- Performance optimization
- Fallback mechanisms
```

**Methods:**
```python
manager.load_model(model_name)
manager.get_available_models()
manager.update_model(model_name, model_path)
manager.get_model_info(model_name)
manager.benchmark_model()
```

### Available Detection Models
```
models/
├── helmet_detector.pth
├── worker_detector.pth
├── ppe_detector.pth
└── ensemble_model.pth
```

### Detection Configuration
```python
HELMET_THRESHOLD = 0.5
WORKER_THRESHOLD = 0.5
ALERT_COOLDOWN = 5 seconds
MIN_DETECTION_FRAMES = 3
```

### Detection Output
```json
{
  "camera_id": 0,
  "timestamp": "2026-03-17T20:00:00Z",
  "detections": [
    {
      "type": "helmet",
      "confidence": 0.85,
      "bbox": [100, 50, 200, 150],
      "class": "No Helmet",
      "alert": true
    }
  ],
  "frame_count": 1234,
  "processing_time_ms": 45
}
```

### AI Performance Metrics
```
Model Inference:  ~30-50ms per frame
Batch Processing: ~100-150ms for 4 frames
Memory per model: 100-300MB
GPU Support:      Yes (CUDA optional)
CPU Optimization: Yes (SIMD, threading)
```

---

## 🎥 CAMERA MONITORING

### Default Camera Setup
```python
Camera ID:     0
Source:        0 (Local webcam)
Location:      Main Entrance
Resolution:    640x480
FPS:           30
Buffer Size:   300 frames
```

### Camera Configuration
```python
MAX_CAMERAS = 16              # Maximum concurrent
CAMERA_WIDTH = 640           # Resolution
CAMERA_HEIGHT = 480
CAMERA_FPS = 30              # Frames per second
DETECTION_INTERVAL = 1       # Process every 1 second
```

### Camera Sources Supported
```
Local Webcam:     source=0
IP Camera:        source="http://192.168.1.100:8080/video"
RTSP Stream:      source="rtsp://camera.local/stream"
Video File:       source="path/to/video.mp4"
```

### MJPEG Streaming
```
Endpoint:         /api/monitoring/stream/<camera_id>
Format:           MJPEG (Motion JPEG)
Frame Interval:   1 second (configurable)
Quality:          85% JPEG compression
MIME Type:        multipart/x-mixed-replace
```

---

## 📊 DATABASE

### Development
```
Type:             SQLite
Path:             safety_monitoring.db
Location:         Project root
Features:         Local storage, easy setup
```

### Production
```
Type:             PostgreSQL
Connection:       ${DATABASE_URL} env var
Pool Size:        10 connections
Idle Timeout:     3600 seconds
```

### Tables
```
- users
- sessions
- incidents
- detections
- camera_feeds
- alerts
- audit_logs
- analytics
```

---

## 🔐 AUTHENTICATION & SECURITY

### JWT Configuration
```
Algorithm:        HS256
Access Token:     1 hour expiry
Refresh Token:    30 days expiry
Secret Key:       From environment or config
```

### CORS Configuration
```
Enabled:          Yes
Allowed Origins:  Configurable
Methods:          GET, POST, PUT, DELETE, OPTIONS
Headers:          Content-Type, Authorization
Credentials:      Allowed
```

### Request Validation
```
JSON Schema:      Enabled
Input Sanitization: Yes
Rate Limiting:    Redis (optional)
```

---

## 📝 LOGGING

### Log Configuration
```
Level:            INFO
Format:           %(asctime)s - %(name)s - %(levelname)s - %(message)s
Log File:         logs/app.log
Max File Size:    10MB
Backup Count:     5 files
```

### Log Retention
```
Application Logs:  7 days
Incident Records:  180 days
Video Data:        30 days
Audit Trail:       90 days
```

---

## ⚙️ CONFIGURATION PROFILES

### Development
```
DEBUG:            True
TESTING:          False
ENV:              development
CORS Secure:      False
Database:         SQLite
Reloader:         Enabled
```

### Production
```
DEBUG:            False
TESTING:          False
ENV:              production
CORS Secure:      True
Database:         PostgreSQL
Reloader:         Disabled
Error Pages:      Custom HTML
```

### Testing
```
DEBUG:            False
TESTING:          True
ENV:              testing
Database:         SQLite (in-memory)
Mock Services:    Yes
```

---

## 🚀 STARTUP PROCESS

1. **Load Configuration**
   ```
   environment → config profile → Flask config
   ```

2. **Initialize Services**
   ```
   Auth Service → Session Management → Incident Management
   ↓
   Notification Service → Reporting Service → Analytics
   ↓
   Continuous Monitoring Service → AI Components
   ```

3. **Register Routes**
   ```
   /api/auth/* → /api/incidents/* → /api/analytics/*
   ↓
   /api/monitoring/* → Frontend routes
   ```

4. **Initialize AI**
   ```
   Load Detection Models → Initialize Model Manager
   ↓
   Setup Multi-Camera Manager → Load Camera Feeds
   ```

5. **Start Monitoring**
   ```
   Initialize Default Cameras → Start Continuous Monitoring
   ↓
   Enable Frame Capture → Enable Detection Processing
   ```

---

## 📈 PERFORMANCE SPECIFICATIONS

### API Response Times
```
Health Check:        <10ms
Status Query:        <20ms
Detection Results:   <50ms
Stream Start:        <100ms
Full Dashboard:      <500ms
```

### Resource Usage
```
Base Memory:         100-150MB
Per Camera:          50-100MB
Per Active Stream:   10-25MB
CPU Usage:           5-15% (4 cameras)
Network per Stream:  2-5 Mbps (1080p)
```

### Scalability
```
Max Concurrent Cameras:    16
Max Concurrent Streams:    Unlimited
Max API Requests/sec:      1000+
Max Database Connections:  10
Max Session Limit:         1000+
```

---

## 📦 DEPLOYMENT

### Local Development
```bash
cd d:\major project
python main.py
# Access at http://localhost:5000
```

### Docker Deployment
```bash
docker build -t safety-monitor .
docker run -p 5000:5000 safety-monitor
```

### Production Server
```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

---

## 🔗 Quick Start URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Dashboard | `http://localhost:5000/` | Main UI |
| Monitoring | `http://localhost:5000/monitoring` | Live feeds |
| Health | `http://localhost:5000/health` | Status check |
| API | `http://localhost:5000/api` | API info |
| Auth | `http://localhost:5000/api/auth/login` | Login |
| Incidents | `http://localhost:5000/api/incidents` | Incidents list |
| Analytics | `http://localhost:5000/api/analytics` | Analytics |
| Monitoring | `http://localhost:5000/api/monitoring/status` | Monitor status |
| Stream | `http://localhost:5000/api/monitoring/stream/0` | Camera stream |

---

## 📞 Support & Documentation

See additional documentation files:
- `API_DOCUMENTATION.md` - Detailed API reference
- `ARCHITECTURE.md` - System architecture
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `MONITORING_24_7_GUIDE.md` - Monitoring system
- `INTEGRATION_GUIDE.md` - Integration examples

