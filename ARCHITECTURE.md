# AI Smart Safety Monitoring System - Enterprise Edition v2.0

## 📋 Overview

This is an enterprise-grade AI-powered real-time safety monitoring system designed for complex industrial and workplace environments. The application features modular architecture supporting:

- **Multi-camera support** (up to 16 concurrent cameras)
- **Advanced AI detection** with ensemble models and multi-model support
- **Enterprise authentication** with JWT tokens and role-based access control
- **Comprehensive incident management** with escalation and resolution workflows
- **Real-time notifications** via email, SMS, and webhooks
- **Advanced analytics** with compliance metrics and trend analysis
- **Full audit logging** for compliance and regulatory requirements

## 🏗️ Architecture

The application is organized into three main modules:

### 1. **AI Module** (`/ai`)
Advanced detection and computer vision capabilities:
- **`detection/advanced_detector.py`** - Multi-model detection engine
  - Ensemble model support (Cascade, SSD, YOLO, Ensemble)
  - Multi-frame detection aggregation
  - 5 helmet color detection (yellow, orange, white, red, blue)
  - Morphological operations and contour analysis
  - Performance metrics tracking

- **`detection/multi_camera_manager.py`** - Concurrent camera management
  - Support for up to 16 cameras
  - Multi-threaded frame capture
  - Frame buffering and caching
  - Camera status monitoring

- **`models/model_manager.py`** - Model versioning and switching
  - Model registration and versioning
  - Active model management
  - Accuracy tracking
  - Model performance history

### 2. **Backend Module** (`/backend`)
Business logic, services, and data management:

#### Services (`/backend/services`)
- **`auth_service.py`** - Authentication and authorization
  - JWT token generation and validation
  - Password hashing and verification
  - Role-based access control (RBAC)
  - Session management
  - Audit logging

- **`incident_service.py`** - Incident management
  - Incident creation and tracking
  - Status workflow management
  - Severity escalation
  - Incident statistics and analytics

- **`notification_service.py`** - Multi-channel notifications
  - Email alerts with HTML templates
  - SMS notifications
  - Webhook integration
  - Report generation
  - Advanced analytics

#### Configuration (`/backend/config`)
- **`settings.py`** - Environment-based configuration
  - Development, Production, Testing profiles
  - Database pooling and connection management
  - JWT configuration
  - Alert channel configuration
  - Data retention policies

#### Database (`/backend/database`)
- **`models.py`** - SQLAlchemy ORM models
  - User management with roles
  - Incident tracking with full lifecycle
  - Alert history and notifications
  - Worker profiles
  - Camera configuration
  - Shift management
  - Audit logs
  - System configuration

#### Routes (`/backend/routes`)
REST API endpoints organized by domain:
- **`auth.py`** - Authentication endpoints (login, logout, token refresh)
- **`incidents.py`** - Incident management endpoints
- **`analytics.py`** - Analytics and reporting endpoints

#### Utilities (`/backend/utils`)
- **`helpers.py`** - Common utilities
  - Response formatting
  - Validation helpers
  - Pagination utilities
  - DateTime helpers
  - Security helpers
  - Caching utilities
  - Exception handling

### 3. **Frontend Module** (`/frontend`)
Web-based user interface:
- **`templates/`** - HTML templates
- **`static/css/`** - Stylesheets
- **`static/js/`** - Client-side JavaScript

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- OpenCV 4.13.0+
- Flask 2.3.2+
- Virtual environment (recommended)

### Installation

1. **Clone/Create workspace**
```bash
cd d:\major project
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Create .env file
echo FLASK_ENV=development > .env
echo SECRET_KEY=your-secret-key-here >> .env
echo MAIL_SERVER=smtp.gmail.com >> .env
# Add other configuration variables
```

5. **Run the application**
```bash
python main.py
```

The application will start on `http://localhost:5000`

## 📡 API Endpoints

### Authentication
```
POST   /api/auth/login              - User login
POST   /api/auth/logout             - User logout
POST   /api/auth/refresh            - Refresh access token
GET    /api/auth/validate           - Validate token
GET    /api/auth/me                 - Get current user
POST   /api/auth/change-password    - Change password
GET    /api/auth/sessions           - Get user sessions
```

### Incidents
```
GET    /api/incidents               - Get open incidents
GET    /api/incidents/<id>          - Get incident details
POST   /api/incidents               - Create new incident
PUT    /api/incidents/<id>/acknowledge  - Acknowledge incident
PUT    /api/incidents/<id>/resolve    - Resolve incident
PUT    /api/incidents/<id>/escalate   - Escalate incident
GET    /api/incidents/camera/<id>  - Get camera incidents
GET    /api/incidents/worker/<id>  - Get worker incidents
GET    /api/incidents/statistics   - Get incident statistics
PUT    /api/incidents/bulk-update   - Bulk update incidents
```

### Analytics & Reporting
```
GET    /api/analytics/dashboard      - Dashboard data
GET    /api/analytics/compliance     - Compliance metrics
GET    /api/analytics/incidents      - Incident statistics
GET    /api/analytics/workers        - Worker statistics
GET    /api/analytics/reports/daily  - Daily report
GET    /api/analytics/reports/weekly - Weekly report
GET    /api/analytics/reports/monthly - Monthly report
GET    /api/analytics/health         - System health
GET    /api/analytics/trends         - Trend analysis
POST   /api/analytics/export         - Export data
```

## 🔐 Authentication

The system uses JWT (JSON Web Tokens) for stateless authentication:

1. **Login**: Send credentials to `/api/auth/login`
2. **Receive**: Access token (1 hour) and refresh token (30 days)
3. **Use**: Include `Authorization: Bearer <token>` in headers
4. **Refresh**: Use refresh token to get new access token

### User Roles
- **Admin** - Full system access, user management, configuration
- **Supervisor** - Incident management, reporting, team oversight
- **Operator** - View incidents, basic operations

## 🎯 Role-Based Access Control

Permissions by role:
```
Admin:
  ✓ User management      ✓ Report generation  ✓ System settings
  ✓ Incident management  ✓ Data export        ✓ Audit log access

Supervisor:
  ✓ Incident management  ✓ Report generation  ✓ Shift management
  ✓ Data export          ✓ Audit log access

Operator:
  ✓ Incident management  ✓ View alerts
```

## 📊 Key Features

### Advanced Detection
- Multi-frame detection aggregation for confidence scoring
- Ensemble model support for improved accuracy
- Multiple helmet color detection
- Morphological operations for noise reduction
- Aspect ratio and solidity validation

### Incident Management
- Automatic incident creation on detection
- Status workflow: Open → Acknowledged → In Progress → Resolved
- Severity levels: Low, Medium, High, Critical
- Escalation workflow
- False positive marking
- Bulk incident operations

### Notifications
- Multi-channel delivery (Email, SMS, Webhook)
- HTML email templates
- Configurable alert rules
- Response tracking
- Notification history

### Analytics
- Real-time compliance metrics
- Incident trend analysis
- Worker safety statistics
- Camera performance metrics
- Customizable reporting
- PDF export capability

### Audit & Compliance
- Complete audit trail of user actions
- Configuration change tracking
- Login attempt logging
- Data retention policies
- Compliance reporting

## 🔧 Configuration

Configuration is environment-based. Edit `backend/config/settings.py`:

```python
class DevelopmentConfig:
    DEBUG = True
    DATABASE_URL = 'sqlite:///safety_monitoring.db'
    MAX_CAMERAS = 16
    DETECTION_THRESHOLD_HELMET = 0.5
    # ... more settings
```

Available environments:
- `development` - Debug mode, SQLite, verbose logging
- `production` - No debug, PostgreSQL recommended, optimized
- `testing` - Test configuration

## 📦 Project Structure

```
major project/
├── ai/
│   ├── __init__.py
│   ├── detection/
│   │   ├── advanced_detector.py
│   │   └── multi_camera_manager.py
│   └── models/
│       └── model_manager.py
├── backend/
│   ├── config/
│   │   └── settings.py
│   ├── database/
│   │   └── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── incidents.py
│   │   └── analytics.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── incident_service.py
│   │   └── notification_service.py
│   └── utils/
│       └── helpers.py
├── frontend/
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       └── js/
├── main.py
├── requirements.txt
└── README.md
```

## 🧪 Testing

Run tests with pytest:
```bash
pytest tests/
pytest tests/ --cov=backend --cov=ai
```

## 🚢 Deployment

### Development
```bash
python main.py
```

### Production (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Docker (Coming Soon)
```bash
docker build -t safety-monitoring .
docker run -p 5000:5000 safety-monitoring
```

## 📈 Performance Optimization

- **Frame buffering** for efficient multi-camera processing
- **Detection caching** to reduce duplicate processing
- **Database connection pooling** for efficient queries
- **JWT token caching** for faster authentication
- **Result aggregation** to reduce alert noise

## 🆘 Troubleshooting

### Port Already in Use
```bash
lsof -i :5000  # Find process
kill -9 <PID>   # Kill process
```

### Database Issues
```bash
# Reset database
rm safety_monitoring.db
python main.py  # Will recreate
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## 📝 License

This is a proprietary enterprise application.

## 👥 Support

For support, contact the development team or create an issue in the repository.

---

**Version**: 2.0.0 (Enterprise Edition)  
**Last Updated**: 2024  
**Status**: Production Ready ✅
