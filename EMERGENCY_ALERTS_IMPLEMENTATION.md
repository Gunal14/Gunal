# Emergency Alert Notification System - Complete Implementation Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Database Schema](#database-schema)
4. [WhatsApp API Integration](#whatsapp-api-integration)
5. [API Endpoints](#api-endpoints)
6. [Frontend Setup](#frontend-setup)
7. [Configuration Guide](#configuration-guide)
8. [Testing & Deployment](#testing--deployment)
9. [Security Considerations](#security-considerations)

---

## 🎯 Overview

The Emergency Alert Notification System provides **real-time emergency alerts** to users and their emergency contacts via multiple channels:
- **WhatsApp** (Primary - Real-time messages)
- **SMS** (Fallback)
- **Email** (Supplementary)

### Key Features
✅ Primary mobile number registration during signup  
✅ Add up to 10 additional emergency contacts  
✅ Multi-channel notification delivery (WhatsApp, SMS, Email)  
✅ Severity-based alert filtering  
✅ Real-time alert triggering with background processing  
✅ Alert history and status tracking  
✅ Contact verification system  

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Safety Monitoring System                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐         ┌──────────────────────┐  │
│  │   AI Detection       │         │   Frontend (Web)     │  │
│  │   System             │────────▶│   - Settings Page    │  │
│  │   (Risk Detection)   │         │   - Alert History    │  │
│  └──────────────────────┘         └──────────────────────┘  │
│           │                                                   │
│           │                                                   │
│           ▼                                                   │
│  ┌──────────────────────────────────────────────────────────┐│
│  │         Alert Dispatcher Service                         ││
│  │  - Checks user & emergency contacts                      ││
│  │  - Formats alert messages                                ││
│  │  - Routes to notification channels                       ││
│  └──────────────┬───────────────────────────────────────────┘│
│                 │                                             │
│     ┌───────────┼───────────┐                                │
│     │           │           │                                │
│     ▼           ▼           ▼                                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                        │
│  │WhatsApp │ │  SMS    │ │ Email   │                        │
│  │Service  │ │ Service │ │Service  │                        │
│  └────┬────┘ └────┬────┘ └────┬────┘                        │
│       │           │           │                              │
│       ▼           ▼           ▼                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Primary + Additional Emergency Contacts              ││
│  │  📱 +1-234-567-8900 (Primary)                         ││
│  │  📱 +1-555-123-4567 (Contact 1)                       ││
│  │  📱 +1-777-890-1234 (Contact 2)                       ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

### User Model (Extended)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(120) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(120),
    last_name VARCHAR(120),
    
    -- Emergency Contact Fields (NEW)
    mobile_number VARCHAR(20) NOT NULL,
    country_code VARCHAR(5) DEFAULT '+1',
    phone_verified BOOLEAN DEFAULT FALSE,
    
    role VARCHAR(50) DEFAULT 'operator',
    department VARCHAR(120),
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Emergency Contacts Table (NEW)
```sql
CREATE TABLE emergency_contacts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE KEY (users.id),
    contact_name VARCHAR(200) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    country_code VARCHAR(5) DEFAULT '+1',
    email VARCHAR(255),
    
    -- Notification Channels
    whatsapp_enabled BOOLEAN DEFAULT TRUE,
    sms_enabled BOOLEAN DEFAULT TRUE,
    email_enabled BOOLEAN DEFAULT TRUE,
    
    -- Severity Filters
    alert_low BOOLEAN DEFAULT FALSE,
    alert_medium BOOLEAN DEFAULT TRUE,
    alert_high BOOLEAN DEFAULT TRUE,
    alert_critical BOOLEAN DEFAULT TRUE,
    
    -- Verification
    verified BOOLEAN DEFAULT FALSE,
    verification_code VARCHAR(6),
    verified_at DATETIME,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Risk Alerts Table
```sql
CREATE TABLE risk_alerts (
    id INTEGER PRIMARY KEY,
    alert_id VARCHAR(36) UNIQUE NOT NULL,
    camera_id INTEGER NOT NULL,
    
    risk_type VARCHAR(100) NOT NULL,
    risk_category VARCHAR(50) NOT NULL,  -- PPE, POSTURE, BEHAVIOR, HAZMAT
    
    severity VARCHAR(20) NOT NULL,  -- LOW, MEDIUM, HIGH, CRITICAL
    confidence_score FLOAT,
    risk_score INT,  -- 0-100
    
    worker_id VARCHAR(100),
    location VARCHAR(255),
    
    -- Detection details
    environmental_conditions JSON,
    detection_count INT DEFAULT 1,
    first_detection_time DATETIME,
    last_detection_time DATETIME,
    
    -- Evidence
    image_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    
    -- Alert Lifecycle
    status VARCHAR(50) DEFAULT 'pending',  -- pending, notified, acknowledged, resolved, dismissed
    notified BOOLEAN DEFAULT FALSE,
    notified_at DATETIME,
    
    created_at DATETIME,
    updated_at DATETIME,
    
    INDEX idx_severity (severity),
    INDEX idx_status (status),
    INDEX idx_camera (camera_id),
    INDEX idx_created (created_at)
);
```

---

## 📱 WhatsApp API Integration

### Option 1: Twilio WhatsApp API (Recommended)

#### Setup
1. **Create Twilio Account**: https://www.twilio.com/
2. **Get Credentials**:
   - Account SID
   - Auth Token
   - WhatsApp Number (sandbox or production)

#### Environment Configuration
```bash
# .env file
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+1-234-567-8901
WHATSAPP_PROVIDER=twilio
```

#### Implementation (Python)
```python
from backend.services.whatsapp_service import TwilioWhatsAppProvider, WhatsAppMessage
from datetime import datetime

# Initialize provider
provider = TwilioWhatsAppProvider(
    account_sid="your_account_sid",
    auth_token="your_auth_token",
    from_number="+1-234-567-8901"
)

# Verify credentials
if provider.verify_credentials():
    print("✓ Twilio credentials verified")
else:
    print("✗ Failed to verify Twilio credentials")

# Send alert message
message = WhatsAppMessage(
    recipient="+1-555-123-4567",
    title="CRITICAL SAFETY ALERT",
    risk_type="not_wearing_helmet",
    location="Factory Floor - Section A",
    timestamp=datetime.utcnow(),
    dashboard_link="https://dashboard.example.com/alerts/123",
    message_type="emergency",
    image_url="https://example.com/image.jpg"
)

success, message_id = provider.send_message(message)
if success:
    print(f"✓ Message sent: {message_id}")
else:
    print(f"✗ Failed: {message_id}")
```

### Option 2: Meta Cloud WhatsApp API

#### Setup
1. **Create Meta Business Account**: https://business.facebook.com/
2. **Set up WhatsApp Business API**
3. **Get Credentials**:
   - Business Account ID
   - Phone Number ID
   - Access Token

#### Environment Configuration
```bash
# .env file
META_BUSINESS_ACCOUNT_ID=your_business_account_id
META_PHONE_NUMBER_ID=your_phone_number_id
META_ACCESS_TOKEN=your_access_token
WHATSAPP_PROVIDER=meta
```

#### Implementation (Python)
```python
from backend.services.whatsapp_service import MetaWhatsAppProvider, WhatsAppMessage
from datetime import datetime

# Initialize provider
provider = MetaWhatsAppProvider(
    business_account_id="your_business_account_id",
    phone_number_id="your_phone_number_id",
    access_token="your_access_token"
)

# Send alert
message = WhatsAppMessage(
    recipient="+1-555-123-4567",
    title="CRITICAL ALERT",
    risk_type="unsafe_behavior",
    location="Warehouse B",
    timestamp=datetime.utcnow(),
    dashboard_link="https://dashboard.example.com/alerts/456"
)

success, message_id = provider.send_message(message)
```

---

## 🔌 API Endpoints

### Authentication Endpoints

#### Register with Mobile Number
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "mobile_number": "+1-234-567-8900"
}
```

**Response**:
```json
{
    "success": true,
    "message": "Registration successful! Please login with your credentials.",
    "user": {
        "user_id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "mobile_number": "+1-234-567-8900",
        "role": "operator"
    }
}
```

---

### Emergency Contact Management

#### Get All Emergency Contacts
```http
GET /api/emergency-contacts
Authorization: Bearer {token}
```

#### Add Emergency Contact
```http
POST /api/emergency-contacts
Authorization: Bearer {token}
Content-Type: application/json

{
    "contact_name": "Emergency Manager",
    "phone_number": "+1-555-123-4567",
    "email": "manager@example.com",
    "whatsapp_enabled": true,
    "sms_enabled": true,
    "email_enabled": false,
    "alert_low": false,
    "alert_medium": true,
    "alert_high": true,
    "alert_critical": true
}
```

#### Update Emergency Contact
```http
PUT /api/emergency-contacts/{contact_id}
Authorization: Bearer {token}
Content-Type: application/json

{
    "contact_name": "Updated Name",
    "phone_number": "+1-555-987-6543",
    "alert_medium": false
}
```

#### Delete Emergency Contact
```http
DELETE /api/emergency-contacts/{contact_id}
Authorization: Bearer {token}
```

#### Verify Emergency Contact
```http
POST /api/emergency-contacts/{contact_id}/verify
Authorization: Bearer {token}
Content-Type: application/json

{
    "otp": "123456"
}
```

#### Get Primary Number
```http
GET /api/emergency-contacts/primary-number
Authorization: Bearer {token}
```

#### Update Primary Number
```http
PUT /api/emergency-contacts/primary-number
Authorization: Bearer {token}
Content-Type: application/json

{
    "mobile_number": "+1-234-567-8900"
}
```

---

### Alert Endpoints

#### Trigger Emergency Alert
```http
POST /api/alerts/trigger
Authorization: Bearer {token}
Content-Type: application/json

{
    "camera_id": 1,
    "risk_type": "not_wearing_helmet",
    "risk_category": "PPE",
    "severity": "CRITICAL",
    "confidence_score": 0.95,
    "risk_score": 85,
    "location": "Factory Floor - Section A",
    "worker_id": "W001",
    "image_url": "https://cdn.example.com/image.jpg",
    "dashboard_link": "https://dashboard.example.com/alerts/123"
}
```

**Response**:
```json
{
    "success": true,
    "message": "Emergency alert triggered successfully",
    "recipients_contacted": 3,
    "timestamp": "2026-03-20T10:30:45.123456"
}
```

#### Send Test Alert
```http
POST /api/alerts/test
Authorization: Bearer {token}
Content-Type: application/json

{}
```

#### Get Alert History
```http
GET /api/alerts/history?limit=50&offset=0&severity=CRITICAL
Authorization: Bearer {token}
```

#### Update Alert Status
```http
PUT /api/alerts/{alert_id}/status
Authorization: Bearer {token}
Content-Type: application/json

{
    "status": "acknowledged"
}
```

---

## 🎨 Frontend Setup

### Settings Page Route
Add to your main Flask app:
```python
@app.route('/settings/emergency-contacts')
@require_auth
def emergency_settings():
    return render_template('emergency_settings.html')
```

### Navigation Links
Update your main template to add link to emergency settings:
```html
<a href="/settings/emergency-contacts" class="nav-link">
    🚨 Emergency Contacts
</a>
```

### Features on Settings Page
- ✅ View and edit primary mobile number
- ✅ Add/edit/delete emergency contacts (up to 10)
- ✅ Configure notification channels (WhatsApp, SMS, Email)
- ✅ Set severity level filters
- ✅ Verify phone numbers
- ✅ Send test alerts
- ✅ View verification status

---

## ⚙️ Configuration Guide

### 1. Environment Setup

Create `.env` file in project root:
```bash
# Database
DATABASE_URL=sqlite:///safety_monitoring.db

# WhatsApp - Choose ONE provider
# Option 1: Twilio
WHATSAPP_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+1-234-567-8901

# Option 2: Meta
# WHATSAPP_PROVIDER=meta
# META_BUSINESS_ACCOUNT_ID=your_account_id
# META_PHONE_NUMBER_ID=your_phone_id
# META_ACCESS_TOKEN=your_token

# Email (for email notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# SMS (Optional - Twilio)
TWILIO_SMS_ENABLED=false
```

### 2. Initialize Database

```python
from backend.app import create_app
from backend.database.models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("✓ Database initialized")
```

### 3. Update Flask App

```python
# backend/app.py
from flask import Flask
from backend.database.models import db
from backend.routes.emergency_contacts_api import init_emergency_routes
from backend.routes.alerts_api import init_alert_api_routes
from backend.services.alert_dispatcher import initialize_alert_dispatcher
from backend.services.whatsapp_service import initialize_whatsapp_service

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safety.db'
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize services
    with app.app_context():
        # Initialize WhatsApp service
        initialize_whatsapp_service(app)
        
        # Initialize alert dispatcher
        initialize_alert_dispatcher(app, db=db)
        
        # Register blueprints
        init_emergency_routes(app)
        init_alert_api_routes(app, db=db)
    
    return app
```

### 4. Install Dependencies

Add to `requirements.txt`:
```
requests>=2.28.0
python-dotenv>=0.21.0
twilio>=8.0.0
```

Then install:
```bash
pip install -r requirements.txt
```

---

## 🧪 Testing & Deployment

### Unit Testing

```python
# test_emergency_alerts.py
import unittest
from backend.services.whatsapp_service import WhatsAppMessage
from datetime import datetime

class TestWhatsAppMessage(unittest.TestCase):
    def test_message_creation(self):
        msg = WhatsAppMessage(
            recipient="+1-234-567-8900",
            title="TEST ALERT",
            risk_type="test",
            location="Test Location",
            timestamp=datetime.utcnow(),
            dashboard_link="https://test.com"
        )
        
        self.assertEqual(msg.recipient, "+1-234-567-8900")
        self.assertEqual(msg.severity, "emergency")
    
    def test_phone_validation(self):
        from backend.routes.emergency_contacts_api import validate_phone_number
        
        # Valid formats
        valid, formatted, cc = validate_phone_number("+1-234-567-8900")
        self.assertTrue(valid)
        self.assertIn("+1", formatted)
        
        # Invalid formats
        valid, formatted, cc = validate_phone_number("invalid")
        self.assertFalse(valid)

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
# test_alert_flow.py
def test_complete_alert_flow():
    """Test complete alert triggering flow"""
    from backend.services.alert_dispatcher import AlertTrigger, get_alert_dispatcher
    
    # Create alert
    alert = AlertTrigger(
        camera_id=1,
        risk_type="not_wearing_helmet",
        risk_category="PPE",
        severity="CRITICAL",
        confidence_score=0.95,
        risk_score=85,
        location="Test Factory"
    )
    
    # Dispatch
    dispatcher = get_alert_dispatcher()
    result = dispatcher.trigger_emergency_alert(alert, user_id=1)
    
    assert result['success'] == True
    assert result['recipients_contacted'] > 0
```

### Manual Testing Checklist

- [ ] Register new user with mobile number
- [ ] Verify phone number format validation
- [ ] Add emergency contact via API
- [ ] Verify contact via web UI
- [ ] Send test alert
- [ ] Verify WhatsApp message received
- [ ] Update emergency contact
- [ ] Delete emergency contact
- [ ] Trigger real alert from AI system
- [ ] Check alert history
- [ ] Verify alert status updates

---

## 🔒 Security Considerations

### 1. Phone Number Protection
```sql
-- Encrypt sensitive phone numbers in database
ALTER TABLE users ADD COLUMN mobile_number_encrypted VARBINARY(255);
ALTER TABLE emergency_contacts ADD COLUMN phone_number_encrypted VARBINARY(255);
```

### 2. Authentication & Authorization
```python
# Only users can access their own contacts
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = request.user.get('user_id')
        contact_id = kwargs.get('contact_id')
        
        # Verify ownership
        contact = EmergencyContact.query.filter_by(
            id=contact_id,
            user_id=user_id  # Ensure user owns contact
        ).first()
        
        if not contact:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return f(*args, **kwargs)
    return decorated
```

### 3. Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.user.get('user_id'))

@alert_api.route('/trigger', methods=['POST'])
@limiter.limit("10 per minute")  # Max 10 alerts per minute
def trigger_alert():
    # ...
```

### 4. API Key Verification
```python
@app.before_request
def verify_api_key():
    token = request.headers.get('Authorization')
    if not token or not validate_token(token):
        return jsonify({'error': 'Unauthorized'}), 401
```

### 5. Data Retention & Privacy
```python
# Auto-delete old alerts after 90 days
def cleanup_old_alerts():
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=90)
    RiskAlert.query.filter(RiskAlert.created_at < cutoff).delete()
    db.session.commit()
```

### 6. Audit Logging
```python
from backend.database.models import AuditLog

def log_action(user_id, action, details):
    log = AuditLog(
        user_id=user_id,
        action=action,
        details=details,
        timestamp=datetime.utcnow(),
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
```

---

## 📊 Monitoring & Analytics

### Alert Metrics
```python
def get_alert_statistics(days=7):
    from datetime import datetime, timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    stats = {
        'total_alerts': RiskAlert.query.filter(RiskAlert.created_at >= cutoff).count(),
        'critical': RiskAlert.query.filter(
            RiskAlert.severity == 'CRITICAL',
            RiskAlert.created_at >= cutoff
        ).count(),
        'high': RiskAlert.query.filter(
            RiskAlert.severity == 'HIGH',
            RiskAlert.created_at >= cutoff
        ).count(),
        'acknowledged': RiskAlert.query.filter(
            RiskAlert.status == 'acknowledged',
            RiskAlert.created_at >= cutoff
        ).count()
    }
    
    return stats
```

### Alert Delivery Success Rate
```python
def calculate_delivery_rate():
    from sqlalchemy import func
    
    total = RiskAlert.query.filter(RiskAlert.notified == True).count()
    if total == 0:
        return 0
    
    # Count successful deliveries
    successful = RiskAlert.query.filter(
        RiskAlert.notified == True,
        RiskAlert.status.in_(['acknowledged', 'resolved'])
    ).count()
    
    return (successful / total) * 100
```

---

## 🚀 Deployment

### Docker Setup
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:create_app()"]
```

### Production Checklist
- [ ] Set up SSL/TLS certificates
- [ ] Configure HTTPS only
- [ ] Set strong password policies
- [ ] Enable database backups
- [ ] Set up monitoring and alerting
- [ ] Configure rate limiting
- [ ] Enable audit logging
- [ ] Test disaster recovery
- [ ] Document operational procedures
- [ ] Train staff on emergency procedures

---

## 📞 Support & Troubleshooting

### Common Issues

**WhatsApp Message Not Sent**
```bash
# Check credentials
python -c "from backend.services.whatsapp_service import TwilioWhatsAppProvider; p = TwilioWhatsAppProvider(...); print(p.verify_credentials())"

# Check logs
tail -f logs/whatsapp.log
```

**Database Connection Error**
```bash
# Verify database URL
export DATABASE_URL=sqlite:///safety.db
python manage.py db upgrade
```

**Phone Number Validation Fails**
```python
# Test validation
from backend.routes.emergency_contacts_api import validate_phone_number
valid, formatted, cc = validate_phone_number("+1-234-567-8900")
print(f"Valid: {valid}, Formatted: {formatted}, Code: {cc}")
```

---

## 📚 API Documentation

Full API documentation available at: `/api/docs` (Swagger/OpenAPI)

---

**Document Version**: 1.0  
**Last Updated**: March 2026  
**Maintained By**: Safety Monitoring Team
