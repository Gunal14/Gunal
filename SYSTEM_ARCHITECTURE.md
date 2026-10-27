# CCTV Safety Detection System - Architecture Diagram

## System Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                 PROFESSIONAL CCTV SAFETY MONITORING SYSTEM                │
└────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          INPUT LAYER - CAMERAS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│    📷 USB Webcam      📹 IP Camera        📽️ Video File                    │
│    (Device 0)         (RTSP Stream)       (MP4/AVI)                        │
│         │                   │                   │                          │
│         └───────────────────┴───────────────────┘                          │
│                           │                                                 │
│                           ▼                                                 │
│              Frame Capture Workers (Multi-threaded)                         │
│              ├─ CAM_001 Capture Thread                                     │
│              ├─ CAM_002 Capture Thread                                     │
│              ├─ CAM_003 Capture Thread                                     │
│              └─ Resolution: 1280x720 @ variable FPS                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PROCESSING LAYER - DETECTION                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Detection Workers (Multi-threaded, Real-time):                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ For Each Frame:                                                     │   │
│  │  1. Worker Detection (Face DetectionCascade)                       │   │
│  │  2. Helmet Detection (Color Range Analysis)                        │   │
│  │  3. PPE Detection (Gloves, Vest, Mask)                            │   │
│  │  4. Zone Violation Check (Polygon Hit Test)                        │   │
│  │  5. Compliance Scoring (0-100%)                                   │   │
│  │  6. Frame Recording (Circular Buffer)                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Output: Detection Results {workers, helmets, violations, confidence}      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌───────────────┐  ┌──────────────┐  ┌────────────┐
        │  Recording    │  │  Analysis    │  │  Alerting  │
        │  System       │  │  System      │  │  System    │
        └───────────────┘  └──────────────┘  └────────────┘
                    │               │               │
                    ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STORAGE & ACTION LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  📹 Video Recording          📊 Database                 🚨 Alerts         │
│  ├─ recordings/              ├─ Incidents (1000)        ├─ missing_helmet  │
│  │  ├─ CAM_001_*.mp4        ├─ Employees                ├─ missing_ppe    │
│  │  ├─ CAM_002_*.mp4        ├─ Zones                    ├─ unauthorized   │
│  │  └─ incidents/            ├─ Alerts                  ├─ zone_violation │
│  │     └─ {timestamp}/       └─ Analytics               └─ excessive      │
│  └─ Daily rotation                                                         │
│     (Auto-delete old)        Memory-based storage      Queue + Handlers    │
│                              (Live data)               (Email, SMS, etc)   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌───────────────┐  ┌──────────────┐  ┌────────────┐
        │   Recording   │  │  Analytics   │  │    Alerts  │
        │   System      │  │  System      │  │   System   │
        └───────────────┘  └──────────────┘  └────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OUTPUT LAYER - INTERFACE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  🌐 Web Dashboard                 📊 REST API                               │
│  ├─ http://localhost:5000        ├─ /api/system/status                    │
│  ├─ Multi-camera feed            ├─ /api/camera/{id}/feed                 │
│  ├─ Status monitoring            ├─ /api/incidents/report                 │
│  ├─ Alert display                ├─ /api/alerts/active                    │
│  ├─ Compliance score             ├─ /api/alerts/{id}/acknowledge          │
│  └─ Incident history             └─ Extensible for integration             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Flow

```
┌──────────────────┐
│   Start System   │
│   (start_cctv.py)│
└────────┬─────────┘
         │
         ▼
┌───────────────────────────────────┐
│  Load Configuration               │
│  (cctv_config.json)              │
│  - Cameras                        │
│  - Zones                          │
│  - Employees                      │
│  - Alert settings                 │
└────────┬────────────────────────────┘
         │
         ▼
┌───────────────────────────────────┐
│  Initialize ProfessionalCCTVSystem│
│  - CCTVFrameRecorder              │
│  - CCTVSafetyAnalyzer             │
│  - CCTVAlertEngine                │
└────────┬────────────────────────────┘
         │
         ▼
┌───────────────────────────────────────────┐
│  Register Cameras, Zones, Employees       │
│  from Configuration                       │
└────────┬────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────┐
│  Start RealtimeCCTVMonitor                     │
│  For each camera:                              │
│    1. Start Capture Thread (Frame Queue)       │
│    2. Start Detection Thread (Analysis Queue)  │
│    3. Start Recording Thread (Recording Queue) │
└────────┬───────────────────────────────────────┘
         │
    ┌────┴────────────────────────────────────────────┐
    │  CONTINUOUS OPERATION (Loop)                   │
    │                                                │
    ├─ Capture Thread:                              │
    │  ├─ Read from camera                          │
    │  ├─ Add to frame queue                        │
    │  ├─ Calculate FPS                             │
    │  └─ Handle disconnection                      │
    │                                                │
    ├─ Detection Thread:                            │
    │  ├─ Get frame from queue                      │
    │  ├─ Perform detection                         │
    │  ├─ Check violations                          │
    │  ├─ Log incidents                             │
    │  ├─ Trigger alerts                            │
    │  └─ Save incident clips                       │
    │                                                │
    └─ Recording Thread:                            │
       ├─ Get frame from queue                      │
       ├─ Write to video file                       │
       ├─ Check disk usage                          │
       └─ Cleanup old files                         │
    │                                                │
    └────────────────────────────────────────────┬──┘
                                                  │
                                                  ▼
                                        ┌──────────────────────┐
                                        │  Web Server Running  │
                                        │  (Flask)             │
                                        │  Port 5000           │
                                        └──────────────────────┘
                                                  │
                                                  ▼
                                        ┌──────────────────────┐
                                        │  Users Access        │
                                        │  Dashboard & API     │
                                        │  http://localhost:5000
                                        └──────────────────────┘
```

---

## Data Flow Diagram

```
CAMERA INPUT
    │
    ├─────────────────────┬──────────────────────┬─ ─ ─ ─ ─ ─ ─ ┐
    │                     │                      │                │
    ▼                     ▼                      ▼                ▼
┌─────────┐          ┌─────────┐          ┌─────────┐      ┌──────────┐
│CAM_001  │          │CAM_002  │          │CAM_003  │ ...  │CAM_N     │
│Open CV  │          │RTSP     │          │MP4 File │      │(Other)   │
└────┬────┘          └────┬────┘          └────┬────┘      └────┬─────┘
     │                    │                     │                │
     └────────────────────┼─────────────────────┼────────────────┘
                          │
                    Frame Queue
                  (FIFO, Max 30)
                          │
                          ▼
                  ┌─────────────────┐
                  │   Preprocessing │
                  │ ├─ Resize       │
                  │ ├─ Color Space  │
                  │ └─ Normalize    │
                  └────────┬────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
      ┌─────────┐  ┌─────────┐  ┌──────────────┐
      │ Worker  │  │ Helmet  │  │ ZoneCheck    │
      │Detector │  │Detector │  │ PPEValidator │
      └────┬────┘  └────┬────┘  └──────┬───────┘
           │             │              │
           └─────────────┼──────────────┘
                         │
                    Detection
                   Result Dict
                    {workers,
                    helmets,
                    violations}
                         │
                ┌────────┴────────┐
                │                 │
                ▼                 ▼
          ┌──────────┐      ┌──────────┐
          │Recording │      │Analysis  │
          └────┬─────┘      └────┬─────┘
               │                 │
               ▼                 ▼
          ┌──────────┐      ┌──────────┐
          │ Save to  │      │ Check    │
          │ MP4 File │      │Violations│
          └──────────┘      └────┬─────┘
               │                 │
               │            ┌────┴────┐
               │            │          │
               │            ▼          ▼
               │       ┌─────────┐  ┌─────────┐
               │       │Log Inc. │  │Trigger  │
               │       │in DB    │  │Alerts   │
               │       └─────────┘  └────┬────┘
               │                         │
               │                    ┌────┴────────┐
               │                    │             │
               │                    ▼             ▼
               │              ┌─────────┐  ┌──────────┐
               │              │ Email   │  │ Save Clip│
               │              │ Notify  │  │ w/ Meta  │
               │              └─────────┘  └──────────┘
               │
               ▼
          ┌──────────────────────────┐
          │  recordings/ Directory   │
          ├──────────────────────────┤
          │ CAM_001_2026-04-12.mp4   │
          │ CAM_002_2026-04-12.mp4   │
          │ CAM_003_2026-04-12.mp4   │
          │ incidents/               │
          │  └─ incident_data.json   │
          │  └─ incident_clip.mp4    │
          └──────────────────────────┘
```

---

## Module Dependencies

```
┌──────────────────────────────────────────────────────┐
│         Application Entry Points                    │
├──────────────────────────────────────────────────────┤
│  • start_cctv.py          (Configuration & Setup)   │
│  • realtime_cctv_monitor.py (Integration Engine)    │
│  • START_CCTV.bat         (Windows Launcher)        │
└──────────┬───────────────────────────────────────────┘
           │
           ├─ Imports ──────┐
           │                │
           ▼                ▼
    ┌─────────────┐   ┌──────────────┐
    │cctv_system  │   │cctv_dashboard│
    ├─────────────┤   ├──────────────┤
    │• FrameRecor │───┤• Dashboard   │
    │• Analyzer   │   │• Hud Info    │
    │• AlertEngine│   │• Analytics   │
    │• MainSys    │   │• Playback    │
    └─────────────┘   └──────────────┘
           │                │
           └────────┬───────┘
                    │
                    ▼
           ┌───────────────────┐
           │   Config File     │
           │ cctv_config.json  │
           ├───────────────────┤
           │• Cameras          │
           │• Zones            │
           │• Employees        │
           │• Alerts           │
           │• Recording        │
           │• Detection        │
           └───────────────────┘
                    │
                    ▼
           ┌───────────────────┐
           │  External Libraries│
           ├───────────────────┤
           │• OpenCV (cv2)     │
           │• NumPy            │
           │• Flask (Web)      │
           │• JSON (Config)    │
           │• Threading        │
           │• Queue            │
           │• Logging          │
           └───────────────────┘

Dependency Tree:
  start_cctv.py
    ├─ cctv_system.py
    │   ├─ cv2 (OpenCV)
    │   ├─ numpy
    │   ├─ threading
    │   ├─ queue
    │   ├─ json
    │   └─ datetime
    │
    ├─ realtime_cctv_monitor.py
    │   ├─ cctv_system.py
    │   ├─ cctv_dashboard.py
    │   ├─ cv2 (OpenCV)
    │   ├─ flask
    │   └─ threading
    │
    └─ cctv_dashboard.py
        ├─ cv2 (OpenCV)
        ├─ numpy
        ├─ json
        └─ pathlib
```

---

## Deployment Architecture

```
┌────────────────────────────────────────────────────────────┐
│              Production Deployment (Optional)             │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Production Server (Windows/Linux)                  │ │
│  ├──────────────────────────────────────────────────────┤ │
│  │                                                      │ │
│  │  ┌─────────────────────────────────────────────┐    │ │
│  │  │  CCTV System (Python Application)           │    │ │
│  │  │  ├─ cctv_system.py                          │    │ │
│  │  │  ├─ realtime_cctv_monitor.py               │    │ │
│  │  │  ├─ cctv_dashboard.py                       │    │ │
│  │  │  └─ Configuration                           │    │ │
│  │  └──────────────┬──────────────────────────────┘    │ │
│  │                 │                                    │ │
│  │                 ▼                                    │ │
│  │  ┌─────────────────────────────────────────────┐    │ │
│  │  │  Data Storage                               │    │ │
│  │  │  ├─ recordings/           (Videos)          │    │ │
│  │  │  ├─ cctv_system.log       (Logs)            │    │ │
│  │  │  └─ cctv_config.json      (Config)          │    │ │
│  │  └─────────────────────────────────────────────┘    │ │
│  │                                                      │ │
│  └──────────────────────────────────────────────────────┘ │
│           │                                                │
│           ├─ Reverse Proxy (Nginx/Apache)               │
│           │  ├─ HTTPS/SSL Encryption                   │
│           │  ├─ Load Balancing                         │
│           │  └─ Authentication                         │
│           │                                              │
│           ▼                                              │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  External Systems (Integration Points)             │ │
│  ├──────────────────────────────────────────────────────┤ │
│  │  • Email Notification Service                      │ │
│  │  • SMS Gateway                                     │ │
│  │  • HR/Payroll System                               │ │
│  │  • Access Control System                           │ │
│  │  • Security Dashboard                              │ │
│  │  • Analytics Platform                              │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   ┌─────────┐      ┌─────────┐      ┌──────────┐
   │  Users  │      │Corporate│      │Security  │
   │Browsers │      │Network  │      │Team      │
   └─────────┘      └─────────┘      └──────────┘
        │                 │               │
        └─────────────────┼───────────────┘
                          │
                    (HTTP/HTTPS)
                          │
                    Dashboard View
                    API Access
```

---

## Performance Monitoring

```
Live System Metrics:
┌────────────────────────────────┐
│  REAL-TIME PERFORMANCE         │
├────────────────────────────────┤
│ FPS (Frames/Sec):      15      │
│ Detection Latency:   <500ms     │
│ CPU Usage:         15-25%       │
│ Memory:            200-400MB    │
│ Disk/Hour:         ~250MB       │
│ Disk/Day:          ~6GB         │
│ Storage Used:      XX days      │
│                                │
│ Detections/Sec:      variable  │
│ Alerts/Hour:          variable │
│ Frames Processed:  1,234,567   │
│ Incidents Logged:      42      │
│ System Uptime:      XX days    │
└────────────────────────────────┘
```

---

## Integration Points

```
CCTV System Integration Points:

┌─────────────────────────────────┐
│  Existing Backend Systems       │
├─────────────────────────────────┤
│  • User Authentication          │
│  • Database (SQLAlchemy ORM)    │
│  • Email Service                │
│  • SMS Notifications            │
│  • Incident Management          │
│  • Employee Database            │
│  • Analytics Engine             │
│  • Reporting System             │
└─────────────────────────────────┘
         ▲
         │ (Can be integrated)
         │
┌─────────────────────────────────┐
│  CCTV System API Endpoints      │
├─────────────────────────────────┤
│  /api/system/status             │
│  /api/camera/{id}/feed          │
│  /api/incidents/report          │
│  /api/alerts/active             │
│  /api/alerts/{id}/acknowledge   │
│  (Extensible for more)          │
└─────────────────────────────────┘
         ▲
         │
┌─────────────────────────────────┐
│  External Services              │
├─────────────────────────────────┤
│  • Email (SMTP)                 │
│  • SMS (Twilio, AWS SNS)        │
│  • Slack/Teams (Webhooks)       │
│  • Cloud Storage (S3, Azure)    │
│  • Analytics (Datadog, New Relic)
└─────────────────────────────────┘
```

---

This architecture is designed for:
✅ Scalability (multi-camera support)  
✅ Reliability (multi-threaded, error handling)  
✅ Performance (optimized detection, streaming)  
✅ Maintainability (modular design)  
✅ Integration (REST API, extensible)  
✅ Security (configurable, auditability)  
