# Multi-Camera Safety Monitoring System - Setup & Implementation Guide

## Overview

This guide covers the advanced features added to support:
- **30-40 simultaneous cameras** with intelligent resource coordination
- **Multi-factor risk prediction** with contextual accuracy
- **3-channel emergency notifications** (Email, SMS, WhatsApp) to up to 10 contacts
- **Real-time health monitoring** and alert management

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flask Web Application                     │
│                     (backend/main.py)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Multi-Camera Coordinator (40 cameras)            │   │
│  │  - ThreadPoolExecutor for parallel processing            │   │
│  │  - Dynamic FPS/resolution optimization                   │   │
│  │  - Frame queue prioritization                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│           │                          │                      │    │
│           ▼                          ▼                      ▼    │
│  ┌──────────────────┐    ┌──────────────────┐  ┌────────────────┐
│  │ Risk Prediction  │    │  Notification    │  │  Camera Health │
│  │ Engine           │    │  Service         │  │  Monitoring    │
│  │                  │    │                  │  │                │
│  │ - Base scores    │    │ - Email channel  │  │ - Connection   │
│  │ - Multipliers    │    │ - SMS (Twilio)   │  │ - Performance  │
│  │ - Context assess │    │ - WhatsApp       │  │ - Uptime       │
│  │ - Pattern detect │    │ - Severity route │  │ - Resources    │
│  └──────────────────┘    └──────────────────┘  └────────────────┘
│           │                      │                      │
│           └──────────────────────┴──────────────────────┘
│                            │
│                            ▼
│              ┌─────────────────────────────┐
│              │     Database (SQLAlchemy)   │
│              │                             │
│              │  - RiskAlert                │
│              │  - EmergencyContact (max 10)│
│              │  - CameraConfiguration      │
│              │  - CameraHealthStatus       │
│              │  - NotificationLog          │
│              │  - RiskPredictionModel      │
│              │  - MultiCameraSession       │
│              └─────────────────────────────┘
│
└─────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
   REST API Routes    WebSocket Live     Admin Dashboard
   (22 endpoints)     Monitoring         (Multi-camera view)
```

---

## Setup Instructions

### 1. Install Required Python Packages

```bash
pip install flask flask-cors flask-jwt-extended
pip install twilio  # For SMS & WhatsApp
pip install opencv-python  # For frame processing
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SENDER_EMAIL=safety-alerts@yourcompany.com
SENDER_NAME=AI Safety Monitoring System

# Twilio Configuration (SMS & WhatsApp)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_SMS_FROM=+1234567890
TWILIO_WHATSAPP_FROM=whatsapp:+1234567890
SMS_ENABLED=true
WHATSAPP_ENABLED=true

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# System Configuration
MAX_CAMERAS=40
```

### 3. Initialize Database

```bash
python -c "
from backend.database import init_db
init_db()
print('Database initialized with 6 new models')
"
```

### 4. Start Flask Application

```bash
python -m backend.main
```

The API will be available at: `http://localhost:5000/api/v1`

---

## New Database Models

### 1. EmergencyContact
Stores up to 10 emergency contacts per admin for multi-channel alerts.

```python
admin_id           # Foreign key to User
contact_name       # "John Manager"
phone_number       # "+1234567890" (required for SMS/WhatsApp)
email              # "john@example.com" (for email alerts)
whatsapp_enabled   # bool (enable WhatsApp notifications)
sms_enabled        # bool (enable SMS notifications)
email_enabled      # bool (enable email notifications)
alert_low          # bool (receive LOW severity alerts)
alert_medium       # bool (receive MEDIUM severity alerts)
alert_high         # bool (receive HIGH severity alerts)
alert_critical     # bool (receive CRITICAL severity alerts)
verified           # bool (phone/email verification status)
is_active          # bool (soft delete flag)
```

### 2. RiskAlert
Enhanced alert tracking with multi-factor scoring.

```python
alert_id                   # UUID primary key
camera_id                  # Foreign key to camera
severity                   # LOW|MEDIUM|HIGH|CRITICAL
risk_score                 # 0-100 (calculated from multiple factors)
confidence_score           # 0-1 (detection confidence)
risk_type                  # "not_wearing_helmet", "hazmat_exposure", etc.
risk_category              # PPE|POSTURE|BEHAVIOR|HAZMAT|FATIGUE|ENVIRONMENT
detection_count            # How many times detected in time window
worker_id                  # Optional worker identifier
environmental_conditions   # JSON: lighting, weather, temperature, air_quality
area_hazard_level         # Location risk: LOW|MEDIUM|HIGH|CRITICAL
status                    # pending|notified|acknowledged|resolved
image_url                 # Evidence image URL
timestamp                 # Alert creation time
```

### 3. CameraHealthStatus
Real-time health tracking for 40+ cameras.

```python
camera_id              # Foreign key
is_connected           # bool (connection status)
current_fps            # Current frames per second
frame_loss_rate        # % of dropped frames
cpu_usage              # % CPU utilization
memory_usage           # % Memory utilization
bandwidth_usage        # Mbps consumed
latency_ms             # Network latency in milliseconds
packet_loss            # % of packet loss
signal_strength        # dBm (for wireless)
uptime_percentage      # % uptime over period
uptime_seconds         # Total uptime in seconds
detection_running      # bool (is detection active)
last_error             # Last error message
```

### 4. NotificationLog
Audit trail for all notifications sent.

```python
notification_id    # UUID primary key
alert_id           # Foreign key to RiskAlert
notification_type  # EMAIL|SMS|WHATSAPP
recipient          # Email or phone number
contact_id         # Foreign key to EmergencyContact
admin_id           # Foreign key to User
status             # pending|sent|failed|bounced
attempts           # Number of retry attempts
last_attempt       # Timestamp of last attempt
delivered          # bool (delivery confirmation)
read               # bool (message read status)
error_message      # Error details if failed
```

### 5. RiskPredictionModel
Model versioning for A/B testing and improvements.

```python
model_name         # "YOLOv8-PPE", "Faster-RCNN"
model_version      # "1.0", "1.1", etc.
model_type         # YOLO|Faster_RCNN|Custom
risk_types         # JSON list: ["helmet", "vest", "gloves", ...]
accuracy           # Overall accuracy %
precision          # Precision metric
recall             # Recall metric
f1_score           # F1 score
inference_time_ms  # Average inference time
memory_required_mb # Memory requirements
is_active          # Currently in use
is_fallback        # Use if primary fails
model_path         # File location of model
```

### 6. MultiCameraSession
Track coordinated monitoring sessions.

```python
session_id              # UUID primary key
started_by_id           # User who started session
camera_ids              # JSON array of camera IDs
total_cameras           # Number of cameras
active_alerts           # Current active alerts count
total_detections        # Total detections in session
high_risk_events        # CRITICAL severity count
avg_response_time_ms    # Average alert response time
system_health_score     # 0-100 (overall health)
start_time              # Session start timestamp
end_time                # Session end timestamp
is_active               # Session running status
```

---

## New Services

### 1. RiskPredictionEngine
**File**: `backend/services/risk_prediction_service.py` (400+ lines)

Multi-factor risk assessment with contextual scoring.

**Key Features**:
- Base risk scores for 15+ violation types
- 10+ multiplier factors (hazard, time, worker history, environment)
- Pattern detection (repeated violations escalate severity)
- Environmental factor analysis (lighting, weather, air quality)
- Worker fatigue detection
- Contextual severity calculation

**Usage**:
```python
from backend.services.risk_prediction_service import RiskPredictionEngine

engine = RiskPredictionEngine()

prediction = engine.predict_risk(
    detection={
        'class': 'person',
        'confidence': 0.95,
        'violation': 'not_wearing_helmet'
    },
    location_id=5,
    worker_id='W123'
)

# Returns:
# {
#     'violation_type': 'not_wearing_helmet',
#     'risk_score': 78.5,
#     'severity': 'HIGH',
#     'confidence': 0.95,
#     'action_required': True,
#     'escalation_level': 2
# }
```

### 2. AdvancedNotificationService
**File**: `backend/services/advanced_notification_service.py` (350+ lines)

Multi-channel alert distribution with intelligent routing.

**Channels**:
- **EMAIL**: HTML formatted with severity color-coding
- **SMS**: Twilio integration with 160-char optimization
- **WHATSAPP**: Rich markdown formatting via Twilio

**Routing Rules**:
- LOW: Email only
- MEDIUM: Email + SMS
- HIGH: Email + SMS + WhatsApp
- CRITICAL: All channels (immediate)

**Usage**:
```python
from backend.services.advanced_notification_service import AdvancedNotificationService

service = AdvancedNotificationService()
service.initialize_channels(config)

result = service.send_emergency_alert(
    alert_data={
        'severity': 'CRITICAL',
        'title': 'Helmet Not Detected',
        'body': 'Worker in hazmat area without helmet',
        'alert_id': 'ALERT-001'
    },
    emergency_contacts=[  # Up to 10 contacts
        {
            'contact_name': 'John Manager',
            'phone_number': '+1234567890',
            'email': 'john@example.com',
            'email_enabled': True,
            'sms_enabled': True,
            'whatsapp_enabled': True,
            'alert_critical': True
        }
    ]
)

# Returns:
# {
#     'total_contacts': 1,
#     'successful': 1,
#     'failed': 0,
#     'notifications': {...}
# }
```

### 3. MultiCameraCoordinator
**File**: `backend/services/multi_camera_coordinator.py` (450+ lines)

Orchestrates 40+ simultaneous camera streams with intelligent resource management.

**Features**:
- ThreadPoolExecutor-based parallel processing
- Dynamic FPS/resolution optimization under high load
- Per-camera statistics tracking
- Alert aggregation and prioritization
- Resource monitoring (CPU, memory)
- Automatic frame skipping when needed
- Connection status tracking

**Usage**:
```python
from backend.services.multi_camera_coordinator import MultiCameraCoordinator

coordinator = MultiCameraCoordinator(
    max_cameras=40,
    risk_engine=engine,
    notification_service=service
)

# Start monitoring all cameras
coordinator.start_monitoring()

# Add camera
coordinator.add_camera(
    camera_id=1,
    config={
        'camera_name': 'Assembly Floor',
        'stream_url': 'rtsp://192.168.1.100:554/stream',
        'hazard_level': 'HIGH'
    }
)

# Process frame
result = coordinator.process_frame(
    camera_id=1,
    frame=cv2_frame,
    detections=[...]
)

# Get status
status = coordinator.get_coordinator_status()
# {
#     'active_cameras': 8,
#     'total_frames_processed': 245780,
#     'coordinator_health': 'healthy'
# }

# Stop monitoring
coordinator.stop_monitoring()
```

---

## REST API Endpoints (22 Total)

### Emergency Contacts (4 endpoints)
```
GET    /api/v1/emergency-contacts              # Get all (max 10)
POST   /api/v1/emergency-contacts              # Register new
PUT    /api/v1/emergency-contacts/{id}         # Update contact
DELETE /api/v1/emergency-contacts/{id}         # Delete contact
```

### Risk Alerts (5 endpoints)
```
GET    /api/v1/risk-alerts                     # Get alerts with filters
GET    /api/v1/risk-alerts/{alert_id}          # Get alert details
POST   /api/v1/risk-alerts/{alert_id}/acknowledge  # Mark acknowledged
POST   /api/v1/risk-alerts/{alert_id}/resolve      # Mark resolved
GET    /api/v1/alert-statistics                # Get statistics
```

### Multi-Camera Management (7 endpoints)
```
GET    /api/v1/cameras                         # Get all cameras
POST   /api/v1/cameras                         # Register camera (max 40)
GET    /api/v1/cameras/{camera_id}             # Get camera details
PUT    /api/v1/cameras/{camera_id}             # Update camera
POST   /api/v1/cameras/{camera_id}/deactivate  # Stop monitoring
GET    /api/v1/cameras/{camera_id}/health      # Get health metrics
POST   /api/v1/cameras/{camera_id}/process-frame  # Process frame
```

### Coordinator Status (3 endpoints)
```
GET    /api/v1/coordinator/status              # System health
GET    /api/v1/coordinator/statistics          # Aggregated stats
POST   /api/v1/monitoring/start                # Start monitoring
POST   /api/v1/monitoring/stop                 # Stop monitoring
GET    /api/v1/monitoring/session/{id}         # Session details
```

### Testing (1 endpoint)
```
POST   /api/v1/test-alert                      # Send test alert
```

---

## Risk Scoring Algorithm

### Base Risk Scores
```python
not_wearing_helmet: 85
improper_helmet_fit: 65
no_safety_vest: 75
improper_ppe_fit: 60
no_safety_glasses: 50
hazmat_exposure: 95
working_at_height_unprotected: 92
electrical_hazard_exposure: 88
# ... 7 more violation types
```

### Multiplier Factors
```
Score = Base Score
        × Detection Confidence (0-1)
        × Hazard Level Multiplier (1.0-3.0)
        × Night Shift Multiplier (1.0-1.3)
        × Repeated Violation Multiplier (1.0-1.5)
        × Environmental Factor Multiplier (1.0-1.3)
        × Worker Fatigue Multiplier (1.0-1.2)

Final: min(Score, 100) → Mapped to Severity Level
```

### Severity Mapping
```
LOW:      0-25    (Email only)
MEDIUM:   25-50   (Email + SMS)
HIGH:     50-75   (Email + SMS + WhatsApp)
CRITICAL: 75-100  (All channels, immediate)
```

---

## Configuration

All settings are in `backend/config/multinotify_config.py`:

- **EMAIL_CONFIG**: SMTP server, sender email, retry settings
- **TWILIO_CONFIG**: Account credentials, SMS/WhatsApp numbers
- **NOTIFICATION_ROUTING**: Channel selection per severity
- **RISK_SCORING_CONFIG**: Base scores, multipliers, thresholds
- **MULTI_CAMERA_CONFIG**: Max cameras, FPS, resolution settings
- **HAZARD_LEVELS**: Risk multipliers for HIGH/MEDIUM/LOW/CRITICAL areas

---

## Integration with Flask App

The main Flask application (`backend/main.py`) now:

1. Initializes all three services:
   ```python
   advanced_notification_service = initialize_notification_service()
   risk_prediction_engine = initialize_risk_prediction_engine()
   multi_camera_coordinator = initialize_multi_camera_coordinator()
   ```

2. Registers new blueprints:
   ```python
   app.register_blueprint(emergency_alerts_bp)
   app.register_blueprint(multi_camera_bp)
   ```

3. Makes services accessible to routes:
   ```python
   app.advanced_notification_service = advanced_notification_service
   app.risk_prediction_engine = risk_prediction_engine
   app.multi_camera_coordinator = multi_camera_coordinator
   ```

---

## Usage Examples

### Register Emergency Contacts (Max 10)
```bash
curl -X POST http://localhost:5000/api/v1/emergency-contacts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "contact_name": "Manager 1",
    "phone_number": "+1234567890",
    "email": "manager@example.com",
    "alert_critical": true
  }'
```

### Register Cameras (Max 40)
```bash
curl -X POST http://localhost:5000/api/v1/cameras \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "camera_name": "Assembly Floor",
    "location": "Line A",
    "stream_url": "rtsp://192.168.1.100:554/stream",
    "hazard_level": "HIGH"
  }'
```

### View Critical Alerts
```bash
curl "http://localhost:5000/api/v1/risk-alerts?severity=CRITICAL&hours=24" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get System Coordinator Status
```bash
curl http://localhost:5000/api/v1/coordinator/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Performance Considerations

### For 40 Cameras
- **CPU**: 4-6 cores (Intel i7/Xeon equivalent)
- **RAM**: 16-32 GB
- **Network**: Gigabit Ethernet recommended
- **Storage**: 500 GB SSD for frame cache/history

### Dynamic Optimization
The system automatically adjusts:
- FPS: 30 → 20 → 15 fps under load
- Resolution: 640x480 → 528x396 → 416x312
- Frame skipping: Automatically enabled if CPU > 85%

---

## Troubleshooting

### SMS/WhatsApp Not Sending
1. Check Twilio credentials in `.env`
2. Verify phone numbers are E.164 format (+1234567890)
3. Check account balance in Twilio dashboard

### All 40 Camera Slots Full
1. Check active cameras: `GET /api/v1/cameras?status=connected`
2. Deactivate unused cameras: `POST /api/v1/cameras/{id}/deactivate`
3. Check system resources: `GET /api/v1/coordinator/status`

### High CPU/Memory Usage
1. Check coordinator stats: `GET /api/v1/coordinator/statistics`
2. System auto-reduces FPS if CPU > 85%
3. Consider reducing active cameras or increasing priority

---

## Next Steps

1. **Configure Twilio account** (optional for SMS/WhatsApp)
2. **Set up email account** (Gmail/corporate SMTP)
3. **Register emergency contacts** (up to 10)
4. **Add cameras** (up to 40 for monitoring)
5. **Start monitoring session**: `POST /api/v1/monitoring/start`
6. **Monitor alerts**: `GET /api/v1/risk-alerts`
7. **View system health**: `GET /api/v1/coordinator/status`

---

## Reference

- **API Reference**: See `MULTI_CAMERA_API_REFERENCE.md`
- **Configuration**: See `backend/config/multinotify_config.py`
- **Services**: See `backend/services/` directory
- **Routes**: See `backend/routes/emergency_alerts.py` and `multi_camera.py`
