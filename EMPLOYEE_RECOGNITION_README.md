# Enhanced AI Safety Monitoring System with Employee Recognition

## Overview

This enhanced safety monitoring system now includes **facial recognition** and **employee-specific compliance tracking**. The system can:

- ✅ Recognize individual employees using facial recognition
- ✅ Track safety compliance per employee
- ✅ Send personalized alerts to employees and emergency contacts
- ✅ Maintain detailed compliance statistics
- ✅ Support SMS, WhatsApp, and email notifications

## Features

### Employee Recognition
- Facial recognition using advanced AI algorithms
- Real-time employee identification in video streams
- Confidence scoring for recognition accuracy

### Safety Compliance Tracking
- Individual employee compliance monitoring
- Helmet, vest, glove, and boot detection
- Historical compliance statistics
- Risk assessment and alerts

### Automated Notifications
- SMS alerts to employees
- WhatsApp messages for instant communication
- Email notifications with detailed reports
- Emergency contact notifications

### Web Interface
- Employee management dashboard
- Real-time compliance statistics
- Training data upload interface
- Alert history and reporting

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Employee Database

```bash
python setup_employee_database.py
```

This will:
- Create database tables for employees
- Add sample employee data
- Setup training data directories

### 3. Configure Notifications

Edit `config.py` to add your notification settings:

```python
# Email configuration
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-app-password'

# WhatsApp configuration (optional)
WHATSAPP_API_KEY = 'your-whatsapp-api-key'
WHATSAPP_PHONE_NUMBER = '+1234567890'

# SMS configuration (optional)
SMS_API_KEY = 'your-sms-api-key'
SMS_PHONE_NUMBER = '+1234567890'
```

### 4. Upload Employee Photos

1. Start the web server: `python run.py`
2. Go to `http://localhost:5000/employees`
3. Add employees or upload face photos for existing ones
4. Upload training images (with/without helmets)

### 5. Start Enhanced Monitoring

```bash
python enhanced_real_time_monitoring.py --camera-id 1 --location "Main Entrance"
```

## System Architecture

### Database Models

- **Employee**: Employee profiles with facial encodings
- **EmployeeRecognition**: Recognition events and compliance
- **SafetyAlert**: Alert history and notifications
- **EmergencyContact**: Emergency notification contacts

### Services

- **EmployeeService**: Facial recognition and employee management
- **EnhancedSafetyMonitor**: Integrated monitoring with notifications
- **NotificationService**: Multi-channel alert delivery

### API Endpoints

- `GET/POST /api/v1/employees` - Employee CRUD operations
- `GET /api/v1/employees/{id}/stats` - Employee statistics
- `POST /api/v1/employees/{id}/training` - Upload training images

## Usage Examples

### Basic Monitoring

```python
from enhanced_real_time_monitoring import EnhancedRealtimeSafetyMonitor

# Start monitoring with employee recognition
monitor = EnhancedRealtimeSafetyMonitor(
    camera_source=0,  # Webcam
    camera_id=1,
    location="Main Entrance"
)
monitor.run()
```

### Employee Management

```python
from backend.services.employee_service import EmployeeService

# Add new employee
employee_service = EmployeeService(db_session)
success, emp_id = employee_service.add_employee({
    'employee_id': 'EMP001',
    'name': 'John Smith',
    'email': 'john@company.com',
    'department': 'Construction'
}, face_image_file)
```

### Custom Notifications

```python
from backend.services.enhanced_safety_monitor import EnhancedSafetyMonitor

# Send custom alert
monitor = EnhancedSafetyMonitor(db_session, employee_service, notification_service)
monitor.process_frame(frame, camera_id=1, location="Warehouse")
```

## Training Data

### Face Recognition Training

1. Upload clear face photos for each employee
2. Ensure good lighting and frontal face position
3. Use high-resolution images (at least 200x200 pixels)

### Helmet Detection Training

1. Upload images of employees with helmets
2. Upload images of employees without helmets
3. Include various helmet types and colors
4. Train in different lighting conditions

### Directory Structure

```
static/uploads/employees/
├── EMP001_face_20241201_120000.jpg
├── EMP002_face_20241201_120100.jpg
└── training/
    ├── EMP001_helmet_001.jpg
    ├── EMP001_no_helmet_001.jpg
    ├── EMP002_helmet_001.jpg
    └── EMP002_no_helmet_001.jpg
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///safety_monitoring.db

# Security
SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600

# AI Settings
DETECTION_THRESHOLD_WORKER=0.5
DETECTION_THRESHOLD_HELMET=0.6
FACE_RECOGNITION_TOLERANCE=0.6

# Notifications
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_NUMBER=+1234567890
```

### Advanced Configuration

Edit `backend/config/settings.py` for advanced settings:

```python
class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///safety_monitoring.db')

    # AI Parameters
    FACE_RECOGNITION_TOLERANCE = 0.6
    HELMET_CONFIDENCE_THRESHOLD = 0.5
    EMPLOYEE_RECOGNITION_COOLDOWN = 300  # seconds

    # Notification Settings
    ALERT_COOLDOWN = 300  # seconds between same alerts
    MAX_EMERGENCY_CONTACTS = 10

    # Camera Settings
    MAX_CAMERAS = 40
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FPS_TARGET = 30
```

## Troubleshooting

### Common Issues

1. **Face Recognition Not Working**
   - Ensure face images are clear and well-lit
   - Check that dlib and face_recognition are properly installed
   - Verify employee photos are uploaded

2. **Low Detection Accuracy**
   - Upload more training images
   - Ensure consistent lighting conditions
   - Check camera quality and positioning

3. **Notifications Not Sending**
   - Verify API keys and credentials
   - Check network connectivity
   - Review SMTP/WhatsApp/SMS configurations

4. **Database Errors**
   - Run `python setup_employee_database.py` to initialize
   - Check database file permissions
   - Verify SQLAlchemy configuration

### Performance Optimization

1. **Face Recognition Speed**
   - Use GPU acceleration if available
   - Reduce frame processing resolution
   - Implement face detection caching

2. **Memory Usage**
   - Limit stored face encodings
   - Implement database pagination
   - Use streaming for large datasets

3. **Network Efficiency**
   - Compress images before upload
   - Implement notification batching
   - Use WebSocket for real-time updates

## API Reference

### Employee Endpoints

#### Get All Employees
```http
GET /api/v1/employees
```

#### Add Employee
```http
POST /api/v1/employees
Content-Type: multipart/form-data

{
  "employee_id": "EMP001",
  "name": "John Smith",
  "email": "john@company.com",
  "face_image": <file>
}
```

#### Get Employee Details
```http
GET /api/v1/employees/{employee_id}
```

#### Update Employee
```http
PUT /api/v1/employees/{employee_id}
Content-Type: application/json

{
  "department": "New Department",
  "phone": "+1234567890"
}
```

#### Upload Training Image
```http
POST /api/v1/employees/{employee_id}/training
Content-Type: multipart/form-data

{
  "image_type": "helmet",
  "image": <file>
}
```

#### Get Employee Statistics
```http
GET /api/v1/employees/{employee_id}/stats
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub
- Contact the development team

---

**Version**: 2.0.0
**Last Updated**: December 2024
**Compatibility**: Python 3.8+