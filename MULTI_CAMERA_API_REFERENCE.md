"""
MULTI-CAMERA & ADVANCED ALERTS API REFERENCE
Complete endpoint documentation for new v1.1 features
"""

# Base URL: http://localhost:5000/api/v1

# ============================================================================
# EMERGENCY CONTACT MANAGEMENT
# ============================================================================

"""
1. GET /emergency-contacts
   Get all emergency contacts (max 10 per admin)
   
   Authorization: Bearer <token>
   
   Response:
   {
       "success": true,
       "count": 5,
       "contacts": [{contact_data}]
   }


2. POST /emergency-contacts
   Register new emergency contact (max 10 per admin)
   
   Body:
   {
       "contact_name": "John Manager",
       "phone_number": "+1234567890",
       "email": "john@example.com",
       "whatsapp_enabled": true,
       "sms_enabled": true,
       "email_enabled": true,
       "alert_low": false,
       "alert_medium": true,
       "alert_high": true,
       "alert_critical": true
   }
   
   Response: 201 Created
   {
       "success": true,
       "message": "Emergency contact registered successfully",
       "contact_id": 1,
       "contact_name": "John Manager"
   }


3. PUT /emergency-contacts/{contact_id}
   Update emergency contact
   
   Body: Same as POST (fields optional)
   Response: 200 OK
   

4. DELETE /emergency-contacts/{contact_id}
   Delete (deactivate) emergency contact
   
   Response: 200 OK
"""

# ============================================================================
# RISK ALERT VIEWING & MANAGEMENT
# ============================================================================

"""
5. GET /risk-alerts
   Get risk alerts with filtering
   
   Query Parameters:
       ?severity=CRITICAL&hours=24&limit=100
       ?camera_id=5&status=pending
   
   Response:
   {
       "success": true,
       "count": 3,
       "alerts": [
           {
               "alert_id": "ALERT-20250318-001",
               "camera_id": 5,
               "risk_type": "not_wearing_helmet",
               "severity": "CRITICAL",
               "confidence_score": 0.95,
               "risk_score": 85.5,
               "status": "notified",
               "worker_id": "W123",
               "timestamp": "2025-03-18T10:30:00Z",
               "detection_count": 3
           }
       ]
   }


6. GET /risk-alerts/{alert_id}
   Get detailed alert information
   
   Response:
   {
       "success": true,
       "alert": {full_alert_details}
   }


7. POST /risk-alerts/{alert_id}/acknowledge
   Mark alert as acknowledged
   
   Response: 200 OK


8. POST /risk-alerts/{alert_id}/resolve
   Mark alert as resolved
   
   Body:
   {
       "action": "Worker provided with proper PPE"
   }
   
   Response: 200 OK


9. GET /alert-statistics
   Get aggregated alert statistics
   
   Query: ?hours=24
   
   Response:
   {
       "success": true,
       "statistics": {
           "total_alerts": 42,
           "by_severity": {...},
           "by_status": {...},
           "by_type": {...},
           "by_camera": {...},
           "avg_response_time_seconds": 720
       }
   }
"""

# ============================================================================
# TESTING
# ============================================================================

"""
10. POST /test-alert
    Send test emergency alert to all contacts
    
    Body:
    {
        "severity": "CRITICAL",
        "include_all_contacts": true
    }
    
    Response:
    {
        "success": true,
        "message": "Test alert sent to 5 contacts",
        "result": {
            "total_contacts": 5,
            "successful": 5,
            "failed": 0,
            "notifications": {...}
        }
    }
"""

# ============================================================================
# MULTI-CAMERA MANAGEMENT
# ============================================================================

"""
11. GET /cameras
    Get all cameras with health status
    
    Query: ?status=connected
    
    Response:
    {
        "success": true,
        "count": 8,
        "cameras": [
            {
                "camera_id": 1,
                "camera_name": "Camera 1 - Assembly Floor",
                "location": "Assembly Line A",
                "stream_url": "rtsp://...",
                "hazard_level": "HIGH",
                "health": {
                    "status": "connected",
                    "fps": 29.8,
                    "cpu_usage": 35.2,
                    "memory_usage": 42.1,
                    "uptime_percentage": 99.5
                }
            }
        ]
    }


12. POST /cameras
    Register new camera (max 40)
    
    Body:
    {
        "camera_name": "Camera 1 - Assembly Floor",
        "location": "Assembly Line A",
        "stream_url": "rtsp://192.168.1.100:554/stream",
        "hazard_level": "HIGH",
        "detection_enabled": true
    }
    
    Response: 201 Created
    {
        "success": true,
        "camera_id": 1,
        "camera_name": "Camera 1 - Assembly Floor"
    }


13. GET /cameras/{camera_id}
    Get camera details
    
    Response: 200 OK


14. PUT /cameras/{camera_id}
    Update camera configuration
    
    Body: (all fields optional)
    {
        "camera_name": "New name",
        "hazard_level": "CRITICAL",
        "detection_enabled": false
    }
    
    Response: 200 OK


15. DELETE /cameras/{camera_id}
    POST /cameras/{camera_id}/deactivate
    Stop monitoring a camera
    
    Response: 200 OK
"""

# ============================================================================
# MULTI-CAMERA COORDINATOR STATUS
# ============================================================================

"""
16. GET /coordinator/status
    Get overall system health (40+ cameras)
    
    Response:
    {
        "success": true,
        "coordinator_status": {
            "active_cameras": 8,
            "max_cameras": 40,
            "total_frames_processed": 245780,
            "total_detections": 3421,
            "system_cpu_usage": 45.2,
            "system_memory_usage": 58.7,
            "coordinator_health": "healthy"
        }
    }


17. GET /coordinator/statistics
    Get aggregated statistics across all cameras
    
    Query: ?hours=24
    
    Response:
    {
        "success": true,
        "coordinator_statistics": {
            "total_cameras": 8,
            "active_cameras": 8,
            "total_frames": 245780,
            "total_detections": 3421,
            "total_alerts": 127,
            "alerts_by_severity": {...},
            "camera_stats": {...}
        }
    }
"""

# ============================================================================
# CAMERA HEALTH & MONITORING SESSION
# ============================================================================

"""
18. GET /cameras/{camera_id}/health
    Get detailed camera health metrics and trends
    
    Response:
    {
        "success": true,
        "camera_id": 5,
        "latest_health": {
            "timestamp": "2025-03-18T10:45:00Z",
            "is_connected": true,
            "current_fps": 29.5,
            "cpu_usage": 38.2,
            "memory_usage": 45.7,
            "latency_ms": 52,
            "uptime_percentage": 98.9
        },
        "health_history": [...]
    }


19. POST /monitoring/start
    Start monitoring all active cameras
    
    Response: 201 Created
    {
        "success": true,
        "session_id": "SESSION-20250318-001",
        "cameras_monitoring": 8
    }


20. POST /monitoring/stop
    Stop all monitoring
    
    Response: 200 OK
    

21. GET /monitoring/session/{session_id}
    Get monitoring session details
    
    Response: 200 OK
"""

# ============================================================================
# FRAME PROCESSING (Edge/External)
# ============================================================================

"""
22. POST /cameras/{camera_id}/process-frame
    Process frame from external AI/edge device
    
    Body:
    {
        "frame_data": "base64_encoded_image",
        "detections": [
            {
                "class": "person",
                "confidence": 0.95,
                "bbox": [100, 200, 300, 400]
            }
        ]
    }
    
    Response: 200 OK
    {
        "success": true,
        "result": {
            "detections_processed": 1,
            "alerts_generated": 0,
            "risk_assessment": {...}
        }
    }
"""

# ============================================================================
# SEVERITY LEVELS & NOTIFICATION ROUTING
# ============================================================================

"""
SEVERITY LEVELS (Auto-Calculated by Risk Engine):
  - LOW (0-25): Low risk, email only
  - MEDIUM (25-50): Medium risk, email + SMS
  - HIGH (50-75): High risk, email + SMS + WhatsApp
  - CRITICAL (75-100): Critical risk, all channels immediately

NOTIFICATION CHANNELS:
  - EMAIL: HTML formatted with severity colors
  - SMS: Twilio integration (≤160 characters)
  - WHATSAPP: Rich markdown formatting via Twilio

CONTACT ALERT PREFERENCES:
  Each contact can enable/disable per severity level + per channel
  Max 10 emergency contacts per admin
  Automatic filtering ensures right message to right channel
"""

# ============================================================================
# RISK SCORING ALGORITHM
# ============================================================================

"""
MULTI-FACTOR RISK CALCULATION:

Base Score (85-95 for PPE violations):
  not_wearing_helmet: 85
  improper_helmet_fit: 65
  no_safety_vest: 75
  hazmat_exposure: 95
  (and 10+ other violation types)

Applied Multipliers:
  × detection_confidence (0-1)
  × hazard_level (LOW:1.0, MEDIUM:1.5, HIGH:2.0, CRITICAL:3.0)
  × night_shift_multiplier (1.3 if night)
  × repeated_violation (1.5 if 3+ violations in 8 hours)
  × worker_fatigue (1.2 if detected)
  
Environmental Factors:
  × poor_lighting (1.2)
  × high_temperature (1.15)
  × air_quality (1.2 if poor)

Example:
  Base: not_wearing_helmet = 85
  85 × 0.95 (confidence) × 2.0 (high hazard) × 1.3 (night) = 210
  Capped to 100 = CRITICAL severity
"""

# ============================================================================
# CONFIGURATION FOR NOTIFICATION CHANNELS
# ============================================================================

"""
REQUIRED ENVIRONMENT VARIABLES:

EMAIL (SMTP):
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USE_TLS=true
  SMTP_USERNAME=your-email@gmail.com
  SMTP_PASSWORD=app-specific-password
  SENDER_EMAIL=safety-alerts@company.com
  SENDER_NAME=AI Safety Monitoring

TWILIO (SMS & WhatsApp):
  TWILIO_ACCOUNT_SID=ACxxxxxx...
  TWILIO_AUTH_TOKEN=your_token_here
  TWILIO_SMS_FROM=+1234567890
  TWILIO_WHATSAPP_FROM=whatsapp:+1234567890
  SMS_ENABLED=true
  WHATSAPP_ENABLED=true

Configuration file: backend/config/multinotify_config.py
"""

# ============================================================================
# ERROR CODES
# ============================================================================

"""
SUCCESS:
  200 OK: Request successful
  201 Created: Resource created
  
CLIENT ERROR:
  400 Bad Request: Invalid request body or parameters
  401 Unauthorized: Missing/invalid JWT token
  403 Forbidden: Insufficient permissions
  404 Not Found: Resource not found
  429 Too Many Requests: Rate limit exceeded
  
SERVER ERROR:
  500 Internal Server Error: Server-side error
  503 Service Unavailable: Service temporarily down
"""

# ============================================================================
# QUICK START CURL EXAMPLES
# ============================================================================

"""
# Get all emergency contacts
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  http://localhost:5000/api/v1/emergency-contacts

# Register emergency contact (max 10)
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "contact_name": "John Manager",
    "phone_number": "+1234567890",
    "email": "john@example.com",
    "alert_critical": true
  }' \\
  http://localhost:5000/api/v1/emergency-contacts

# Get critical alerts from last 24 hours
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  "http://localhost:5000/api/v1/risk-alerts?severity=CRITICAL&hours=24"

# Get all cameras with health status
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  http://localhost:5000/api/v1/cameras

# Register a new camera (max 40)
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "camera_name": "Assembly Floor Camera",
    "location": "Line A",
    "stream_url": "rtsp://192.168.1.100:554/stream",
    "hazard_level": "HIGH"
  }' \\
  http://localhost:5000/api/v1/cameras

# Get coordinator status (all 40 cameras)
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  http://localhost:5000/api/v1/coordinator/status

# Send test alert to all contacts
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"severity": "CRITICAL"}' \\
  http://localhost:5000/api/v1/test-alert
"""
