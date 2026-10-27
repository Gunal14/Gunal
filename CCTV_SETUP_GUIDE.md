# Professional CCTV Safety Detection System - Complete Setup Guide

**Your app is now a production-ready CCTV safety detection system for employees!**

## 🎯 What You Get

### Core Features
✅ **24/7 Continuous Recording** - Automatic frame-by-frame recording with intelligent disk management  
✅ **Real-time Safety Detection** - Helmet, PPE, and safety zone compliance  
✅ **Multi-Camera Support** - Synchronized monitoring of multiple cameras  
✅ **Employee Recognition** - Employee database with safety profiles  
✅ **Incident Video Clips** - Auto-save violation footage for review  
✅ **Smart Alert System** - Real-time alerts with severity levels and escalation  
✅ **Professional Dashboard** - Live monitoring interface with multi-camera view  
✅ **Analytics & Reporting** - Compliance reports, incident trends, employee metrics  
✅ **Zone Management** - Define high-risk areas, restricted zones, hazard areas  
✅ **Archive System** - Long-term video storage with retrieval capability

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
cd "d:\major project"
pip install -r requirements.txt
```

### Step 2: Start CCTV System
**Option A: Dashboard Only (Recommended for Testing)**
```bash
python realtime_cctv_monitor.py
```

**Option B: With Web Interface**
```bash
python realtime_cctv_monitor.py --web --port 5000
```
Then open: http://localhost:5000

### Step 3: Verify Cameras
The system will automatically detect your webcam. You should see:
```
PROFESSIONAL CCTV SAFETY MONITORING SYSTEM
============================================================
System Status: online
Cameras: 1/1
============================================================
```

---

## 📚 System Architecture

```
CCTV System Components:
├── cctv_system.py (Core CCTV System)
│   ├── CCTVFrameRecorder (24/7 Recording)
│   ├── CCTVSafetyAnalyzer (Detection & Analysis)
│   ├── CCTVAlertEngine (Alert Management)
│   └── ProfessionalCCTVSystem (Coordinator)
│
├── cctv_dashboard.py (Visualization)
│   ├── CCTVDashboard (Multi-camera view)
│   ├── Single camera detailed view
│   └── Analytics dashboard
│
└── realtime_cctv_monitor.py (Integration Engine)
    ├── RealtimeCCTVMonitor (Real-time processing)
    ├── Frame capture workers
    ├── Detection workers
    └── CCTVWebServer (HTTP API)
```

---

## 🔧 Configuration Guide

### 1. Register Cameras

```python
# In your startup script:
system = ProfessionalCCTVSystem("My Warehouse Safety CCTV")

# Register cameras
system.register_camera("CAM_001", 0, "Main Entrance")      # Webcam
system.register_camera("CAM_002", "rtsp://...", "Floor")   # IP Camera
system.register_camera("CAM_003", "video.mp4", "Office")   # Video file
```

### 2. Define Safety Zones

```python
# High-risk area requiring helmet
system.analyzer.register_safety_zone(
    zone_id="ZONE_HAZMAT",
    zone_type="high_risk",
    coordinates=[(100, 100), (400, 100), (400, 600), (100, 600)],
    min_ppe={"helmet": True, "gloves": True, "vest": True},
    restricted=False
)

# Restricted area - no unauthorized access
system.analyzer.register_safety_zone(
    zone_id="ZONE_RESTRICTED",
    zone_type="confined_space",
    coordinates=[(500, 100), (800, 100), (800, 600), (500, 600)],
    min_ppe={"helmet": True, "mask": True},
    restricted=True  # Requires authorization
)
```

### 3. Register Employees

```python
# Add employees to safety database
system.analyzer.register_employee(
    emp_id="EMP001",
    name="John Doe",
    role="Warehouse Operator",
    required_ppe={"helmet": True, "gloves": True}
)

system.analyzer.register_employee(
    emp_id="EMP002",
    name="Jane Smith",
    role="Safety Officer",
    required_ppe={"helmet": True}
)
```

### 4. Setup Alert Handlers

```python
# Custom alert handler
def email_alert_handler(alert):
    """Send email on critical alerts"""
    if alert["severity"] == "critical":
        send_email(
            to="safety@company.com",
            subject=f"CRITICAL: {alert['type']}",
            body=json.dumps(alert, indent=2)
        )

# Register handler
system.alert_engine.register_alert_handler("missing_helmet", email_alert_handler)
system.alert_engine.register_alert_handler("unauthorized_access", email_alert_handler)
```

---

## 📊 Real-Time Monitoring

### Start Monitoring System

```python
from realtime_cctv_monitor import RealtimeCCTVMonitor

# Create monitor
monitor = RealtimeCCTVMonitor(system)

# Start all cameras
monitor.start()

# Get live feeds
live_frame = monitor.get_live_feed("CAM_001")

# Get dashboard view
dashboard = monitor.get_dashboard_view()

# Get detailed camera view
detailed = monitor.get_detailed_view("CAM_001")

# Get performance report
report = monitor.get_performance_report()
print(json.dumps(report, indent=2))

# When done
monitor.stop()
```

---

## 🎬 Video Recording & Playback

### Continuous Recording

The system automatically records 24/7:
- **Location**: `recordings/` directory
- **Format**: MP4 (H.264)
- **Quality**: 1280x720 @ 15 FPS
- **Storage**: Automatic rotation (oldest deleted when disk full)
- **Daily Files**: `CAM_001_2026-04-12.mp4`

### Incident Clips

Critical incidents auto-save to: `recordings/incidents/{timestamp}/`
- **Video**: `missing_helmet_critical.mp4`
- **Metadata**: `metadata.json`

### Playback

```python
from cctv_system import CCTVFrameRecorder
from cctv_dashboard import CCTVRecordingPlayback

playback = CCTVRecordingPlayback("recordings")

# List today's recordings
recordings = playback.list_recordings("CAM_001", "2026-04-12")

# Search recordings
results = playback.search_recordings(
    start_time=datetime(2026, 4, 12, 8, 0),
    end_time=datetime(2026, 4, 12, 17, 0),
    camera_id="CAM_001",
    incident_type="missing_helmet"
)

# Play incident clip
incident_file = playback.play_incident_clip("missing_helmet_critical")
```

---

## 🚨 Alert System

### Alert Types

| Alert Type | Severity | Description | Action |
|-----------|----------|-------------|--------|
| `missing_helmet` | HIGH | Worker without safety helmet | Notify supervisor |
| `missing_ppe` | HIGH | Incomplete PPE in zone | Notify supervisor |
| `unauthorized_access` | CRITICAL | Restricted area access | Block + Notify security |
| `zone_violation` | HIGH | Entering hazard zone unprepared | Notify worker |
| `excessive_violations` | CRITICAL | Employee pattern of violations | Safety review |

### Alert Escalation

```python
# Alerts escalate based on frequency
# 1st violation: Email supervisor (5 min cooldown)
# 2nd violation: SMS alert (3 min cooldown)  
# 3rd violation: Call security (1 min cooldown)
# Repeated: System blocks access (10 sec alert)
```

### Acknowledge Alerts

```python
# Mark alert as acknowledged
system.alert_engine.acknowledge_alert(
    alert_id="missing_helmet_2026-04-12T10:30:45.123Z",
    acknowledged_by="supervisor@company.com"
)

# Get active unacknowledged alerts
active = system.alert_engine.get_active_alerts()
critical = system.alert_engine.get_active_alerts(severity_filter="critical")
```

---

## 📈 Analytics & Reporting

### Generate Reports

```python
# 24-hour incident report
report_24h = system.analyzer.get_incident_report(hours=24)
print(f"Total Incidents: {report_24h['total_incidents']}")
print(f"Critical: {report_24h['critical_incidents']}")
print(f"Top Violators: {report_24h['top_violators']}")

# Weekly report
report_week = system.analyzer.get_incident_report(hours=168)

# Export report
with open("incident_report.json", "w") as f:
    json.dump(report_24h, f, indent=2)
```

### Compliance Metrics

```python
# Employee safety score
for emp_id, emp_data in system.analyzer.employee_db.items():
    print(f"{emp_data['name']}: Score {emp_data['safety_score']}/100")

# Overall system compliance
compliance = system.analyzer.get_incident_report()
```

---

## 🌐 Web Dashboard

### Access Dashboard

1. **Start system**:
   ```bash
   python realtime_cctv_monitor.py --web --port 5000
   ```

2. **Open browser**: http://localhost:5000

3. **Features**:
   - Multi-camera live feeds
   - System status monitoring
   - Active incident tracking
   - Alert management
   - Real-time FPS display
   - Compliance score
   - Employee safety metrics

### API Endpoints

```
GET  /api/system/status          - System status
GET  /api/camera/{id}/feed       - Live camera stream
GET  /api/incidents/report       - 24h incident report  
GET  /api/alerts/active          - Active alerts
POST /api/alerts/{id}/acknowledge - Acknowledge alert
POST /api/zones/create           - Create safety zone
GET  /api/employees/list         - List employees
POST /api/employees/register     - Register employee
```

---

## 🔒 Security Best Practices

1. **Access Control**
   - Run behind reverse proxy (nginx)
   - Use HTTPS/SSL certificates
   - Implement authentication
   - Log all access

2. **Video Storage**
   - Encrypt stored recordings
   - Set retention policies
   - Backup critical incidents
   - Restrict access to videos

3. **Alert Handling**
   - Don't store PII in alerts
   - Use secure email/SMS
   - Implement audit logs
   - Encrypt notifications

4. **System Security**
   - Update dependencies regularly
   - Run with minimal privileges
   - Monitor system resources
   - Implement rate limiting

---

## 🐛 Troubleshooting

### Camera Not Detected
```python
# Check if camera works
import cv2
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera not available")
cap.release()
```

### High CPU Usage
- Reduce FPS: `recorder.fps = 10`
- Lower resolution: `recorder.frame_width = 640`
- Disable detailed detection

### Disk Full
- Check with: `df -h`
- Increase `max_disk_usage_gb` in recorder
- System auto-deletes old files

### Poor Detection
- Check lighting conditions
- Adjust camera angle
- Tune detection thresholds
- Use better detection models (YOLO)

---

## 📝 Implementation Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure cameras (IP address/device)
- [ ] Define safety zones
- [ ] Register employees
- [ ] Setup alert handlers
- [ ] Configure email/SMS notifications
- [ ] Test with sample video
- [ ] Verify recording works
- [ ] Check incident reporting
- [ ] Deploy to production

---

## 🎓 Examples

### Complete Setup Example

```python
#!/usr/bin/env python3
from cctv_system import ProfessionalCCTVSystem
from realtime_cctv_monitor import RealtimeCCTVMonitor, CCTVWebServer
import time
import json

# 1. Initialize system
system = ProfessionalCCTVSystem("Warehouse Safety CCTV v1.0")

# 2. Register cameras
system.register_camera("CAM_001", 0, "Warehouse Floor")
system.register_camera("CAM_002", "rtsp://192.168.1.100:554", "Loading Area")

# 3. Define zones
system.analyzer.register_safety_zone(
    "ZONE_MAIN",
    "high_risk",
    [(0, 0), (1280, 0), (1280, 720), (0, 720)],
    min_ppe={"helmet": True},
    restricted=False
)

# 4. Register employees
employees = [
    ("EMP001", "John Operator", "Operator"),
    ("EMP002", "Jane Supervisor", "Supervisor"),
]
for emp_id, name, role in employees:
    system.analyzer.register_employee(emp_id, name, role, {"helmet": True})

# 5. Setup alerts
def critical_alert(alert):
    if alert["severity"] == "critical":
        print(f"🚨 CRITICAL ALERT: {alert['type']}")

system.alert_engine.register_alert_handler("missing_helmet", critical_alert)
system.alert_engine.register_alert_handler("unauthorized_access", critical_alert)

# 6. Start monitoring
monitor = RealtimeCCTVMonitor(system)
monitor.start()

# 7. Web server (optional)
web_server = CCTVWebServer(monitor, port=5000)

print("System running. Visit http://localhost:5000")
print(json.dumps(system.get_system_status(), indent=2))

# 8. Keep running
try:
    web_server.run()
except KeyboardInterrupt:
    print("Shutting down...")
    monitor.stop()
    
# 9. Generate report after 24 hours
# report = system.analyzer.get_incident_report(hours=24)
# print(json.dumps(report, indent=2))
```

---

## 📞 Support

For issues or questions:
1. Check logs: `logs/app.log`
2. Review configuration
3. Test with simple video file
4. Check system resources (CPU, RAM, Disk)

---

## ✨ Next Steps

1. **Deploy**: Move to production server
2. **Monitor**: 24/7 incident tracking
3. **Report**: Daily/weekly compliance reports
4. **Integrate**: Connect with HR/security systems
5. **Optimize**: Use YOLO/TensorFlow for better accuracy

Your CCTV safety detection system is now ready! 🎉
