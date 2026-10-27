# Integration & Usage Guide

## 🔌 Quick Integration Examples

### 1. Using AI Detection Module

```python
from ai import AdvancedSafetyDetector, MultiCameraManager

# Initialize detector
detector = AdvancedSafetyDetector(
    model_type='ensemble',  # Options: cascade, ssd, yolo, ensemble
    confidence_threshold=0.5
)

# Process a frame
import cv2
frame = cv2.imread('safety_image.jpg')

results = detector.detect(
    frame=frame,
    camera_id=0
)

print(f"Workers detected: {len(results['workers'])}")
print(f"Helmets detected: {len(results['helmets'])}")
print(f"Violations: {results['violations']}")
print(f"Confidence: {results['confidence_scores']}")
```

### 2. Multi-Camera Management

```python
from ai import MultiCameraManager

# Initialize manager
camera_manager = MultiCameraManager(max_cameras=16)

# Add cameras
camera_manager.add_camera(
    camera_id=1,
    source='http://camera1.local:8080/stream',
    location='Production Floor A'
)

# Get camera status
status = camera_manager.get_camera_status(camera_id=1)
print(f"Camera 1 is {'active' if status['active'] else 'inactive'}")

# Get last frame for camera
frame = camera_manager.get_last_frame(camera_id=1)
```

### 3. Model Management

```python
from ai import ModelManager

model_manager = ModelManager()

# Register a new model
model_manager.register_model(
    name='helmet_detector_v2',
    version='2.1.0',
    model_type='yolo',
    accuracy=0.94
)

# Switch active model
model_manager.set_active_model('helmet_detector_v2')

# Get model info
current = model_manager.get_active_model()
print(f"Current model: {current['name']} v{current['version']}")
```

### 4. Incident Management Service

```python
from backend.services import IncidentManagementService

incident_service = IncidentManagementService(db_session=None)

# Create incident
incident_id = incident_service.create_incident(
    incident_type='missing_helmet',
    severity='high',
    camera_id=1,
    location='Production Floor A',
    worker_id=42,
    message='Worker without helmet detected',
    image_url='/static/incidents/incident_001.jpg'
)

# Get incident
incident = incident_service.get_incident(incident_id)
print(f"Incident {incident['incident_id']}: {incident['type']}")

# Acknowledge incident
incident_service.acknowledge_incident(
    incident_id=incident_id,
    user_id=1,
    notes='Supervisor acknowledged, worker notified'
)

# Resolve incident
incident_service.resolve_incident(
    incident_id=incident_id,
    user_id=1,
    resolution_type='corrected',
    notes='Worker complied with safety protocols'
)

# Get statistics
stats = incident_service.get_incident_statistics(hours=24)
print(f"Total incidents (24h): {stats['total_incidents']}")
print(f"Open incidents: {stats['open_incidents']}")
```

### 5. Authentication Service

```python
from backend.services import AuthenticationService

auth_service = AuthenticationService(
    secret_key='your-secret-key',
    access_token_expires=3600  # 1 hour
)

# Hash password
password_hash = auth_service.hash_password('user123')

# Verify password
is_valid = auth_service.verify_password('user123', password_hash)

# Create tokens
access_token = auth_service.create_access_token(
    user_id=1,
    username='john_doe',
    role='supervisor'
)

# Verify token
payload = auth_service.verify_token(access_token)
print(f"Token valid for user: {payload['username']}")

# Refresh token
refresh_token = auth_service.create_refresh_token(user_id=1, username='john_doe')
new_access_token = auth_service.refresh_access_token(refresh_token)
```

### 6. Notification Service

```python
from backend.services import NotificationService

notification_service = NotificationService(mail_config={
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USERNAME': 'your-email@gmail.com',
    'MAIL_PASSWORD': 'app-password',
    'MAIL_DEFAULT_SENDER': 'alerts@safety-system.com'
})

# Send email alert
notification_service.send_email_alert(
    recipient='supervisor@company.com',
    alert_type='missing_helmet',
    message='High-risk incident detected in Production Floor A',
    severity='HIGH'
)

# Send SMS alert
notification_service.send_sms_alert(
    phone='+1234567890',
    message='Critical safety alert: Multiple workers without helmets'
)

# Send webhook alert
notification_service.send_webhook_alert(
    webhook_url='https://company-systems.com/safety-webhook',
    alert_data={
        'incident_type': 'overcrowding',
        'severity': 'MEDIUM',
        'camera_id': 1,
        'location': 'Production Floor A'
    }
)
```

### 7. Analytics Service

```python
from backend.services import AnalyticsService

analytics_service = AnalyticsService(db_session=None)

# Get compliance metrics
compliance = analytics_service.get_compliance_metrics(days=30)
print(f"Compliance rate: {compliance['overall_compliance']}%")

# Get incident statistics
incidents = analytics_service.get_incident_statistics(days=7)
print(f"Incidents this week: {incidents['total_incidents']}")

# Get worker statistics
worker_stats = analytics_service.get_worker_statistics(worker_id=42)
print(f"Worker safety score: {worker_stats['safety_score']}")
```

### 8. Reporting Service

```python
from backend.services import ReportingService

reporting_service = ReportingService(db_session=None)

# Generate daily report
daily_report = reporting_service.generate_daily_report()
print(f"Total incidents today: {daily_report['summary']['total_incidents']}")

# Generate weekly report
weekly_report = reporting_service.generate_weekly_report()

# Generate monthly report
monthly_report = reporting_service.generate_monthly_report()

# Export to PDF
reporting_service.export_to_pdf(
    report=daily_report,
    filename='daily_safety_report.pdf'
)
```

## 🌐 API Usage Examples

### Login & Authentication

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password"
  }'

# Response:
{
  "success": true,
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer"
  }
}
```

### Get Incidents

```bash
# Get all open incidents
curl -X GET http://localhost:5000/api/incidents \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."

# Get incidents for specific camera
curl -X GET "http://localhost:5000/api/incidents/camera/1?hours=24" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."

# Get incident statistics
curl -X GET "http://localhost:5000/api/incidents/statistics?hours=24" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Create Incident

```bash
curl -X POST http://localhost:5000/api/incidents \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "type": "missing_helmet",
    "severity": "high",
    "camera_id": 1,
    "location": "Production Floor A",
    "worker_id": 42,
    "message": "Worker without helmet detected",
    "image_url": "/static/incidents/incident_001.jpg"
  }'
```

### Resolve Incident

```bash
curl -X PUT http://localhost:5000/api/incidents/<incident_id>/resolve \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "resolution_type": "corrected",
    "notes": "Worker complied with safety protocols"
  }'
```

### Get Analytics Dashboard

```bash
curl -X GET "http://localhost:5000/api/analytics/dashboard?days=7" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

## 🔄 Workflow Examples

### Complete Incident Workflow

1. **Detection** - System detects violation
2. **Incident Creation** - Incident created automatically
3. **Notification** - Alerts sent to supervisors
4. **Acknowledgment** - Supervisor acknowledges incident
5. **Investigation** - Supervisor reviews data
6. **Resolution** - Incident resolved with action taken
7. **Audit** - All actions logged for compliance

### User Login Workflow

1. User enters credentials
2. System validates credentials
3. System generates access & refresh tokens
4. User authorized for API calls
5. Token expires after 1 hour
6. User refreshes using refresh token
7. User logs out (optional)

## 🛠️ Configuration Examples

### Development Environment

```python
# .env file
FLASK_ENV=development
SECRET_KEY=dev-secret-key-123
DATABASE_URL=sqlite:///safety_monitoring.db
DEBUG=True
MAIL_SERVER=localhost
MAX_CAMERAS=4
```

### Production Environment

```python
# .env file
FLASK_ENV=production
SECRET_KEY=prod-secret-key-xyz
DATABASE_URL=postgresql://user:pass@localhost/safety_db
DEBUG=False
MAIL_SERVER=smtp.gmail.com
MAX_CAMERAS=16
ALLOWED_HOSTS=safety.company.com
```

## 📊 Common Queries

### Get incidents for specific worker this month

```python
from datetime import datetime, timedelta
from backend.services import IncidentManagementService

incident_service = IncidentManagementService(db_session)

# Get incidents for last 30 days
incidents = incident_service.get_incidents_by_worker(
    worker_id=42,
    hours=30*24  # 30 days
)

# Filter by type
helmet_incidents = [i for i in incidents if i['type'] == 'missing_helmet']
print(f"Helmet violations: {len(helmet_incidents)}")
```

### Generate compliance report

```python
from backend.services import AnalyticsService

analytics = AnalyticsService(db_session)

# Get monthly compliance
compliance = analytics.get_compliance_metrics(days=30)

# Get by department
stats = analytics.get_incident_statistics(days=30)

report = {
    'period': 'Monthly',
    'compliance_rate': compliance['overall_compliance'],
    'total_incidents': stats['total_incidents'],
    'by_severity': stats['by_severity']
}
```

## 🚨 Error Handling

```python
# API responses follow consistent format:

# Success
{
    "success": true,
    "message": "Operation successful",
    "data": {...}
}

# Error
{
    "success": false,
    "message": "Error description",
    "error_code": "ERROR_TYPE",
    "details": {...}
}

# Authentication Error
{
    "error": "Invalid or expired token",
    "status": 401
}

# Permission Error
{
    "error": "Insufficient permissions",
    "status": 403
}
```

---

For more details, see [ARCHITECTURE.md](ARCHITECTURE.md)
