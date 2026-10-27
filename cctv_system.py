#!/usr/bin/env python3
"""
Professional CCTV Safety Detection System
Production-grade real-time monitoring for employee safety with continuous recording
"""

import cv2
import numpy as np
import threading
import logging
import queue
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional
import os
import time

logger = logging.getLogger(__name__)

class CCTVFrameRecorder:
    """Professional video recording system with circular buffer management"""
    
    def __init__(self, output_dir="recordings", max_disk_usage_gb=100):
        """
        Initialize CCTV recorder
        
        Args:
            output_dir: Directory for recording storage
            max_disk_usage_gb: Maximum disk space for recordings
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_disk_usage = max_disk_usage_gb * 1024 * 1024 * 1024  # Convert to bytes
        self.recording_threads = {}
        self.recording_queues = {}
        self.is_recording = False
        
        # 24/7 recording configuration
        self.fps = 15  # Lower FPS for storage efficiency
        self.frame_width = 1280
        self.frame_height = 720
        self.codec = cv2.VideoWriter_fourcc(*'mp4v')
        
        logger.info("CCTV Frame Recorder initialized")
    
    def start_continuous_recording(self, camera_id: str, frame_queue: queue.Queue):
        """Start continuous 24/7 recording for a camera"""
        thread = threading.Thread(
            target=self._recording_worker,
            args=(camera_id, frame_queue),
            daemon=True
        )
        thread.start()
        self.recording_threads[camera_id] = thread
        self.recording_queues[camera_id] = frame_queue
        self.is_recording = True
        logger.info(f"Started 24/7 recording for camera: {camera_id}")
    
    def _recording_worker(self, camera_id: str, frame_queue: queue.Queue):
        """Worker thread for continuous recording"""
        current_file = None
        current_writer = None
        current_date = None
        
        while self.is_recording:
            try:
                # Get frame with timeout
                frame = frame_queue.get(timeout=1)
                
                # Create new file if date changed (daily rotation)
                today = datetime.now().date()
                if current_date != today:
                    if current_writer:
                        current_writer.release()
                    
                    current_date = today
                    filename = self.output_dir / f"{camera_id}_{today.isoformat()}.mp4"
                    current_writer = cv2.VideoWriter(
                        str(filename),
                        self.codec,
                        self.fps,
                        (self.frame_width, self.frame_height)
                    )
                    logger.info(f"Started new recording file: {filename}")
                
                # Write frame
                if current_writer:
                    resized_frame = cv2.resize(frame, (self.frame_width, self.frame_height))
                    current_writer.write(resized_frame)
                
                # Check disk usage and cleanup old files if needed
                self._manage_disk_space()
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Recording error for {camera_id}: {e}")
        
        if current_writer:
            current_writer.release()
    
    def _manage_disk_space(self):
        """Manage disk space by removing old recordings"""
        total_size = 0
        files_by_time = []
        
        for file in self.output_dir.glob("*.mp4"):
            size = file.stat().st_size
            total_size += size
            files_by_time.append((file.stat().st_mtime, file))
        
        # Remove old files if over limit
        if total_size > self.max_disk_usage:
            files_by_time.sort()
            for _, old_file in files_by_time:
                if total_size <= self.max_disk_usage:
                    break
                old_file.unlink()
                total_size -= old_file.stat().st_size
                logger.warning(f"Deleted old recording: {old_file.name}")
    
    def save_incident_clip(self, camera_id: str, frames: List, incident_type: str, severity: str):
        """Save incident video clip with metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clip_dir = self.output_dir / "incidents" / timestamp
        clip_dir.mkdir(parents=True, exist_ok=True)
        
        # Save video clip
        clip_file = clip_dir / f"{incident_type}_{severity}.mp4"
        writer = cv2.VideoWriter(
            str(clip_file),
            self.codec,
            self.fps,
            (self.frame_width, self.frame_height)
        )
        
        for frame in frames:
            resized_frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            writer.write(resized_frame)
        writer.release()
        
        # Save metadata
        metadata_file = clip_dir / "metadata.json"
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "camera_id": camera_id,
            "incident_type": incident_type,
            "severity": severity,
            "duration_seconds": len(frames) / self.fps,
            "video_file": str(clip_file)
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved incident clip: {clip_file}")
        return str(clip_file)


class CCTVSafetyAnalyzer:
    """Advanced safety analysis with zone management and employee tracking"""
    
    def __init__(self, frame_width=1280, frame_height=720):
        """Initialize safety analyzer"""
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.zones = {}  # Safety zones configuration
        self.employee_db = {}  # Employee safety profiles
        self.incident_history = deque(maxlen=1000)  # Keep last 1000 incidents
        self.alert_triggers = defaultdict(lambda: {"last_alert": None, "count": 0})
        
        # Detection history for trend analysis
        self.detection_trends = defaultdict(lambda: deque(maxlen=300))  # 5 min @ 1 FPS
        
        logger.info("CCTV Safety Analyzer initialized")
    
    def register_safety_zone(self, zone_id: str, zone_type: str, coordinates: List[Tuple], 
                            min_ppe: Dict = None, restricted: bool = False):
        """
        Register a safety zone (high-risk area, hazard zone, etc.)
        
        Args:
            zone_id: Unique zone identifier
            zone_type: 'high_risk', 'hazard', 'equipment', 'confined_space'
            coordinates: List of (x, y) points defining the zone
            min_ppe: Minimum PPE required in this zone
            restricted: Whether access is restricted
        """
        self.zones[zone_id] = {
            "type": zone_type,
            "coordinates": np.array(coordinates, dtype=np.int32),
            "min_ppe": min_ppe or {},
            "restricted": restricted,
            "created_at": datetime.now(),
            "violations": 0
        }
        logger.info(f"Registered safety zone: {zone_id} ({zone_type})")
    
    def register_employee(self, emp_id: str, name: str, role: str, required_ppe: Dict,
                         face_encoding: Optional[np.ndarray] = None):
        """Register employee with safety profile"""
        self.employee_db[emp_id] = {
            "name": name,
            "role": role,
            "required_ppe": required_ppe,
            "face_encoding": face_encoding,
            "last_seen": None,
            "violation_count": 0,
            "safety_score": 95  # Out of 100
        }
        logger.info(f"Registered employee: {name} ({role})")
    
    def check_zone_violation(self, detections: Dict, frame: np.ndarray) -> List[Dict]:
        """Check if detected people violate zone restrictions"""
        violations = []
        
        for zone_id, zone_config in self.zones.items():
            if zone_config["restricted"]:
                # Check if anyone is in restricted zone without authorization
                for detection in detections.get("workers", []):
                    if self._point_in_polygon(detection["center"], zone_config["coordinates"]):
                        violations.append({
                            "type": "unauthorized_access",
                            "zone_id": zone_id,
                            "zone_type": zone_config["type"],
                            "detection": detection,
                            "severity": "high",
                            "timestamp": datetime.now()
                        })
            
            # Check PPE compliance in zone
            for detection in detections.get("workers", []):
                if self._point_in_polygon(detection["center"], zone_config["coordinates"]):
                    ppe_violations = self._check_ppe_compliance(detection, zone_config)
                    violations.extend(ppe_violations)
        
        return violations
    
    def _point_in_polygon(self, point: Tuple, polygon: np.ndarray) -> bool:
        """Check if point is inside polygon"""
        x, y = point
        return cv2.pointPolygonTest(polygon, (float(x), float(y)), False) >= 0
    
    def _check_ppe_compliance(self, detection: Dict, zone_config: Dict) -> List[Dict]:
        """Check PPE compliance for a detection in a zone"""
        violations = []
        required_ppe = zone_config["min_ppe"]
        
        for ppe_type, required in required_ppe.items():
            detected = detection.get("ppe", {}).get(ppe_type, False)
            
            if required and not detected:
                violations.append({
                    "type": "missing_ppe",
                    "ppe_type": ppe_type,
                    "zone_id": zone_config.get("id"),
                    "detection": detection,
                    "severity": "critical",
                    "timestamp": datetime.now()
                })
        
        return violations
    
    def log_incident(self, incident: Dict):
        """Log incident for analytics and reporting"""
        incident["logged_at"] = datetime.now()
        self.incident_history.append(incident)
        
        # Update employee violation count
        if "employee_id" in incident:
            emp_id = incident["employee_id"]
            if emp_id in self.employee_db:
                self.employee_db[emp_id]["violation_count"] += 1
                # Reduce safety score
                self.employee_db[emp_id]["safety_score"] = max(0, 
                    self.employee_db[emp_id]["safety_score"] - 5)
    
    def get_incident_report(self, hours=24) -> Dict:
        """Generate incident report for time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_incidents = [
            inc for inc in self.incident_history 
            if inc.get("logged_at", datetime.now()) > cutoff_time
        ]
        
        report = {
            "period_hours": hours,
            "total_incidents": len(recent_incidents),
            "critical_incidents": len([i for i in recent_incidents if i["severity"] == "critical"]),
            "high_incidents": len([i for i in recent_incidents if i["severity"] == "high"]),
            "incidents_by_type": defaultdict(int),
            "top_violators": [],
            "generated_at": datetime.now().isoformat()
        }
        
        # Count by type
        for incident in recent_incidents:
            report["incidents_by_type"][incident["type"]] += 1
        
        # Find top violators
        violator_counts = defaultdict(int)
        for incident in recent_incidents:
            if "employee_id" in incident:
                violator_counts[incident["employee_id"]] += 1
        
        report["top_violators"] = sorted(violator_counts.items(), key=lambda x: x[1], reverse=True)
        
        return report


class CCTVAlertEngine:
    """Alert management with priority-based escalation"""
    
    def __init__(self, notification_service=None):
        """Initialize alert engine"""
        self.notification_service = notification_service
        self.active_alerts = {}
        self.alert_queue = queue.Queue()
        self.alert_handlers = defaultdict(list)
        self.cooldown_periods = {
            "low": 300,      # 5 minutes
            "medium": 180,   # 3 minutes
            "high": 60,      # 1 minute
            "critical": 10   # 10 seconds
        }
        
        logger.info("CCTV Alert Engine initialized")
    
    def register_alert_handler(self, alert_type: str, handler_func):
        """Register handler for specific alert type"""
        self.alert_handlers[alert_type].append(handler_func)
    
    def trigger_alert(self, alert_type: str, severity: str, details: Dict):
        """Trigger a new alert"""
        alert_id = f"{alert_type}_{datetime.now().isoformat()}"
        
        alert = {
            "id": alert_id,
            "type": alert_type,
            "severity": severity,
            "details": details,
            "created_at": datetime.now(),
            "acknowledged": False,
            "acknowledged_by": None,
            "acknowledged_at": None
        }
        
        self.active_alerts[alert_id] = alert
        self.alert_queue.put(alert)
        
        # Call registered handlers
        for handler in self.alert_handlers[alert_type]:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
        
        logger.warning(f"Alert triggered: {alert_type} ({severity}) - {alert_id}")
        return alert_id
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Mark alert as acknowledged"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id]["acknowledged"] = True
            self.active_alerts[alert_id]["acknowledged_by"] = acknowledged_by
            self.active_alerts[alert_id]["acknowledged_at"] = datetime.now()
            logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
    
    def get_active_alerts(self, severity_filter: Optional[str] = None) -> List[Dict]:
        """Get list of active alerts"""
        alerts = list(self.active_alerts.values())
        
        if severity_filter:
            alerts = [a for a in alerts if a["severity"] == severity_filter and not a["acknowledged"]]
        
        return sorted(alerts, key=lambda x: x["created_at"], reverse=True)


class ProfessionalCCTVSystem:
    """Main professional CCTV system coordinator"""
    
    def __init__(self, system_name="CCTV Safety Monitoring System"):
        """Initialize professional CCTV system"""
        self.system_name = system_name
        self.recorder = CCTVFrameRecorder()
        self.analyzer = CCTVSafetyAnalyzer()
        self.alert_engine = CCTVAlertEngine()
        self.cameras = {}  # Active cameras
        self.system_status = "initialized"
        self.start_time = datetime.now()
        
        logger.info(f"Professional CCTV System '{system_name}' initialized")
    
    def register_camera(self, camera_id: str, source: str, location: str, 
                       zones: List[str] = None) -> bool:
        """Register a camera for monitoring"""
        try:
            self.cameras[camera_id] = {
                "source": source,
                "location": location,
                "zones": zones or [],
                "status": "offline",
                "frames_processed": 0,
                "detections": 0,
                "alerts": 0,
                "start_time": None
            }
            logger.info(f"Registered camera: {camera_id} at {location}")
            return True
        except Exception as e:
            logger.error(f"Failed to register camera {camera_id}: {e}")
            return False
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        uptime = datetime.now() - self.start_time
        
        return {
            "system_name": self.system_name,
            "status": self.system_status,
            "uptime_seconds": uptime.total_seconds(),
            "active_cameras": len([c for c in self.cameras.values() if c["status"] == "online"]),
            "total_cameras": len(self.cameras),
            "total_incidents": len(self.analyzer.incident_history),
            "active_alerts": len([a for a in self.alert_engine.active_alerts.values() if not a["acknowledged"]]),
            "critical_alerts": len([a for a in self.alert_engine.get_active_alerts() if a["severity"] == "critical"]),
            "employees_registered": len(self.analyzer.employee_db),
            "safety_zones": len(self.analyzer.zones),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_camera_status(self, camera_id: str) -> Optional[Dict]:
        """Get status of specific camera"""
        if camera_id not in self.cameras:
            return None
        
        camera = self.cameras[camera_id]
        return {
            "camera_id": camera_id,
            "location": camera["location"],
            "status": camera["status"],
            "frames_processed": camera["frames_processed"],
            "detections": camera["detections"],
            "alerts": camera["alerts"],
            "uptime": camera["start_time"]
        }


# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    # Example usage
    system = ProfessionalCCTVSystem("Warehouse Safety CCTV")
    
    # Register cameras
    system.register_camera("CAM_001", 0, "Main Entrance")
    system.register_camera("CAM_002", 1, "Warehouse Floor")
    
    # Register safety zones
    system.analyzer.register_safety_zone(
        "ZONE_HAZMAT",
        "high_risk",
        [(100, 100), (400, 100), (400, 300), (100, 300)],
        min_ppe={"helmet": True, "gloves": True, "vest": True},
        restricted=False
    )
    
    # Register employees
    system.analyzer.register_employee(
        "EMP001",
        "John Doe",
        "Warehouse Operator",
        required_ppe={"helmet": True, "gloves": True}
    )
    
    print("\n" + "="*60)
    print(f"{system.system_name}")
    print("="*60)
    print(json.dumps(system.get_system_status(), indent=2))
