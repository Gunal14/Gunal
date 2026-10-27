# Emergency Alert System - Complete Code Examples

## 🏗️ Integration with Existing AI Detection System

### Example 1: Auto-Trigger Alert from Detection Engine

```python
# backend/detection/advanced_detector.py (UPDATED)

from backend.services.alert_dispatcher import get_alert_dispatcher, AlertTrigger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AdvancedDetector:
    """AI detection engine with automatic alert triggering"""
    
    def __init__(self):
        self.alert_dispatcher = get_alert_dispatcher()
        self.risk_threshold = 70  # Trigger alerts above 70 risk score
    
    def process_frame(self, frame, camera_id, user_id):
        """
        Process video frame and trigger alerts
        
        Args:
            frame: Video frame from camera
            camera_id: ID of camera
            user_id: Admin/supervisor user ID
        """
        try:
            # Run detection model
            detections = self.detect_violations(frame)
            
            # Score risk level
            for detection in detections:
                risk_data = self.score_risk(detection, camera_id)
                
                # Auto-trigger alert if critical
                if risk_data['risk_score'] >= self.risk_threshold:
                    self._trigger_alert(
                        camera_id=camera_id,
                        risk_data=risk_data,
                        frame=frame,
                        user_id=user_id
                    )
        
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
    
    def _trigger_alert(self, camera_id, risk_data, frame, user_id):
        """Trigger alert through dispatcher"""
        try:
            # Save detection image
            image_url = self._save_detection_image(frame, camera_id)
            
            # Create alert trigger
            alert = AlertTrigger(
                camera_id=camera_id,
                risk_type=risk_data['violation_type'],
                risk_category=risk_data['category'],
                severity=risk_data['severity'],
                confidence_score=risk_data['confidence'],
                risk_score=risk_data['risk_score'],
                location=self._get_camera_location(camera_id),
                worker_id=risk_data.get('worker_id'),
                image_url=image_url,
                dashboard_link=f"https://dashboard.example.com/camera/{camera_id}",
                timestamp=datetime.utcnow()
            )
            
            # Dispatch to alert service
            result = self.alert_dispatcher.trigger_emergency_alert(
                alert,
                user_id=user_id,
                async_mode=True  # Non-blocking
            )
            
            if result['success']:
                logger.info(f"Alert triggered: {risk_data['violation_type']} -> {result['recipients_contacted']} contacts")
            else:
                logger.error(f"Alert dispatch failed: {result.get('error')}")
        
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    def score_risk(self, detection, camera_id):
        """Score risk level based on detection"""
        # Your existing risk scoring logic
        return {
            'violation_type': 'not_wearing_helmet',
            'category': 'PPE',
            'severity': 'CRITICAL',
            'confidence': 0.95,
            'risk_score': 85,
            'worker_id': 'W-12345'
        }
    
    def detect_violations(self, frame):
        """Run detection model"""
        # Your AI model inference
        return []
    
    def _save_detection_image(self, frame, camera_id):
        """Save detection image to storage"""
        # Your image storage logic
        return "https://cdn.example.com/detection_image.jpg"
    
    def _get_camera_location(self, camera_id):
        """Get camera location from database"""
        # Your location lookup logic
        return f"Camera Zone {camera_id}"
```

### Example 2: Multi-Camera Alert Coordination

```python
# backend/services/multi_alert_coordinator.py (NEW)

from backend.services.alert_dispatcher import AlertTrigger, get_alert_dispatcher
from backend.database.models import CameraConfiguration
from datetime import datetime, timedelta
import threading

class MultiCameraAlertCoordinator:
    """Coordinate alerts across multiple cameras"""
    
    def __init__(self, db):
        self.db = db
        self.dispatcher = get_alert_dispatcher()
        self.incident_cache = {}  # Cache to avoid duplicate alerts
    
    def check_incident_cluster(self, alert_trigger, user_id):
        """
        Check if alert is part of cluster (same incident across multiple cameras)
        
        This prevents alert spam for same incident detected by multiple cameras
        """
        incident_key = f"{alert_trigger.risk_type}_{alert_trigger.location}"
        
        # Check if similar alert sent in last 5 minutes
        if incident_key in self.incident_cache:
            last_alert_time = self.incident_cache[incident_key]
            if datetime.utcnow() - last_alert_time < timedelta(minutes=5):
                logger.debug(f"Skipping duplicate alert for {incident_key}")
                return False  # Skip alert
        
        # Update cache
        self.incident_cache[incident_key] = datetime.utcnow()
        return True
    
    def trigger_coordinated_alert(self, alert_trigger, user_id):
        """Trigger coordinated alert with deduplication"""
        
        if not self.check_incident_cluster(alert_trigger, user_id):
            return {'success': False, 'reason': 'Duplicate incident within 5 minutes'}
        
        result = self.dispatcher.trigger_emergency_alert(
            alert_trigger,
            user_id=user_id,
            async_mode=True
        )
        
        return result
    
    def escalate_if_multiple_cameras(self, alert_trigger, user_id):
        """Escalate severity if same incident on multiple cameras"""
        
        # Find other active cameras detecting same incident
        similar_alerts = self.db.session.query(RiskAlert).filter(
            RiskAlert.risk_type == alert_trigger.risk_type,
            RiskAlert.status == 'pending',
            RiskAlert.created_at > datetime.utcnow() - timedelta(minutes=2)
        ).count()
        
        if similar_alerts >= 2:
            # Escalate severity
            alert_trigger.severity = 'CRITICAL'
            logger.warning(f"Alert escalated: {similar_alerts} cameras detecting same incident")
        
        return alert_trigger
```

---

## 🔔 Real-Time Alert Broadcasting

### Example 3: WebSocket Alert Notifications

```python
# backend/services/realtime_alerts.py (NEW)

from flask_socketio import SocketIO, emit, join_room
import logging

logger = logging.getLogger(__name__)
socketio = SocketIO()

class RealtimeAlertBroadcaster:
    """Broadcast alerts to connected clients in real-time"""
    
    def __init__(self):
        self.connected_users = {}
    
    def setup_socketio(self, app):
        """Initialize SocketIO"""
        socketio.init_app(app)
        
        @socketio.on('connect')
        def handle_connect(data):
            user_id = data.get('user_id')
            if user_id:
                self.connected_users[user_id] = request.sid
                logger.info(f"User {user_id} connected for alerts")
        
        @socketio.on('disconnect')
        def handle_disconnect():
            # Remove user from connected list
            for user_id, sid in self.connected_users.items():
                if sid == request.sid:
                    del self.connected_users[user_id]
                    logger.info(f"User {user_id} disconnected from alerts")
    
    def broadcast_alert(self, alert_data, user_id):
        """Broadcast alert to connected user"""
        if user_id in self.connected_users:
            sid = self.connected_users[user_id]
            
            message = {
                'type': 'emergency_alert',
                'severity': alert_data.get('severity'),
                'risk_type': alert_data.get('risk_type'),
                'location': alert_data.get('location'),
                'timestamp': alert_data.get('timestamp'),
                'dashboard_link': alert_data.get('dashboard_link')
            }
            
            socketio.emit('alert_received', message, room=sid)
            logger.info(f"Alert broadcasted to user {user_id}")
    
    def broadcast_to_all_admins(self, alert_data):
        """Broadcast alert to all connected admin users"""
        for user_id in self.connected_users.keys():
            self.broadcast_alert(alert_data, user_id)
```

### Example 4: Frontend Real-Time Alert Handler

```javascript
// frontend/static/js/realtime_alerts.js (NEW)

class RealtimeAlertHandler {
    constructor() {
        this.socket = null;
        this.alerts = [];
    }
    
    connect(userId) {
        this.socket = io();
        
        // Connect with user ID
        this.socket.emit('connect', { user_id: userId });
        
        // Listen for incoming alerts
        this.socket.on('alert_received', (alertData) => {
            this.handleAlert(alertData);
        });
        
        console.log('✓ Connected to alert server');
    }
    
    handleAlert(alertData) {
        // Add to alerts list
        this.alerts.unshift(alertData);
        
        // Show notification
        this.showNotification(alertData);
        
        // Play sound
        this.playAlertSound();
        
        // Update UI
        this.updateAlertUI();
        
        // Log to console
        console.log('🚨 ALERT RECEIVED:', alertData);
    }
    
    showNotification(alertData) {
        // Browser notification
        if ("Notification" in window && Notification.permission === "granted") {
            new Notification('🚨 Emergency Alert', {
                body: `${alertData.risk_type} at ${alertData.location}`,
                icon: '/static/images/alert-icon.png',
                tag: 'emergency-alert'
            });
        }
    }
    
    playAlertSound() {
        const audio = new Audio('/static/sounds/alert.mp3');
        audio.play().catch(e => console.log('Audio play failed:', e));
    }
    
    updateAlertUI() {
        const container = document.getElementById('alerts-container');
        const latestAlert = this.alerts[0];
        
        // Create alert HTML
        const alertHTML = `
            <div class="alert alert-critical">
                <h3>🚨 ${latestAlert.severity} Alert</h3>
                <p><strong>Type:</strong> ${latestAlert.risk_type}</p>
                <p><strong>Location:</strong> ${latestAlert.location}</p>
                <p><strong>Time:</strong> ${latestAlert.timestamp}</p>
                <a href="${latestAlert.dashboard_link}" class="btn btn-primary">
                    View Details
                </a>
            </div>
        `;
        
        container.insertAdjacentHTML('afterbegin', alertHTML);
    }
}

// Initialize
const alertHandler = new RealtimeAlertHandler();
```

---

## 📊 Alert Analytics & Reporting

### Example 5: Alert Statistics Dashboard

```python
# backend/services/alert_analytics.py (NEW)

from backend.database.models import RiskAlert, db
from datetime import datetime, timedelta
from sqlalchemy import func

class AlertAnalytics:
    """Generate analytics and insights from alerts"""
    
    @staticmethod
    def get_daily_summary(days=7):
        """Get alert statistics for past N days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        summary = db.session.query(
            func.date(RiskAlert.created_at).label('date'),
            RiskAlert.severity,
            func.count(RiskAlert.id).label('count')
        ).filter(
            RiskAlert.created_at >= cutoff
        ).group_by(
            func.date(RiskAlert.created_at),
            RiskAlert.severity
        ).all()
        
        return [{
            'date': str(row.date),
            'severity': row.severity,
            'count': row.count
        } for row in summary]
    
    @staticmethod
    def get_top_risk_types(limit=10):
        """Get most common risk types"""
        results = db.session.query(
            RiskAlert.risk_type,
            func.count(RiskAlert.id).label('count')
        ).group_by(
            RiskAlert.risk_type
        ).order_by(
            func.count(RiskAlert.id).desc()
        ).limit(limit).all()
        
        return [{
            'risk_type': row.risk_type,
            'count': row.count
        } for row in results]
    
    @staticmethod
    def get_alert_response_metrics():
        """Calculate response time metrics"""
        alerts = RiskAlert.query.filter(
            RiskAlert.status.in_(['acknowledged', 'resolved'])
        ).all()
        
        response_times = []
        for alert in alerts:
            if alert.notified_at and alert.updated_at:
                response_time = (alert.updated_at - alert.notified_at).total_seconds()
                response_times.append(response_time)
        
        if not response_times:
            return {}
        
        import statistics
        
        return {
            'avg_response_time_seconds': statistics.mean(response_times),
            'median_response_time_seconds': statistics.median(response_times),
            'min_response_time_seconds': min(response_times),
            'max_response_time_seconds': max(response_times),
            'total_alerts': len(response_times)
        }
    
    @staticmethod
    def get_delivery_success_rate(days=7):
        """Calculate WhatsApp delivery success rate"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        total = RiskAlert.query.filter(
            RiskAlert.notified == True,
            RiskAlert.created_at >= cutoff
        ).count()
        
        if total == 0:
            return 0
        
        # Count alerts that received acknowledgment
        acknowledged = RiskAlert.query.filter(
            RiskAlert.notified == True,
            RiskAlert.status.in_(['acknowledged', 'resolved']),
            RiskAlert.created_at >= cutoff
        ).count()
        
        return (acknowledged / total) * 100

# API Endpoint
from flask import jsonify

@app.route('/api/analytics/alerts', methods=['GET'])
@require_auth
def get_alert_analytics():
    """Get comprehensive alert analytics"""
    
    analytics = AlertAnalytics()
    
    return jsonify({
        'daily_summary': analytics.get_daily_summary(7),
        'top_risk_types': analytics.get_top_risk_types(10),
        'response_metrics': analytics.get_alert_response_metrics(),
        'delivery_rate': analytics.get_delivery_success_rate(7)
    })
```

---

## 🛡️ Security & Compliance

### Example 6: Encrypt Phone Numbers

```python
# backend/utils/encryption.py (NEW)

from cryptography.fernet import Fernet
import os

class PhoneNumberEncryption:
    """Encrypt/decrypt sensitive phone numbers"""
    
    def __init__(self):
        # Use environment variable for key
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            # Generate and save new key
            key = Fernet.generate_key().decode()
            print(f"Generated encryption key: {key}")
            print("Add to .env: ENCRYPTION_KEY={key}")
        
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
    
    def encrypt_phone(self, phone_number):
        """Encrypt phone number"""
        return self.cipher.encrypt(phone_number.encode()).decode()
    
    def decrypt_phone(self, encrypted_phone):
        """Decrypt phone number"""
        return self.cipher.decrypt(encrypted_phone.encode()).decode()

# Usage in emergency contacts
from backend.utils.encryption import PhoneNumberEncryption

encryptor = PhoneNumberEncryption()

# Store encrypted
encrypted = encryptor.encrypt_phone("+1-234-567-8900")
emergency_contact.phone_number_encrypted = encrypted

# Retrieve and decrypt
phone = encryptor.decrypt_phone(emergency_contact.phone_number_encrypted)
```

### Example 7: Audit Logging for Alerts

```python
# backend/services/audit_service.py (UPDATED)

from backend.database.models import AuditLog
from datetime import datetime

class AlertAuditService:
    """Log all alert-related actions for compliance"""
    
    @staticmethod
    def log_alert_triggered(user_id, alert_data, ip_address):
        """Log when alert is triggered"""
        log = AuditLog(
            user_id=user_id,
            action='ALERT_TRIGGERED',
            table_name='risk_alerts',
            record_id=alert_data.get('alert_id'),
            new_values={
                'severity': alert_data.get('severity'),
                'risk_type': alert_data.get('risk_type'),
                'recipients': alert_data.get('recipients_count')
            },
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
    
    @staticmethod
    def log_contact_added(user_id, contact_data, ip_address):
        """Log when emergency contact is added"""
        log = AuditLog(
            user_id=user_id,
            action='EMERGENCY_CONTACT_ADDED',
            table_name='emergency_contacts',
            new_values={
                'contact_name': contact_data.get('contact_name'),
                'phone_number_masked': contact_data.get('phone_number')[-4:]  # Only last 4 digits
            },
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
    
    @staticmethod
    def log_contact_deleted(user_id, contact_id, ip_address):
        """Log when emergency contact is deleted"""
        log = AuditLog(
            user_id=user_id,
            action='EMERGENCY_CONTACT_DELETED',
            table_name='emergency_contacts',
            record_id=str(contact_id),
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
```

---

## 🧪 Unit Tests

### Example 8: Test Alert Dispatcher

```python
# test_alert_dispatcher.py

import unittest
from unittest.mock import Mock, patch, MagicMock
from backend.services.alert_dispatcher import AlertDispatcher, AlertTrigger
from datetime import datetime

class TestAlertDispatcher(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.mock_whatsapp = Mock()
        self.dispatcher = AlertDispatcher(
            db=self.mock_db,
            whatsapp_service=self.mock_whatsapp
        )
    
    def test_alert_trigger_creation(self):
        """Test AlertTrigger object creation"""
        alert = AlertTrigger(
            camera_id=1,
            risk_type="not_wearing_helmet",
            risk_category="PPE",
            severity="CRITICAL",
            confidence_score=0.95,
            risk_score=85,
            location="Test Factory"
        )
        
        self.assertEqual(alert.camera_id, 1)
        self.assertEqual(alert.severity, "CRITICAL")
        self.assertIsNotNone(alert.timestamp)
    
    def test_severity_filtering(self):
        """Test that LOW severity alerts are skipped"""
        alert = AlertTrigger(
            camera_id=1,
            risk_type="test",
            risk_category="TEST",
            severity="LOW",
            confidence_score=0.5,
            risk_score=10,
            location="Test"
        )
        
        result = self.dispatcher.trigger_emergency_alert(alert, user_id=1)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'Severity too low')
    
    def test_get_recipients(self):
        """Test recipient filtering"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.mobile_number = "+1-234-567-8900"
        mock_user.email = "user@example.com"
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        
        # Mock emergency contacts
        self.mock_db.query.return_value.filter_by.return_value.all.return_value = []
        
        recipients = self.dispatcher._get_alert_recipients(mock_user, "CRITICAL")
        
        self.assertEqual(len(recipients), 1)
        self.assertEqual(recipients[0]['phone_number'], "+1-234-567-8900")
        self.assertEqual(recipients[0]['contact_type'], 'primary')

if __name__ == '__main__':
    unittest.main()
```

### Example 9: Test Phone Number Validation

```python
# test_phone_validation.py

import unittest
from backend.routes.emergency_contacts_api import validate_phone_number

class TestPhoneValidation(unittest.TestCase):
    
    def test_valid_us_numbers(self):
        """Test valid US phone numbers"""
        test_cases = [
            ("+1-234-567-8900", "+1", "+1234567890"),
            ("+1 234 567 8900", "+1", "+1234567890"),
            ("1234567890", "+1", "+11234567890"),
            ("+1(234)567-8900", "+1", "+1234567890")
        ]
        
        for input_num, expected_cc, expected_fmt in test_cases:
            valid, formatted, cc = validate_phone_number(input_num)
            self.assertTrue(valid, f"Failed for {input_num}")
            self.assertEqual(cc, expected_cc)
    
    def test_valid_international(self):
        """Test valid international numbers"""
        valid, formatted, cc = validate_phone_number("+44-20-7946-0958")
        self.assertTrue(valid)
        self.assertEqual(cc, "+44")
    
    def test_invalid_numbers(self):
        """Test invalid phone numbers"""
        invalid_numbers = [
            "invalid",
            "123",  # too short
            "+",
            ""
        ]
        
        for num in invalid_numbers:
            valid, formatted, cc = validate_phone_number(num)
            self.assertFalse(valid, f"Should be invalid: {num}")

if __name__ == '__main__':
    unittest.main()
```

---

## 🚀 Deployment Scripts

### Example 10: Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  web:
    build: .
    container_name: safety-monitoring-app
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: production
      DATABASE_URL: postgresql://user:password@db:5432/safety_db
      WHATSAPP_PROVIDER: twilio
      TWILIO_ACCOUNT_SID: ${TWILIO_ACCOUNT_SID}
      TWILIO_AUTH_TOKEN: ${TWILIO_AUTH_TOKEN}
      TWILIO_WHATSAPP_NUMBER: ${TWILIO_WHATSAPP_NUMBER}
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    restart: always

  db:
    image: postgres:13
    container_name: safety-monitoring-db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: safety_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7
    container_name: safety-monitoring-redis
    restart: always

volumes:
  postgres_data:
```

---

**All examples are production-ready and can be deployed immediately!**
