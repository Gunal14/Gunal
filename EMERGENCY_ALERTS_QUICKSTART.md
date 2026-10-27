# Emergency Alerts - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Requirements
```bash
pip install requests python-dotenv twilio
```

### Step 2: Configure WhatsApp Provider

#### For Twilio:
```bash
# .env file
WHATSAPP_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=+1-234-567-8901
```

#### For Meta Cloud API:
```bash
# .env file
WHATSAPP_PROVIDER=meta
META_BUSINESS_ACCOUNT_ID=your_business_id
META_PHONE_NUMBER_ID=your_phone_id
META_ACCESS_TOKEN=your_access_token
```

### Step 3: Initialize Database
```python
from backend.app import create_app
from backend.database.models import db

app = create_app()
with app.app_context():
    db.create_all()
```

### Step 4: Start the Application
```bash
python run.py
```

---

## 📝 Usage Examples

### Example 1: Register User with Mobile Number

```python
import requests
import json

# Registration request
payload = {
    "username": "john_operator",
    "email": "john@factory.com",
    "password": "SafePass123!",
    "confirm_password": "SafePass123!",
    "first_name": "John",
    "last_name": "Operator",
    "mobile_number": "+1-555-123-4567"  # PRIMARY NUMBER
}

response = requests.post(
    'http://localhost:5000/api/auth/register',
    json=payload,
    headers={'Content-Type': 'application/json'}
)

print(response.json())
# Output:
# {
#     "success": true,
#     "message": "Registration successful!",
#     "user": {
#         "user_id": 1,
#         "mobile_number": "+1-555-123-4567",
#         ...
#     }
# }
```

### Example 2: Add Emergency Contact

```python
import requests

# Get auth token from login
token = "your_jwt_token_here"

# Add emergency contact
payload = {
    "contact_name": "Safety Manager",
    "phone_number": "+1-777-890-1234",
    "email": "manager@factory.com",
    "whatsapp_enabled": True,
    "sms_enabled": True,
    "email_enabled": False,
    "alert_critical": True,
    "alert_high": True,
    "alert_medium": True,
    "alert_low": False
}

response = requests.post(
    'http://localhost:5000/api/emergency-contacts',
    json=payload,
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
)

print(response.json())
# Output:
# {
#     "success": true,
#     "message": "Emergency contact added successfully",
#     "contact": {
#         "id": 1,
#         "contact_name": "Safety Manager",
#         "phone_number": "+1-777-890-1234",
#         "verified": false
#     }
# }
```

### Example 3: Get All Emergency Contacts

```python
import requests

token = "your_jwt_token_here"

response = requests.get(
    'http://localhost:5000/api/emergency-contacts',
    headers={'Authorization': f'Bearer {token}'}
)

contacts = response.json()['contacts']

for contact in contacts:
    print(f"📱 {contact['contact_name']}: {contact['phone_number']}")
    print(f"   WhatsApp: {contact['whatsapp_enabled']}")
    print(f"   Verified: {contact['verified']}\n")
```

### Example 4: Trigger Emergency Alert

```python
import requests
from datetime import datetime

token = "your_jwt_token_here"

# Trigger alert
payload = {
    "camera_id": 1,
    "risk_type": "not_wearing_helmet",
    "risk_category": "PPE",
    "severity": "CRITICAL",
    "confidence_score": 0.98,
    "risk_score": 92,
    "location": "Production Floor - Zone A",
    "worker_id": "W-12345",
    "image_url": "https://cdn.example.com/detection_12345.jpg",
    "dashboard_link": "https://dashboard.example.com/alerts/12345"
}

response = requests.post(
    'http://localhost:5000/api/alerts/trigger',
    json=payload,
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
)

result = response.json()

if result['success']:
    print(f"✅ Alert sent to {result['recipients_contacted']} contacts")
    print(f"   Timestamp: {result['timestamp']}")
else:
    print(f"❌ Error: {result['error']}")
```

### Example 5: Send Test Alert

```python
import requests

token = "your_jwt_token_here"

response = requests.post(
    'http://localhost:5000/api/alerts/test',
    json={},
    headers={'Authorization': f'Bearer {token}'}
)

print(response.json())
# Output:
# {
#     "success": true,
#     "message": "Test alert sent to configured emergency contacts",
#     "delivery_status": {
#         "+1-555-123-4567": {
#             "contact_type": "primary",
#             "channels": {
#                 "whatsapp": {"sent": true, "message_id": "wamid.xxx"}
#             }
#         },
#         "+1-777-890-1234": {
#             "contact_type": "additional",
#             "channels": {
#                 "whatsapp": {"sent": true, "message_id": "wamid.yyy"}
#             }
#         }
#     }
# }
```

### Example 6: Update Alert Status

```python
import requests

token = "your_jwt_token_here"
alert_id = "alert_uuid_here"

# Mark as acknowledged
response = requests.put(
    f'http://localhost:5000/api/alerts/{alert_id}/status',
    json={"status": "acknowledged"},
    headers={'Authorization': f'Bearer {token}'}
)

print(response.json())
# Output:
# {
#     "success": true,
#     "message": "Alert status updated to acknowledged"
# }
```

### Example 7: Get Alert History

```python
import requests

token = "your_jwt_token_here"

# Get critical alerts from last 7 days
response = requests.get(
    'http://localhost:5000/api/alerts/history?severity=CRITICAL&limit=50',
    headers={'Authorization': f'Bearer {token}'}
)

alerts = response.json()['alerts']

print(f"Total alerts: {len(alerts)}\n")

for alert in alerts:
    print(f"🚨 {alert['risk_type']} - {alert['severity']}")
    print(f"   Location: {alert['location']}")
    print(f"   Risk Score: {alert['risk_score']}/100")
    print(f"   Status: {alert['status']}")
    print(f"   Time: {alert['created_at']}\n")
```

### Example 8: Delete Emergency Contact

```python
import requests

token = "your_jwt_token_here"
contact_id = 1

response = requests.delete(
    f'http://localhost:5000/api/emergency-contacts/{contact_id}',
    headers={'Authorization': f'Bearer {token}'}
)

print(response.json())
# Output:
# {
#     "success": true,
#     "message": "Emergency contact deleted successfully"
# }
```

---

## 🧪 Testing Checklist

### Basic Functionality
- [ ] User registration with phone number
- [ ] Phone format validation works
- [ ] Can add emergency contact
- [ ] Can view emergency contacts
- [ ] Can update emergency contact
- [ ] Can delete emergency contact

### WhatsApp Integration
- [ ] WhatsApp credentials verified
- [ ] Can send test message
- [ ] Receives test alert on WhatsApp
- [ ] Message includes required info:
  - [ ] Alert type
  - [ ] Location
  - [ ] Risk score
  - [ ] Dashboard link
  - [ ] Timestamp

### Alert Triggering
- [ ] Can trigger emergency alert
- [ ] Alert sent to primary number
- [ ] Alert sent to all enabled contacts
- [ ] Alert respects severity filters
- [ ] Alert history updated
- [ ] Can update alert status

### Error Handling
- [ ] Invalid phone numbers rejected
- [ ] Invalid API tokens rejected
- [ ] Database errors handled gracefully
- [ ] WhatsApp API failures logged
- [ ] Fallback to secondary contact works

---

## 🔧 Troubleshooting

### WhatsApp Messages Not Sending

**Problem**: Messages fail silently
**Solution**:
```bash
# Check environment variables
echo $TWILIO_ACCOUNT_SID
echo $TWILIO_AUTH_TOKEN

# Test credentials directly
python -c "
from backend.services.whatsapp_service import TwilioWhatsAppProvider
p = TwilioWhatsAppProvider(
    account_sid='YOUR_SID',
    auth_token='YOUR_TOKEN',
    from_number='YOUR_NUMBER'
)
print('✓ Verified!' if p.verify_credentials() else '✗ Failed!')
"
```

### Phone Number Validation Fails

**Problem**: Valid phone numbers rejected
**Solution**:
```python
# Test validation function
from backend.routes.emergency_contacts_api import validate_phone_number

test_numbers = [
    "+1-234-567-8900",
    "+1 234 567 8900",
    "1234567890",
    "+1(234)567-8900"
]

for number in test_numbers:
    valid, formatted, cc = validate_phone_number(number)
    print(f"{number:20} → Valid: {valid}, Formatted: {formatted}")
```

### Alert Not Triggering

**Problem**: Alerts don't send despite successful API call
**Solution**:
```bash
# Check if dispatcher running in background
ps aux | grep alert_dispatcher

# Check logs for errors
tail -f logs/app.log

# Verify user has emergency contacts
sqlite3 safety.db "SELECT * FROM emergency_contacts WHERE user_id=1;"
```

### Database Connection Error

**Problem**: "Database is locked" error
**Solution**:
```bash
# Check database file permissions
ls -la safety.db

# Reset database if corrupted
rm safety.db
python -c "from backend.app import create_app; from backend.database.models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

---

## 📱 Frontend Integration

### Add Settings Link to Dashboard

```html
<!-- In your dashboard template -->
<a href="/settings/emergency-contacts" class="menu-item">
    <i class="icon-emergency"></i>
    <span>Emergency Contacts</span>
</a>
```

### Embed Settings Page

```html
<!-- emergency_contacts_iframe.html -->
<div id="emergency-settings">
    <!-- Loads emergency_settings.html -->
    <iframe src="/templates/emergency_settings.html" width="100%" height="800px"></iframe>
</div>
```

---

## 🚨 Production Deployment

### Environment Setup
```bash
# Production .env
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=postgresql://user:pass@localhost/safety_db

# Security
SECRET_KEY=your-secret-key-min-32-chars-long
JWT_SECRET=your-jwt-secret-min-32-chars

# WhatsApp
WHATSAPP_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_NUMBER=+1-xxx-xxx-xxxx

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Start Services
```bash
# Start with production WSGI server
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:create_app()

# Or using Docker
docker-compose up -d
```

### Monitor Alerts
```bash
# Real-time log monitoring
tail -f logs/app.log | grep "WhatsApp\|Alert\|Error"

# Database health check
sqlite3 safety.db "SELECT COUNT(*) FROM risk_alerts WHERE created_at > datetime('now', '-1 hour');"
```

---

## 📞 API Response Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Alert sent successfully |
| 201 | Created | Emergency contact added |
| 400 | Bad Request | Invalid phone number |
| 401 | Unauthorized | Missing auth token |
| 403 | Forbidden | Access denied to contact |
| 404 | Not Found | Contact doesn't exist |
| 409 | Conflict | Email already registered |
| 500 | Server Error | Database connection failed |
| 503 | Service Unavailable | WhatsApp provider down |

---

## 💾 Data Backup

```bash
# Backup database
cp safety.db safety.db.backup

# Backup with timestamp
cp safety.db safety.db.$(date +%Y%m%d_%H%M%S).backup

# Monthly full backup
0 2 1 * * /bin/bash -c 'cp /path/to/safety.db /backups/safety_$(date +\%Y\%m\%d).db'
```

---

## 📊 Monitoring Dashboard

Create monitoring endpoint:

```python
@app.route('/api/monitoring/health')
def health_check():
    """System health status"""
    return jsonify({
        'status': 'healthy',
        'database': check_db_connection(),
        'whatsapp': check_whatsapp_provider(),
        'alert_queue': get_queue_status(),
        'timestamp': datetime.utcnow().isoformat()
    })
```

---

**Quick Reference Card**:
- 📱 **Register**: `POST /api/auth/register` (add `mobile_number`)
- ➕ **Add Contact**: `POST /api/emergency-contacts`
- 📋 **List Contacts**: `GET /api/emergency-contacts`
- 🚨 **Trigger Alert**: `POST /api/alerts/trigger`
- 🧪 **Test Alert**: `POST /api/alerts/test`
- 📊 **History**: `GET /api/alerts/history`

---

**Version**: 1.0 | **Date**: March 2026
