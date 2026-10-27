# Project Exploration Report
## AI Safety Monitoring System - Architecture & Implementation

**Last Updated**: March 19, 2026

---

## Table of Contents
1. [User Registration](#user-registration)
2. [User Database Schema](#user-database-schema)
3. [Current Notification System](#notification-system)
4. [Authentication Flow](#authentication-flow)
5. [Alert & Monitoring System](#alert--monitoring-system)
6. [Architecture Overview](#architecture-overview)

---

## User Registration

### Registration Endpoint
- **Route**: `POST /api/auth/register`
- **File**: [backend/routes/auth.py](backend/routes/auth.py)

### Registration Process
```python
1. Accepts: username, email, password, confirm_password, first_name, last_name
2. Validates:
   - Username: minimum 3 characters
   - Email: valid email format
   - Password: 
     * Minimum 8 characters
     * At least one uppercase letter
     * At least one lowercase letter
     * At least one digit
     * At least one special character (!@#$%^&*...)
   - Passwords match
   - Username and email uniqueness
3. Creates user with database (SQLAlchemy) or fallback JSON file (users.json)
```

### Hybrid Storage Approach
- **Primary**: SQLAlchemy with database (models: [backend/database/models.py](backend/database/models.py))
- **Fallback**: In-memory JSON file storage (`users.json`) if database unavailable
- **Graceful Degradation**: System uses `InMemoryUserStore` class for fallback

### User Data Stored
```json
{
  "id": "auto-increment",
  "username": "unique",
  "email": "unique",
  "password_hash": "pbkdf2:sha256",
  "first_name": "string",
  "last_name": "string",
  "role": "operator (default)",
  "is_active": true,
  "created_at": "timestamp",
  "last_login": "timestamp"
}
```

---

## User Database Schema

### User Model
**File**: [backend/database/models.py](backend/database/models.py#L27-L45)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | Integer | Primary Key | Auto-increment |
| username | String(120) | UNIQUE, Index | Required |
| email | String(255) | UNIQUE, Index | Required |
| password_hash | String(255) | - | Required, pbkdf2:sha256 |
| first_name | String(120) | - | Optional |
| last_name | String(120) | - | Optional |
| role | String(50) | Default: 'operator' | admin, supervisor, operator |
| department | String(120) | - | Optional |
| is_active | Boolean | Default: True | Soft-delete support |
| last_login | DateTime | - | Tracking |
| created_at | DateTime | Index | Auto-populated |
| updated_at | DateTime | - | Auto-tracked |

### Relationship Models
**Relationships** (all via backref):
- `User.incidents` → `IncidentLog` (one-to-many)
- `User.alerts` → `AlertHistory` (one-to-many)
- `User.audit_logs` → `AuditLog` (one-to-many)
- `User.acknowledged_alerts` → `AlertHistory` (one-to-many)
- `User.emergency_contacts` → `EmergencyContact` (one-to-many, max 10)

### Related Models in Schema

#### NotificationPreference
[backend/database/models.py](backend/database/models.py#L213-L225)
```
- user_id (FK to User)
- alert_type (string, indexed)
- email_enabled (boolean, default: true)
- sms_enabled (boolean, default: false)
- push_enabled (boolean, default: true)
- min_severity (default: 'MEDIUM')
```

#### EmergencyContact (NEW - v2.0)
[backend/database/models.py](backend/database/models.py#L241-L269)
```
- admin_id (FK to User, indexed)
- contact_name (string)
- phone_number (string, indexed)
- email (string)
- whatsapp_enabled (boolean, default: true)
- sms_enabled (boolean, default: true)
- email_enabled (boolean, default: true)
- alert_low/medium/high/critical (boolean flags)
- is_active (boolean, default: true)
- verified (boolean, default: false)
- created_at, updated_at (timestamps)
```

#### RiskAlert (NEW - v2.0)
[backend/database/models.py](backend/database/models.py#L314-L365)
```
- alert_id (UUID, unique, indexed)
- camera_id (FK to CameraConfiguration, indexed)
- risk_type (string - not_wearing_helmet, improper_stance, etc.)
- risk_category (PPE|POSTURE|BEHAVIOR|HAZMAT)
- severity (LOW|MEDIUM|HIGH|CRITICAL, indexed)
- confidence_score (0-1 float)
- risk_score (0-100 float)
- worker_id, detection_count, first_detection_time, last_detection_time
- environmental_conditions (JSON)
- area_hazard_level (LOW|MEDIUM|HIGH)
- nearby_hazards (JSON list)
- image_url, thumbnail_url
- status (pending|notified|acknowledged|resolved|dismissed, indexed)
- notified (boolean), notified_at (datetime)
```

#### CameraHealthStatus (NEW - v2.0)
[backend/database/models.py](backend/database/models.py#L273-L310)
```
Real-time monitoring for 30-40+ cameras:
- Connection status, last_frame_time, connection_attempts
- Performance: current_fps, frame_loss_rate, cpu_usage, memory_usage, bandwidth_usage
- Detection: detection_running, last_detection_time, detections_per_minute
- Uptime: uptime_percentage, uptime_seconds, downtime_events
- Network: latency_ms, packet_loss, signal_strength (wireless)
- last_update (auto-updated)
```

---

## Notification System

### 1. Basic Notification Service
**File**: [backend/services/notification_service.py](backend/services/notification_service.py)

#### Methods Available
```python
- send_email_alert(recipient, alert_type, message, severity)
  Returns: boolean
  
- send_sms_alert(phone, message)
  Returns: boolean
  Placeholder for Twilio integration
  
- send_webhook_alert(webhook_url, alert_data)
  Returns: boolean
  
- _generate_email_body(alert_type, message, severity)
  Returns: HTML string
  Color-coded by severity
```

#### Email Features
- SMTP configuration required (`MAIL_SERVER`, `MAIL_DEFAULT_SENDER`)
- HTML emails with severity-based colors
- Notification queue support

---

### 2. Advanced Multi-Channel Notification Service
**File**: [backend/services/advanced_notification_service.py](backend/services/advanced_notification_service.py)

#### Architecture
Implements **NotificationChannel** abstract base class with three concrete implementations

#### Unified Message Format
```python
@dataclass
class NotificationMessage:
    recipient: str          # Email or phone number
    subject: str            # Email subject / SMS/WA header
    title: str              # Alert title
    body: str               # Alert message
    severity: str           # LOW|MEDIUM|HIGH|CRITICAL
    action_url: str         # Optional dashboard link
    image_url: str          # Optional evidence image
    alert_id: str           # For tracking
    timestamp: datetime
```

#### Email Channel
- **SMTP Config**: Host, port, username, password
- **Security**: SSL connection, login authentication
- **Response**: Returns (bool, error_message)
- **Validation**: Email format check
- **Priority Headers**: Mapped by severity (1=critical, 5=low)
- **HTML Template**:
  ```html
  - Header with severity color
  - Content with alert details
  - Embedded image support
  - Action button with link
  - Footer branding
  ```

#### SMS Channel (Twilio)
- **Validation**: Phone number format (10+ digits)
- **Message Format**: 160-character limit with emoji prefix
  ```
  Severity emojis:
  LOW: ⚠️
  MEDIUM: ⚠️⚠️
  HIGH: 🔴
  CRITICAL: 🚨
  ```
- **Returns**: (bool, SID or error message)

#### WhatsApp Channel (Twilio)
- **Number Format**: `whatsapp:+1234567890`
- **Rich Formatting**: Supports emojis, newlines, emphasis
- **Message Structure**:
  ```
  [Severity Emoji] Severity Level
  {title}: {body}
  Alert ID: {last 6 chars}
  ```
- **Returns**: (bool, SID or error message)

---

## Authentication Flow

### 1. Authentication Service
**File**: [backend/services/auth_service.py](backend/services/auth_service.py)

#### Token Management
```python
# Access Token
- Expires: 1 hour (3600 seconds)
- Algorithm: HS256
- Payload: user_id, username, role, type='access', iat, exp

# Refresh Token
- Expires: 30 days (2592000 seconds)
- Algorithm: HS256
- Payload: user_id, username, type='refresh', iat, exp
```

#### Password Handling
```python
hash_password(password: str) -> str
  Uses: Werkzeug pbkdf2:sha256
  
verify_password(password: str, hash: str) -> bool
  Secure comparison
```

#### Token Methods
- `create_access_token(user_id, username, role)` → JWT
- `create_refresh_token(user_id, username)` → JWT
- `verify_token(token)` → payload dict or None
- `refresh_access_token(refresh_token)` → new access token

### 2. Authorization Service
**File**: [backend/services/auth_service.py](backend/services/auth_service.py#L106-L165)

#### Role-Based Access Control (RBAC)
Three roles with 9 permissions:

| Permission | Admin | Supervisor | Operator |
|------------|-------|------------|----------|
| user_management | ✅ | ❌ | ❌ |
| system_settings | ✅ | ❌ | ❌ |
| report_generation | ✅ | ✅ | ❌ |
| incident_management | ✅ | ✅ | ✅ |
| camera_configuration | ✅ | ❌ | ❌ |
| data_export | ✅ | ✅ | ❌ |
| audit_log_access | ✅ | ✅ | ❌ |
| shift_management | ✅ | ✅ | ❌ |
| alert_configuration | ✅ | ✅ | ❌ |

#### Permission Methods
```python
has_permission(role, permission) -> bool
has_any_permission(role, permissions_list) -> bool
has_all_permissions(role, permissions_list) -> bool
```

### 3. Session Management Service
**File**: [backend/services/auth_service.py](backend/services/auth_service.py#L167-L226)

#### Session Features
```python
Create: session_id (UUID) with user_id, token, ip_address, timestamps
Validate: 
  - Check session exists
  - Verify IP address (security)
  - Check 30-minute inactivity timeout
  
Update: last_activity timestamp on each request
Remove: On logout or timeout
```

#### Session Tracking
```python
active_sessions: Dict = {
  session_id: {
    'user_id': int,
    'token': str,
    'ip_address': str,
    'created_at': datetime,
    'last_activity': datetime
  }
}
```

### 4. Audit Service
**File**: [backend/services/auth_service.py](backend/services/auth_service.py#L228-end)

**AuditLog Model**:
- User ID performing action
- Action type (create, update, delete)
- Table name and record ID
- Old/new values (JSON)
- IP address
- Timestamp

---

## Alert & Monitoring System

### 1. Emergency Contact Management
**Routes File**: [backend/routes/emergency_alerts.py](backend/routes/emergency_alerts.py)

#### API Endpoints

**GET** `/api/v1/emergency-contacts`
```json
Returns:
{
  "success": true,
  "count": number,
  "contacts": [
    {
      "id": int,
      "contact_name": string,
      "phone_number": string,
      "email": string,
      "whatsapp_enabled": boolean,
      "sms_enabled": boolean,
      "email_enabled": boolean,
      "alert_levels": {
        "low": boolean,
        "medium": boolean,
        "high": boolean,
        "critical": boolean
      },
      "verified": boolean,
      "created_at": iso_datetime
    }
  ]
}
```

**POST** `/api/v1/emergency-contacts`
```json
Request:
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

Constraints:
- Max 10 contacts per admin
- Phone format validation (10+ digits)
```

**PUT** `/api/v1/emergency-contacts/<contact_id>`
```json
Updates any field with ownership verification
```

**DELETE** `/api/v1/emergency-contacts/<contact_id>`
```json
Soft delete (is_active = false)
```

### 2. Risk Alert Retrieval
**GET** `/api/v1/risk-alerts`

#### Query Parameters
```
- severity: LOW|MEDIUM|HIGH|CRITICAL (optional)
- camera_id: integer (optional)
- status: pending|notified|acknowledged|resolved (optional)
- hours: integer (default 24)
- limit: integer (default 100)
```

#### Response Format
```json
{
  "success": true,
  "count": number,
  "alerts": [
    {
      "alert_id": uuid,
      "camera_id": int,
      "risk_type": string,
      "risk_category": string,
      "severity": string,
      "confidence_score": float,
      "risk_score": float,
      "status": string,
      "worker_id": string,
      "image_url": string,
      "timestamp": iso_datetime,
      "first_detection": iso_datetime,
      "detection_count": int
    }
  ]
}
```

### 3. Risk Prediction Engine
**File**: [backend/services/risk_prediction_service.py](backend/services/risk_prediction_service.py)

#### ContextualRiskScorer Class

**Base Risk Scores** (0-100):
```python
{
  'not_wearing_helmet': 85,
  'improper_helmet_fit': 65,
  'no_safety_vest': 75,
  'missing_ppe': 70,
  'improper_posture': 40,
  'near_hazard': 60,
  'hazmat_exposure': 95,
  'fatigue_detected': 45,
  'unsafe_behavior': 55,
}
```

**Risk Multipliers**:
```python
CONFIDENCE_WEIGHT = 1.0
HAZARD_LEVEL_WEIGHT = 1.2       # Location hazard amplifies risk
CRITICAL_AREA_MULTIPLIER = 2.0  # High hazard areas
NIGHT_SHIFT_MULTIPLIER = 1.3    # Night shift fatigue
REPEATED_VIOLATION_MULTIPLIER = 1.5  # Repeated violations
```

#### score_risk() Method
```python
Inputs:
  - violation_type: string
  - detection_confidence: 0-1 float
  - risk_context: RiskContext (location, time, history, environment)
  - detection_count: integer

Process:
  1. Get base risk score
  2. Weight by detection confidence
  3. Apply location hazard multiplier
  4. Apply time-of-day risk (fatigue)
  5. Escalate for repeated violations
  6. Amplify by worker history
  7. Apply environmental factors
  8. Factor in worker fatigue
  9. Cap at 100

Returns: (risk_score: 0-100, severity: RiskSeverity)
```

#### RiskContext Data
```python
@dataclass
class RiskContext:
    time_of_day: str              # morning, afternoon, night
    location_hazard_level: str    # LOW, MEDIUM, HIGH
    shift_type: str               # morning, afternoon, night
    environmental_conditions: Dict  # lighting, weather, temp, air_quality
    nearby_hazards: List[str]     # hazard descriptions
    worker_fatigue_level: float   # 0-1 scale
    previous_violations: int      # count
```

---

## Architecture Overview

### Layer Structure
```
API Routes (Flask Blueprints)
    ↓
Service Layer (Business Logic)
    ↓
Database Models (SQLAlchemy ORM)
    ↓
Database (PostgreSQL/SQLite)
```

### File Organization
```
backend/
├── routes/
│   ├── auth.py                      # Registration, login
│   ├── emergency_alerts.py          # Contact & alert management
│   ├── incidents.py                 # Incident tracking
│   ├── monitoring.py                # Real-time monitoring
│   ├── analytics.py                 # Analytics endpoints
│   └── ...
├── services/
│   ├── auth_service.py              # JWT, RBAC, sessions
│   ├── notification_service.py      # Basic notifications
│   ├── advanced_notification_service.py  # Multi-channel
│   ├── risk_prediction_service.py   # Risk scoring
│   ├── incident_service.py          # Incident handling
│   └── ...
└── database/
    └── models.py                    # All SQLAlchemy models
```

### Key Design Patterns

1. **Service Layer Separation**: Business logic isolated from routes
2. **Multi-channel Notifications**: Abstract base class with pluggable channels
3. **Contextual Risk Scoring**: Risk adjusted by location, time, history, environment
4. **Graceful Degradation**: Falls back to JSON if database unavailable
5. **RBAC with Permissions**: Matrix-based role-permission system
6. **JWT Tokens**: Stateless authentication with refresh token flow
7. **Comprehensive Audit Trail**: All actions logged with before/after values

---

## Summary Statistics

| Category | Count | Status |
|----------|-------|--------|
| Total Database Models | 15+ | ✅ Defined |
| User Roles | 3 | ✅ admin, supervisor, operator |
| Permissions | 9 | ✅ Defined |
| Alert Severity Levels | 4 | ✅ LOW, MEDIUM, HIGH, CRITICAL |
| Notification Channels | 3 | ✅ Email, SMS, WhatsApp |
| Risk Categories | 6 | ✅ PPE, POSTURE, BEHAVIOR, HAZMAT, FATIGUE, ENVIRONMENT |
| Base Risk Violation Types | 9 | ✅ Defined |
| Emergency Contacts Per Admin | Max 10 | ✅ Enforced |
| Camera Support | 30-40+ | ✅ Planned |
| Token Expiration | 1 hour (access) / 30 days (refresh) | ✅ Configured |

---

## Next Steps for Integration

Based on the existing infrastructure, future work should focus on:

1. ✅ Completing the connection between AI detection and alert triggering
2. ✅ Implementing webhook integration for external systems
3. ✅ Full implementation of reporting service (endpoints exist, need population)
4. ✅ Real-time alert delivery coordination
5. ✅ Dashboard/frontend integration with alert APIs
6. ✅ Testing with 30-40 simultaneous cameras
