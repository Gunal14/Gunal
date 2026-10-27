# CCTV Safety Detection System - Architecture & Flow Diagrams
## Presentation-Ready Technical Documentation

---

## SYSTEM COMPONENT HIERARCHY

```
┌─────────────────────────────────────────────────────────────────┐
│                  CCTV SAFETY DETECTION SYSTEM                  │
│                    (Main Orchestrator)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  INPUT SUBSYSTEM (Camera Management)                    │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • USB Webcams         • IP Cameras (RTSP)              │  │
│  │ • Video Files         • HLS Streams (future)           │  │
│  │                                                          │  │
│  │ Component: CCTVFrameRecorder                            │  │
│  │ ├─ start_continuous_recording()                        │  │
│  │ ├─ _recording_worker() [Per-camera threads]            │  │
│  │ └─ _manage_disk_space()                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│            ↓ (Frame Queues)                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PROCESSING SUBSYSTEM (Real-Time Detection)             │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ Component: CCTVSafetyAnalyzer                           │  │
│  │ ├─ Worker Detection (Face Cascade)                      │  │
│  │ ├─ Helmet Detection (HSV Color ranges)                  │  │
│  │ ├─ PPE Verification (Gloves, Vest, Mask)              │  │
│  │ ├─ Zone Violation Check (Polygon test)                 │  │
│  │ ├─ Compliance Scoring (0-100%)                         │  │
│  │ └─ Incident Logging                                    │  │
│  │                                                          │  │
│  │ Component: CCTVAlertEngine                              │  │
│  │ ├─ trigger_alert()                                     │  │
│  │ ├─ register_alert_handler()                            │  │
│  │ ├─ acknowledge_alert()                                 │  │
│  │ └─ get_active_alerts()                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│            ↓ (Output: Violations, Alerts)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  STORAGE SUBSYSTEM (Data Persistence)                   │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • Video Files (MP4, daily rotation)                     │  │
│  │ • Incident Database (In-memory, 1000 max)              │  │
│  │ • Alert History (JSON logs)                            │  │
│  │ • Analytics Data (Trends, metrics)                     │  │
│  │                                                          │  │
│  │ Components:                                             │  │
│  │ ├─ CCTVFrameRecorder (Video)                            │  │
│  │ ├─ CCTVSafetyAnalyzer (Incidents)                       │  │
│  │ └─ CCTVAlertEngine (Alerts)                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│            ↓ (Data retrieval)                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  OUTPUT SUBSYSTEM (User Interface)                      │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ Component: CCTVDashboard                                │  │
│  │ ├─ create_multi_camera_view()                           │  │
│  │ ├─ create_single_camera_view()                          │  │
│  │ ├─ create_analytics_dashboard()                         │  │
│  │ └─ draw_hud_info() [Real-time overlay]                 │  │
│  │                                                          │  │
│  │ Component: CCTVWebServer (Flask)                        │  │
│  │ ├─ GET  /                                               │  │
│  │ ├─ GET  /api/system/status                              │  │
│  │ ├─ GET  /api/camera/{id}/feed                           │  │
│  │ ├─ GET  /api/incidents/report                           │  │
│  │ ├─ GET  /api/alerts/active                              │  │
│  │ └─ POST /api/alerts/{id}/acknowledge                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│            ↓                                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  USER ACCESS                                            │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • Web Dashboard (http://localhost:5000)                 │  │
│  │ • REST API (JSON)                                       │  │
│  │ • Email/SMS Notifications                               │  │
│  │ • Incident Reports (Exportable)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## THREAD EXECUTION MODEL

```
Main Process
│
├─ Web Server Thread (Flask)
│  ├─ GET /
│  ├─ GET /api/system/status
│  ├─ GET /api/camera/{id}/feed (MJPEG)
│  └─ ... (other endpoints)
│
├─ Camera 1: Capture Thread
│  ├─ cv2.VideoCapture(0)
│  ├─ Read frames
│  └─ enqueue_frame_queue()
│
├─ Camera 1: Detection Thread
│  ├─ dequeue_frame_queue()
│  ├─ Perform detection
│  ├─ Check violations
│  ├─ Trigger alerts
│  └─ Save incident clips
│
├─ Camera 1: Recording Thread
│  ├─ dequeue_frame_queue()
│  ├─ cv2.VideoWriter()
│  ├─ Write MP4 file
│  └─ Manage disk space
│
├─ Camera 2: Capture Thread
│  ├─ cv2.VideoCapture(1)
│  ├─ Read frames
│  └─ enqueue_frame_queue()
│
├─ Camera 2: Detection Thread
│
├─ Camera 2: Recording Thread
│
└─ Alert Notification Threads (Future)
   ├─ Email Service
   ├─ SMS Service
   └─ Webhook Service

All threads run concurrently with thread-safe queues
```

---

## PROCESSING PIPELINE DETAILED

```
CAMERA INPUT (30 FPS)
        │
        ▼
┌───────────────────────────────────────┐
│ FRAME CAPTURE WORKER                  │
│ ├─ Connection: cv2.VideoCapture()    │
│ ├─ Read: ret, frame = cap.read()     │
│ ├─ Timing: Track FPS                 │
│ └─ Queue: frame_queue.put(frame)     │
│                                       │
│ Time: 0-50ms                         │
│ FPS Out: 30 FPS                      │
└───────────────────────────────────────┘
        │
        ▼
    Frame Queue
   (FIFO, max 30)
        │
        ▼
┌───────────────────────────────────────┐
│ PREPROCESSING                         │
│ ├─ Get: frame = queue.get(timeout=1) │
│ ├─ Convert: BGR → HSV                │
│ ├─ Resize: 1920x1080 → 640x480       │
│ ├─ Normalize: 0-255 → 0-1.0          │
│ └─ Metadata: Add timestamp           │
│                                       │
│ Time: 10-30ms                        │
└───────────────────────────────────────┘
        │
        ▼ (Three parallel detection branches)
        │
    ┌───┼───┬────────┐
    │   │   │        │
    ▼   ▼   ▼        ▼
   W1  W2  W3       W4
    │   │   │        │
WORKER HELMET PPE  ZONE
DETECT DETECT DETECT CHECK
    │   │   │        │
    └───┼───┴────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ DETECTION FUSION                      │
│ ├─ Combine results from all branches │
│ ├─ Calculate confidence score        │
│ ├─ Generate detection result dict    │
│ └─ {workers[], helmets[], violations[]}
│                                       │
│ Time: 100-300ms                      │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ VIOLATION ANALYSIS                    │
│ ├─ Check PPE compliance              │
│ ├─ Zone requirement validation       │
│ ├─ Employee history check            │
│ ├─ Escalation determination          │
│ └─ Generate violation records        │
│                                       │
│ Time: 50-100ms                       │
└───────────────────────────────────────┘
        │
    ┌───┴──────────┐
    │              │
    ▼              ▼
Has Violations?   No Violations?
    │ (YES)           │ (NO)
    │                  │
    ▼                  ▼
┌─────────────┐   ┌──────────────┐
│ TRIGGER     │   │ LOG NORMAL   │
│ ALERT       │   │ OPERATION    │
│             │   │              │
│ ├─ Type:    │   └──────────────┘
│ │  missing_ │
│ │  helmet   │
│ │           │
│ ├─ Severity:│
│ │  HIGH     │
│ │           │
│ ├─ Queue:   │
│ │  Alert    │
│ │  Engine   │
│ │           │
│ └─ Handler: │
│    Email,   │
│    SMS      │
└─────────────┘
    │
    └─→ Save Incident Clip
         (10 sec video + metadata)
    │
    └─→ Update Employee Score
         (-5 points for violation)
         │
         ▼ (Time: 10-50ms)
┌───────────────────────────────────────┐
│ STORAGE                               │
│ ├─ Video: MP4 file (continuous)      │
│ ├─ Incident: Database entry          │
│ ├─ Alert: Alert queue                │
│ └─ Analytics: Update counters        │
│                                       │
│ Time: 50-150ms                       │
└───────────────────────────────────────┘
        │
        ▼ (Total latency: ~400ms)
    OUTPUT READY FOR
    WEB DASHBOARD & API
```

---

## DATA FLOW - INCIDENT DETECTION EXAMPLE

```
Frame 1: Worker enters frame
│
├─ Detection: Face detected ✓
├─ Helmet detection result: YES (confidence: 92%)
├─ Violation: NONE
└─ Action: Log normal operation

Frame 2: Worker moves to hazmat zone
│
├─ Zone check: In ZONE_HAZMAT
├─ Zone requirement: Helmet + Gloves
├─ Detection: Helmet ✓, Gloves ✗
├─ Violation: MISSING_PPE (gloves)
│
├─ Alert Triggered:
│  ├─ Type: missing_ppe
│  ├─ Severity: HIGH
│  ├─ Worker: #ID_42
│  ├─ Zone: ZONE_HAZMAT
│  ├─ Time: 14:32:15
│  └─ Confidence: 85%
│
├─ Alert Engine Actions:
│  ├─ Create Alert ID: PPE_42_20260412_143215
│  ├─ Check Cooldown: No previous alert (5 min elapsed)
│  ├─ Call Handlers:
│  │  ├─ Email Handler: Send to supervisor@company.com
│  │  ├─ SMS Handler: Send to +1-555-0123
│  │  └─ Slack Handler: Post to #safety-alerts
│  │
│  └─ Store: Alert queue + database
│
├─ Database Updates:
│  ├─ Employee #42 violation count: +1
│  ├─ Employee #42 safety score: 95 → 90
│  ├─ Zone violation count: +1
│  └─ Incident logged with metadata
│
├─ Video Clip Saved:
│  ├─ File: recordings/incidents/20260412_143215/missing_ppe_HIGH.mp4
│  ├─ Duration: 10 seconds (frames -5 to +5)
│  ├─ Metadata: incidents/20260412_143215/metadata.json
│  │  {
│  │    "timestamp": "2026-04-12T14:32:15",
│  │    "camera_id": "CAM_001",
│  │    "incident_type": "missing_ppe",
│  │    "severity": "HIGH",
│  │    "employee_id": "EMP_42",
│  │    "zone_id": "ZONE_HAZMAT",
│  │    "ppe_missing": ["gloves"],
│  │    "duration_seconds": 10
│  │  }
│  └─ Accessible via Web UI for review

└─ Dashboard Updates:
   ├─ Active Alerts: +1
   ├─ Incident Count: +1
   ├─ Employee #42 Compliance: 80% → 75%
   ├─ Refresh Dashboard (real-time)
   └─ Notify Users via WebSocket
```

---

## SYSTEM STATE DIAGRAM

```
                    ┌─────────────┐
                    │    INIT     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  LOADING    │
   ┌────────────────▶ CONFIG      │◀────────────────┐
   │                └──────┬──────┘                │
   │                       │                      │
   │                       ▼                      │
   │            ┌─────────────────┐               │
   │            │ REGISTERING     │               │
   │            │ CAMERAS         │               │
   │            │ ZONES           │               │
   │            │ EMPLOYEES       │               │
   │            └──────┬──────────┘               │
   │                   │                         │
   │                   ▼                         │
   │            ┌─────────────────┐              │
   │            │ CAMERAS READY?  │              │
   │            └──┬──────────┬───┘              │
   │               │NO        │YES              │
   │               │          │                 │
   │         ERROR │          ▼                 │
   │         STATE │  ┌────────────────┐        │
   │      (retry)  └─▶│ START          │        │
   │                  │ MONITORING     │        │
   │                  └────────┬───────┘        │
   │                           │                │
   │                           ▼                │
   │                    ┌────────────────┐      │
   │                    │ MONITOR ACTIVE │      │
   │                    │                │      │
   │                    │ ├─ Capture     │      │
   │                    │ ├─ Detect      │      │
   │                    │ ├─ Record      │      │
   │                    │ ├─ Alert       │      │
   │                    │ └─ Serve       │      │
   │                    │                │      │
   │      Ctrl+C        └────────┬───────┘      │
   │        OR           Errors  │              │
   │    Config                   │              │
   │    Change                   ▼              │
   │        │          ┌────────────────┐       │
   │        │          │ SHUTDOWN       │       │
   │        │          │ GRACEFULLY     │       │
   │        │          │                │       │
   │        │          │ ├─ Stop threads│       │
   │        │          │ ├─ Close files │       │
   │        │          │ ├─ Save state  │       │
   │        │          │ └─ Log exit    │       │
   │        └──────────└────────┬───────┘       │
   └──────────────────────────────┘
                                  
States:
INIT       - Application starting
LOADING    - Configuration loading
REGISTERING- Setting up system
ACTIVE     - Running normally
SHUTDOWN   - Clean exit
ERROR      - Error recovery
```

---

## ALERT ESCALATION WORKFLOW

```
Violation Detected
       │
       ▼
┌──────────────────┐
│ Check Cooldown   │
│ for Alert Type   │
└────┬─────────┬──┘
     │         │
    YES        NO (Alert already recent)
     │         │
     │         ▼
     │    ┌─────────────────────────┐
     │    │ SKIP                    │
     │    │ (Cooldown not elapsed)  │
     │    └─────────────────────────┘
     │
     ▼
┌────────────────────────┐
│ Get Violation Count    │
│ for This Employee      │
└────┬─────────┬─────────┘
     │         │         │       │
  1st        2nd        3rd    4th+
  Bad        Bad        Bad     Bad
     │         │         │       │
     ▼         ▼         ▼       ▼
  EMAIL     EMAIL    PHONE    BLOCK
  alert  +   SMS    CALL +    ACCESS
            alert   SMS        +
                              EMAIL
     │         │         │       │
     └─────────┴─────────┴───────┘
             │
             ▼
       ┌──────────────┐
       │ LOG ALERT    │
       │ + METADATA   │
       └──────┬───────┘
              │
              ▼
       ┌──────────────────┐
       │ DISPLAY ON       │
       │ DASHBOARD        │
       │ (Real-time)      │
       └──────┬───────────┘
              │
              ▼
       ┌──────────────────┐
       │ USER             │
       │ ACKNOWLEDGE?     │
       └────┬──────────┬──┘
            │YES       │NO
            │          │
            ▼          │
       ┌──────────┐    │
       │ MARK     │    │
       │ REVIEWED │    │
       └──────────┘    │
                       │ (Auto after 24h)
                       │
                       ▼
                  ┌──────────────┐
                  │ ESCALATE     │
                  │ TO MANAGER   │
                  └──────────────┘
```

---

## SECURITY & DATA FLOW

```
User Request                  System
        │                      │
        ├─ HTTP Request ──────▶│
        │                      │ 1. Authentication
        │                      │    (username/password)
        │                      │
        │                      │ 2. Authorization
        │                      │    (role-based access)
        │                      │
        │◀─── Response ────────┤ 3. Query Database/System
        │     (JSON)           │    (secure data retrieval)
        │                      │
        │                      │ 4. Format Response
        │                      │    (remove sensitive data)
        │                      │
        │                      │ 5. Encrypt Response
        │                      │    (HTTPS/TLS)
        │                      │
        ├─ Display Data ────────
        │ (Dashboard)
        │
        ├─ User Action
        │ (Acknowledge Alert)
        │
        ├─ HTTP Request ──────▶│
        │ (POST)               │ 1. Re-authenticate
        │                      │
        │                      │ 2. Validate Request
        │                      │
        │                      │ 3. Update Database
        │                      │ (audit log entry)
        │                      │
        │◀─── Success ─────────┤
        │     Response
        │

Audit Trail:
└─ All access logged
   ├─ User ID
   ├─ Timestamp
   ├─ Action
   ├─ Result
   └─ IP Address
```

---

## STORAGE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│            STORAGE SUBSYSTEM ARCHITECTURE               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  DISK (File System)                                     │
│  ├─ recordings/ (Directory)                             │
│  │  ├─ CAM_001_2026-04-12.mp4 (1.8 GB)                 │
│  │  ├─ CAM_001_2026-04-11.mp4 (1.9 GB)                 │
│  │  ├─ CAM_002_2026-04-12.mp4 (2.1 GB)                 │
│  │  ├─ ... (Daily files)                               │
│  │  │                                                   │
│  │  └─ incidents/ (Directory)                           │
│  │     ├─ 20260412_143215/ (Incident folder)           │
│  │     │  ├─ missing_ppe_HIGH.mp4 (2.3 MB)             │
│  │     │  └─ metadata.json (1.2 KB)                    │
│  │     ├─ 20260412_142100/ (Incident folder)           │
│  │     │  ├─ missing_helmet_CRITICAL.mp4               │
│  │     │  └─ metadata.json                             │
│  │     └─ ... (All incidents with videos)              │
│  │                                                      │
│  ├─ logs/ (Directory)                                   │
│  │  ├─ cctv_system.log (Active log)                     │
│  │  └─ cctv_system.log.1 (Archive)                      │
│  │                                                      │
│  └─ config/ (Directory)                                 │
│     ├─ cctv_config.json (Configuration)                 │
│     └─ system_state.json (Current state)                │
│                                                          │
│  MEMORY (In-Process)                                    │
│  ├─ Incident Database                                   │
│  │  └─ Deque (max 1000 incidents)                       │
│  │     ├─ {incident 1}                                  │
│  │     ├─ {incident 2}                                  │
│  │     ├─ {incident 3}                                  │
│  │     └─ ... (most recent first)                       │
│  │                                                      │
│  ├─ Employee Database                                   │
│  │  └─ Dict: {emp_id → emp_data}                        │
│  │     ├─ EMP_001: {name, role, violations, score}      │
│  │     ├─ EMP_002: {name, role, violations, score}      │
│  │     └─ ... (all employees)                           │
│  │                                                      │
│  ├─ Zone Database                                       │
│  │  └─ Dict: {zone_id → zone_data}                      │
│  │     ├─ ZONE_MAIN: {type, coords, min_ppe}           │
│  │     ├─ ZONE_HAZMAT: {type, coords, min_ppe}         │
│  │     └─ ... (all zones)                               │
│  │                                                      │
│  ├─ Alert Queue                                         │
│  │  └─ Queue: {Alert 1}─▶{Alert 2}─▶{Alert 3}          │
│  │                                                      │
│  └─ Camera State                                        │
│     └─ Dict: {cam_id → {status, fps, frame_count}}      │
│                                                          │
│  DATABASE (Optional - Future)                           │
│  ├─ incidents table                                     │
│  ├─ employees table                                     │
│  ├─ alerts table                                        │
│  ├─ zones table                                         │
│  └─ audit_log table                                     │
│                                                          │
└─────────────────────────────────────────────────────────┘

Storage Hierarchy:
Fast  ─ Memory (In-process) 
      │  Deque, Dict - <1ms access
      │
Mid   ─ Disk (File system)
      │  JSON files - 10-100ms access
      │  Video files - Sequential read
      │
Slow  ─ Database (Future)
      │  SQL queries - 100-500ms
      │
Archive─ Cloud storage (Future)
        S3, Azure Blob - 1000+ ms
```

---

## DEPLOYMENT TOPOLOGY OPTIONS

```
OPTION 1: STANDALONE (Single Server)
┌────────────────────────────────────────┐
│         SERVER (Windows/Linux)         │
├────────────────────────────────────────┤
│                                        │
│  CCTV System Application               │
│  ├─ Python Runtime                     │
│  ├─ OpenCV                             │
│  ├─ Flask Server                       │
│  ├─ Storage (100GB+)                   │
│  └─ Logs                               │
│                                        │
└────────────────────────────────────────┘
    │          │            │
    ├─ Cameras (RTSP/USB)
    ├─ Users (Web Browser)
    └─ Notifications (Email/SMS)


OPTION 2: EDGE + CLOUD (Hybrid)
┌──────────────────────┐    ┌──────────────────────┐
│   EDGE SERVER        │    │    CLOUD SERVER      │
│  (Local Network)     │    │   (AWS/Azure/GCP)    │
├──────────────────────┤    ├──────────────────────┤
│                      │    │                      │
│ Real-time Detection  │    │ Analytics            │
│ Video Recording      │────▶ Historical Data     │
│ Local Alerts         │◀──── Reporting          │
│                      │    │ Backup               │
└──────────────────────┘    └──────────────────────┘
    │
    ├─ Cameras


OPTION 3: DISTRIBUTED (Multi-Region)
Region 1:                Region 2:              Region 3:
┌──────────────┐        ┌──────────────┐      ┌──────────────┐
│ CCTV Server  │        │ CCTV Server  │      │ CCTV Server  │
│ (Local)      │        │ (Local)      │      │ (Local)      │
├──────────────┤        ├──────────────┤      ├──────────────┤
│ 4 Cameras    │        │ 4 Cameras    │      │ 4 Cameras    │
│              │        │              │      │              │
└──────────────┘        └──────────────┘      └──────────────┘
       │                       │                      │
       └───────────────┬───────┴──────────────────────┘
                       │
                       ▼
           ┌────────────────────────┐
           │   CENTRAL HUB          │
           │  (Cloud Platform)      │
           ├────────────────────────┤
           │ Unified Dashboard      │
           │ Global Analytics       │
           │ Backup Storage         │
           │ Notifications          │
           └────────────────────────┘
```

---

## MODULE INTERACTION DIAGRAM

```
                     ┌─────────────────────┐
                     │  start_cctv.py      │
                     │  (Entry Point)      │
                     └──────────┬──────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
         ┌────────────┐  ┌────────────┐  ┌──────────────┐
         │ Load       │  │ Register   │  │ Initialize   │
         │ Config     │  │ Cameras    │  │ Analytics    │
         │            │  │ Zones      │  │              │
         │            │  │ Employees  │  │              │
         └────────────┘  └────────────┘  └──────────────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │ProfessionalCCTVSystem│
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
         ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
         │   Recorder  │ │  Analyzer   │ │ AlertEngine  │
         ├─────────────┤ ├─────────────┤ ├──────────────┤
         │ Recording   │ │ Detection   │ │ Trigger      │
         │ Workers     │ │ Analysis    │ │ Acknowledge  │
         │ Disk Mgmt   │ │ Incidents   │ │ Handlers     │
         └──────┬──────┘ └──────┬──────┘ └──────┬───────┘
                │               │               │
         Videos to Disk    Alerts triggered   Notifications
                │               │               │
                └───────────────┼───────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │RealtimeCCTVMonitor  │
                    │ (Processing Engine) │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
         ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
         │  Capture    │ │ Detection   │ │ Dashboard    │
         │  Workers    │ │ Workers     │ │              │
         ├─────────────┤ ├─────────────┤ ├──────────────┤
         │ Frame Queue │ │ Analysis    │ │ HUD Overlay  │
         │ FPS Calc.   │ │ Violations  │ │ Multi-cam    │
         └─────────────┘ └─────────────┘ └──────┬───────┘
                │               │               │
           cv2.VideoCapture  Detection Results  Visual Output
                │               │               │
                └───────────────┼───────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │  CCTVWebServer      │
                    │  (Flask)            │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
         ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
         │   HTTP      │ │   MJPEG     │ │   JSON       │
         │  Dashboard  │ │   Stream    │ │    API       │
         │             │ │             │ │              │
         │ /           │ │/camera/{id} │ │/api/status   │
         │/api/status  │ │/feed        │ │/api/incidents│
         └─────────────┘ └─────────────┘ └──────────────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                                ▼
                          USER INTERFACE
                       (Web Browser / API Client)
```

---

## QUICK ARCHITECTURE REFERENCE

```
┌──────────────────────────────────────────────────┐
│           ARCHITECTURE AT A GLANCE               │
├──────────────────────────────────────────────────┤
│                                                  │
│ INPUT LAYER:                                    │
│ • Multi-threaded camera capture                 │
│ • Frame queue buffering                         │
│ • 30 FPS input, 15 FPS output                   │
│                                                  │
│ PROCESSING LAYER:                               │
│ • Real-time detection (4 parallel branches)      │
│ • 400ms average latency                         │
│ • Multi-threaded per-camera                     │
│                                                  │
│ STORAGE LAYER:                                  │
│ • Continuous MP4 recording                      │
│ • In-memory incident database                   │
│ • Daily file rotation                           │
│ • Automatic cleanup (100GB max)                 │
│                                                  │
│ OUTPUT LAYER:                                   │
│ • Web dashboard (Flask)                         │
│ • REST API (JSON)                               │
│ • Real-time streams (MJPEG)                    │
│ • Analytics & reports                           │
│                                                  │
│ THREADING MODEL:                                │
│ • 1 HTTP server thread                          │
│ • 3 threads per camera (capture/detect/record)  │
│ • Total: 3N+1 threads (N=cameras)               │
│ • Non-blocking queues for communication         │
│                                                  │
│ DATA FLOW:                                      │
│ Camera → Queue → Detect → Analyze → Store       │
│            ↓         ↓        ↓       ↓          │
│          Video    Violations  Alerts  DB         │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

This document contains all the architectural details needed for PowerPoint slides:
- Use ASCII diagrams as reference for creating graphics
- Convert tables into visual charts
- Create flow diagrams from the workflow sections
- Use the component hierarchy for system overview slides
- Show threading model for technical deep-dive
- Present performance metrics in charts/graphs
