# 🎥 CCTV Safety System - Quick Reference Card

## 🚀 Start System (Choose One)

### Windows
```batch
START_CCTV.bat
```

### Command Line
```bash
python start_cctv.py --web --port 5000
```

### Python Script
```python
from start_cctv import setup_cctv_system, start_monitoring
system, config = setup_cctv_system()
start_monitoring(system, config, web=True, port=5000)
```

---

## 🌐 Access Dashboard
```
http://localhost:5000
```

---

## 📋 Core Commands

| Command | Purpose |
|---------|---------|
| `python start_cctv.py` | Start monitoring (headless) |
| `python start_cctv.py --web` | Start with web dashboard |
| `python start_cctv.py --report` | Generate 24h incident report |
| `python start_cctv.py --config custom.json` | Use custom config |
| `python start_cctv.py --port 8080` | Change port |
| `python start_cctv.py --test` | Debug mode |

---

## ⚙️ Configuration (Edit cctv_config.json)

### Add Camera
```json
{
  "id": "CAM_002",
  "source": "rtsp://192.168.1.100:554",
  "location": "Warehouse Floor",
  "enabled": true
}
```

### Define Zone
```json
{
  "id": "ZONE_HAZMAT",
  "type": "high_risk",
  "coordinates": [[100,100], [400,100], [400,600], [100,600]],
  "min_ppe": {"helmet": true, "gloves": true}
}
```

### Register Employee
```json
{
  "id": "EMP001",
  "name": "John Operator",
  "role": "Operator",
  "required_ppe": {"helmet": true, "gloves": true}
}
```

---

## 💻 Python API

### Create System
```python
from cctv_system import ProfessionalCCTVSystem
system = ProfessionalCCTVSystem("My CCTV")
```

### Register Camera
```python
system.register_camera("CAM_001", 0, "Main Entrance")
```

### Register Zone
```python
system.analyzer.register_safety_zone(
    "ZONE_1",
    "high_risk",
    [(0, 0), (640, 0), (640, 480), (0, 480)],
    {"helmet": True},
    restricted=False
)
```

### Register Employee
```python
system.analyzer.register_employee(
    "EMP001",
    "John Doe",
    "Operator",
    {"helmet": True}
)
```

### Start Monitoring
```python
from realtime_cctv_monitor import RealtimeCCTVMonitor
monitor = RealtimeCCTVMonitor(system)
monitor.start()
```

### Get Reports
```python
report = system.analyzer.get_incident_report(hours=24)
print(f"Incidents: {report['total_incidents']}")
```

### Stop Monitoring
```python
monitor.stop()
```

---

## 📊 System Status

```python
status = system.get_system_status()
print(status)
# Output:
# {
#   "system_name": "...",
#   "status": "online",
#   "active_cameras": 2,
#   "total_incidents": 15,
#   "critical_alerts": 2,
#   ...
# }
```

---

## 🚨 Alert Types

| Alert | Severity | Cooldown |
|-------|----------|----------|
| `missing_helmet` | HIGH | 1 min |
| `missing_ppe` | HIGH | 1 min |
| `unauthorized_access` | CRITICAL | 10 sec |
| `zone_violation` | HIGH | 1 min |
| `excessive_violations` | CRITICAL | 10 sec |

---

## 📁 Directory Structure

```
d:\major project\
├── cctv_system.py              # Core system
├── cctv_dashboard.py           # Dashboard
├── realtime_cctv_monitor.py   # Real-time engine
├── start_cctv.py              # Startup
├── START_CCTV.bat             # Windows launcher
├── cctv_config.json           # Configuration
├── recordings/                # 24/7 recordings
├── logs/                      # System logs
└── CCTV_*.md                 # Documentation
```

---

## 🔍 Finding Issues

| Issue | Solution |
|-------|----------|
| Camera not detected | Check device manager, try index 1 instead of 0 |
| High CPU | Reduce FPS in config, lower resolution |
| Disk full | System auto-deletes old videos, check `max_disk_usage_gb` |
| Web won't load | Check port isn't in use: `netstat -ano \| findstr :5000` |
| Poor detection | Ensure good lighting (300+ lux), adjust camera angle |

---

## 🎬 Recording & Playback

### Saved Recordings
```
recordings/CAM_001_2026-04-12.mp4    (Daily)
recordings/incidents/                 (Critical incidents)
```

### Replay Incident
```python
from cctv_dashboard import CCTVRecordingPlayback
playback = CCTVRecordingPlayback("recordings")
recordings = playback.list_recordings("CAM_001", "2026-04-12")
```

---

## 🌐 Web API Endpoints

```
GET  /                              Dashboard page
GET  /api/system/status             System status JSON
GET  /api/camera/{id}/feed          Live camera stream
GET  /api/incidents/report          24h incident report
GET  /api/alerts/active             Active alerts
POST /api/alerts/{id}/acknowledge   Mark alert as acknowledged
```

---

## 🎓 Full Example

```python
#!/usr/bin/env python3
from cctv_system import ProfessionalCCTVSystem
from realtime_cctv_monitor import RealtimeCCTVMonitor, CCTVWebServer

# 1. Create system
system = ProfessionalCCTVSystem("Warehouse CCTV")

# 2. Register camera
system.register_camera("CAM_001", 0, "Main Entry")

# 3. Register zone
system.analyzer.register_safety_zone(
    "ZONE_MAIN",
    "high_risk",
    [(0, 0), (640, 0), (640, 480), (0, 480)],
    {"helmet": True},
    restricted=False
)

# 4. Register employee
system.analyzer.register_employee("EMP001", "John", "Operator", {"helmet": True})

# 5. Start monitoring
monitor = RealtimeCCTVMonitor(system)
monitor.start()

# 6. Start web server
web = CCTVWebServer(monitor, port=5000)
web.run()  # Visit http://localhost:5000
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| CCTV_IMPLEMENTATION.md | Complete implementation details |
| CCTV_SETUP_GUIDE.md | Detailed setup & configuration |
| cctv_config.json | System configuration |
| cctv_system.log | System logs |

---

## ✅ Implementation Status

✅ Core CCTV system (24/7 recording)  
✅ Real-time detection (helmet, PPE)  
✅ Multi-camera support  
✅ Professional dashboard  
✅ Alert system (escalation)  
✅ Incident management  
✅ Analytics & reporting  
✅ Web API & interface  
✅ Employee database  
✅ Zone management  
✅ Configuration system  
✅ Windows launcher  

---

**Your CCTV Safety System is Production Ready! 🚀**

Start now: `python start_cctv.py --web`
