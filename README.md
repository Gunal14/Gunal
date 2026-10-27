# AI Smart Safety Monitoring System

A comprehensive real-time safety monitoring system using OpenCV and Flask for workplace safety compliance, helmet detection, and PPE monitoring.

## 🎯 Features

### Core Functionality
- **Real-time Video Processing**: Live video stream processing with OpenCV
- **Helmet Detection**: Automated detection of hard hats and safety helmets
- **PPE Compliance**: Monitors personal protective equipment usage
- **Worker Detection**: Identifies workers and tracks presence
- **Safety Alerts**: Real-time alerts for safety violations
- **Incident Logging**: Comprehensive incident tracking and history
- **Analytics Dashboard**: Visual analytics and compliance reports

### Web Interface
- **Live Monitoring**: Real-time video feed and statistics
- **Dashboard**: Overview of safety metrics and KPIs
- **Incident Management**: Complete incident history with filtering
- **Alert System**: Real-time alert management and acknowledgment
- **Analytics**: Charts and trend analysis
- **Configuration**: System settings and parameter adjustment

### Backend Features
- **Database**: SQLite for persistent data storage
- **REST API**: Full API for system control and monitoring
- **Real-time Updates**: Live statistics and alerts
- **Health Monitoring**: System health checks
- **Logging**: Comprehensive event logging

## 📋 System Requirements

### Hardware Requirements
- **Processor**: Intel i5 or equivalent (or better for real-time processing)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB for application and database
- **Camera**: USB or integrated webcam (minimum resolution 640x480)

### Software Requirements
- Python 3.8 or higher
- Windows 10/11, macOS, or Linux
- Modern web browser (Chrome, Firefox, Edge, Safari)

## 🚀 Installation

### Step 1: Clone Repository and Navigate
```bash
cd "d:\major project"
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python -c "from app import init_db; init_db()"
```

### Step 5: Run Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## 📁 Project Structure

```
d:\major project\
├── app.py                          # Flask application main entry point
├── models.py                       # Database models
├── safety_detection.py             # OpenCV detection module
├── safety_monitoring_opencv.py     # Legacy detection script
├── index.html                      # Web interface
├── requirements.txt                # Python dependencies
├── dataset_guide.txt               # Dataset information
├── README.md                       # This file
├── static/
│   ├── css/
│   │   └── style.css              # Stylesheet
│   └── js/
│       └── app.js                 # Frontend JavaScript
└── dataset/                        # Datasets and models (optional)
    ├── helmet/                     # Helmet images
    ├── no_helmet/                  # Non-helmet images
    ├── worker/                     # Worker detection dataset
    └── machine/                    # Machine/equipment images
```

## 🎮 Usage

### Starting the Application

1. **Activate Virtual Environment**
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

2. **Run Application**
```bash
python app.py
```

3. **Access Web Interface**
Open browser and navigate to: `http://localhost:5000`

### Using the Web Interface

#### Dashboard
- View overall safety metrics
- Check safety score and incident counts
- See recent incidents
- Quick access to key functions

#### Live Monitoring
- Real-time video stream from camera
- Live worker and helmet detection stats
- Active alerts display
- Detection event log

#### Incident Management
- View all recorded incidents
- Filter by date and severity
- Export incident data
- View incident details

#### Alerts
- Review active safety alerts
- Acknowledge alerts
- Configure alert parameters
- Enable/disable notifications

#### Analytics
- View incident trends
- Safety compliance charts
- Incident type distribution
- Generate reports (PDF export)

#### Settings
- Camera configuration
- Detection parameter tuning
- System information
- Database management

## 🔧 Configuration

### Camera Settings
Edit in Settings page or modify in `app.py`:
```python
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

### Detection Thresholds
In `safety_detection.py`:
```python
self.helmet_confidence_threshold = 0.5
self.worker_detection_threshold = 0.5
self.alert_cooldown = 5
```

### Alert Configuration
Via API or Settings UI:
- Detection threshold (seconds)
- Sound alerts
- Email notifications

## 🤖 Detection System

### How It Works

1. **Video Capture**: Frames captured from camera at configured FPS
2. **Preprocessing**: Convert to grayscale/HSV for analysis
3. **Worker Detection**: Cascade classifier detects faces/workers
4. **Helmet Detection**: Color and shape analysis detects helmets
5. **Safety Analysis**: Compares worker positions with helmet positions
6. **Alert Generation**: Generates alerts for violations
7. **Logging**: Records incidents in database

### Detection Methods

- **Cascade Classifier**: For face/worker detection
- **Color Thresholding**: For helmet detection (adjustable ranges)
- **Contour Analysis**: For object shape validation
- **Spatial Analysis**: For helmet-to-worker relationship

### Supported Helmet Colors
- Yellow (typical construction)
- Orange (industrial)
- White (medical/clean rooms)
- Custom colors (adjustable via HSV ranges)

## 📊 API Reference

### Monitoring Control
```
POST /api/start_monitoring      - Start safety monitoring
POST /api/stop_monitoring       - Stop safety monitoring
GET  /video_feed                - Live video stream
```

### Data Retrieval
```
GET  /api/incidents             - Get incident history
GET  /api/alerts                - Get active alerts
GET  /api/statistics            - Get monitoring statistics
```

### Configuration
```
GET  /api/alert_config          - Get alert settings
POST /api/alert_config          - Update alert settings
POST /api/clear_alerts          - Clear all alerts
```

### Health & Status
```
GET  /health                    - System health check
```

## 🗄️ Database Schema

### IncidentLog Table
- id: Primary key
- incident_type: Type of violation
- severity: LOW/MEDIUM/HIGH
- timestamp: Incident time
- location: Where incident occurred
- worker_id: Affected worker ID
- details: JSON details
- resolved: Status

### AlertHistory Table
- id: Primary key
- alert_type: Type of alert
- message: Alert message
- timestamp: Alert time
- is_active: Current status
- acknowledged_by: Who acknowledged
- acknowledged_at: Acknowledgment time

### WorkerProfile Table
- id: Primary key
- worker_id: Unique identifier
- name: Worker name
- department: Department
- shift: Work shift
- equipment_required: PPE requirements

## 🎓 Training Detection Models

### Using Your Own Dataset

1. **Prepare Dataset** following the structure in `dataset_guide.txt`
2. **Organize Images**:
   ```
   dataset/
   ├── helmet/       (helmet images)
   ├── no_helmet/    (non-helmet images)
   ├── worker/       (worker images)
   └── machine/      (equipment images)
   ```

3. **Train Model** (custom script):
   ```python
   from training_script import train_model
   train_model('dataset/', epochs=50)
   ```

4. **Update Model Path** in `safety_detection.py`:
   ```python
   self.load_pretrained_models('path/to/trained_model')
   ```

### Pre-trained Models
The system can utilize:
- Haar Cascade classifiers
- MobileNet-SSD for object detection
- Custom trained models (YOLO, Faster R-CNN)

## 🐛 Troubleshooting

### Camera Not Detected
```
Error: Cannot open camera
Solution: 
- Check camera connection
- Ensure no other app uses camera
- Try camera ID 1 or 2 in settings
```

### Low Detection Accuracy
```
Solution:
- Adjust detection thresholds in Settings
- Ensure good lighting conditions
- Train model on your specific helmets
- Check camera quality/resolution
```

### Database Errors
```
Solution:
- Delete safety_monitoring.db to reset
- Check file permissions
- Ensure disk space available
```

### Performance Issues
```
Solution:
- Lower video resolution in settings
- Reduce frame rate
- Close other applications
- Use more powerful machine
```

## 📈 Performance Optimization

### Frame Rate vs Accuracy
- 30 FPS: Good balance (default)
- 15 FPS: Lower CPU, less accurate
- 60+ FPS: High CPU required, very accurate

### Resolution vs Performance
- 640x480: Recommended (good balance)
- 1280x720: Better accuracy, higher CPU
- 1920x1080: Best accuracy, significant CPU

## 🔐 Security Considerations

1. **API Security**: Add authentication for production
2. **Data Privacy**: Implement GDPR compliance for incident data
3. **Video Storage**: Configure retention policies
4. **Access Control**: Set up user roles and permissions
5. **Encryption**: Use HTTPS for production deployment

## 📝 Logging

Application logs are written to:
- Console output during runtime
- `safety_monitoring.db` for persistent storage
- Each request logged in database

## 🚀 Deployment

### Production Deployment

1. **Set Flask to Production**:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

2. **Use WSGI Server** (Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Configure Reverse Proxy** (Nginx/Apache)

4. **Enable HTTPS** with SSL certificate

5. **Set up Monitoring** and alerting

## 📚 Additional Resources

- OpenCV Documentation: https://docs.opencv.org/
- Flask Documentation: https://flask.palletsprojects.com/
- Kaggle Datasets: https://www.kaggle.com/datasets

## 📄 License

This project is provided for educational and commercial use.

## 👥 Support

For issues, updates, and feature requests:
- Check documentation
- Review API reference
- Check troubleshooting section

## 🎉 Features Coming Soon

- [ ] Multi-camera support
- [ ] Custom AI model training interface
- [ ] Mobile app version
- [ ] Cloud integration
- [ ] Advanced analytics
- [ ] SMS notifications
- [ ] Video recording and playback
- [ ] Hardware acceleration (GPU)

## 📝 Change Log

### Version 1.0.0 (Current)
- Initial release
- Core detection system
- Web dashboard
- Real-time monitoring
- Alert system
- Analytics

---

**AI Smart Safety Monitoring System v1.0.0**
*Your workplace safety solution powered by AI*
