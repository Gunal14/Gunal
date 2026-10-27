#!/usr/bin/env python3
"""
Real-Time CCTV Monitoring Engine
Integrates detection, recording, alerts, and dashboard for 24/7 safety monitoring
"""

import cv2
import numpy as np
import threading
import queue
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from collections import deque, defaultdict
import time

from cctv_system import ProfessionalCCTVSystem, CCTVFrameRecorder
from cctv_dashboard import CCTVDashboard

logger = logging.getLogger(__name__)

class RealtimeCCTVMonitor:
    """Real-time CCTV monitoring with all integrated features"""
    
    def __init__(self, system: ProfessionalCCTVSystem):
        """
        Initialize real-time monitor
        
        Args:
            system: ProfessionalCCTVSystem instance
        """
        self.system = system
        self.dashboard = CCTVDashboard()
        
        # Thread management
        self.monitor_threads = {}
        self.is_running = False
        
        # Frame queues for each camera
        self.frame_queues = {}
        self.detection_results = {}
        
        # Performance monitoring
        self.fps_counters = defaultdict(lambda: deque(maxlen=30))
        self.detection_metrics = defaultdict(dict)
        
        logger.info("Real-time CCTV Monitor initialized")
    
    def start_monitoring(self, camera_id: str, source: str):
        """Start monitoring a camera"""
        if camera_id not in self.frame_queues:
            self.frame_queues[camera_id] = queue.Queue(maxsize=30)
        
        # Check if source is valid
        cap = cv2.VideoCapture(source if isinstance(source, str) else int(source))
        if not cap.isOpened():
            logger.error(f"Cannot open camera: {source}")
            return False
        
        cap.release()
        
        # Start capture thread
        capture_thread = threading.Thread(
            target=self._capture_worker,
            args=(camera_id, source),
            daemon=True,
            name=f"Capture-{camera_id}"
        )
        capture_thread.start()
        
        # Start detection thread
        detection_thread = threading.Thread(
            target=self._detection_worker,
            args=(camera_id,),
            daemon=True,
            name=f"Detection-{camera_id}"
        )
        detection_thread.start()
        
        self.monitor_threads[camera_id] = {
            "capture": capture_thread,
            "detection": detection_thread
        }
        
        self.system.cameras[camera_id]["status"] = "online"
        self.system.cameras[camera_id]["start_time"] = datetime.now()
        
        logger.info(f"Started monitoring camera: {camera_id}")
        return True
    
    def _capture_worker(self, camera_id: str, source: str):
        """Capture frames from camera"""
        cap = cv2.VideoCapture(source if isinstance(source, str) else int(source))
        
        frame_count = 0
        while self.is_running or not self.frame_queues[camera_id].empty():
            ret, frame = cap.read()
            
            if not ret:
                logger.warning(f"Frame capture failed for {camera_id}")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            
            # Calculate FPS
            self.fps_counters[camera_id].append(datetime.now())
            if len(self.fps_counters[camera_id]) > 1:
                time_diff = (self.fps_counters[camera_id][-1] - 
                           self.fps_counters[camera_id][0]).total_seconds()
                if time_diff > 0:
                    fps = len(self.fps_counters[camera_id]) / time_diff
                    self.detection_metrics[camera_id]["fps"] = fps
            
            # Put frame in queue
            try:
                self.frame_queues[camera_id].put_nowait(frame)
            except queue.Full:
                # Skip frame if queue is full
                pass
            
            self.system.cameras[camera_id]["frames_processed"] = frame_count
        
        cap.release()
        logger.info(f"Capture worker stopped for {camera_id}")
    
    def _detection_worker(self, camera_id: str):
        """Perform detections on frames"""
        frame_queue = self.frame_queues[camera_id]
        incident_frames = deque(maxlen=90)  # 6 seconds @ 15 FPS
        
        while self.is_running or not frame_queue.empty():
            try:
                frame = frame_queue.get(timeout=1)
                
                # Perform detection
                detections = self._perform_detection(frame)
                
                # Store results
                self.detection_results[camera_id] = {
                    "frame": frame,
                    "detections": detections,
                    "timestamp": datetime.now()
                }
                
                # Check for violations and alerts
                violations = self._check_violations(camera_id, detections, frame)
                
                if violations:
                    for violation in violations:
                        self.system.analyzer.log_incident(violation)
                        self.system.cameras[camera_id]["alerts"] += 1
                        incident_frames.append(frame.copy())
                        
                        # Trigger alert
                        alert_id = self.system.alert_engine.trigger_alert(
                            violation["type"],
                            violation["severity"],
                            violation
                        )
                        
                        # Save incident clip if critical
                        if violation["severity"] == "critical":
                            self.system.recorder.save_incident_clip(
                                camera_id,
                                list(incident_frames),
                                violation["type"],
                                violation["severity"]
                            )
                
                # Record frame (24/7)
                recording_queue = self.frame_queues.get(f"{camera_id}_recording")
                if recording_queue:
                    try:
                        recording_queue.put_nowait(frame)
                    except queue.Full:
                        pass
                
                self.system.cameras[camera_id]["detections"] += 1
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Detection worker error for {camera_id}: {e}")
        
        logger.info(f"Detection worker stopped for {camera_id}")
    
    def _perform_detection(self, frame: np.ndarray) -> Dict:
        """Perform actual detection on frame"""
        detections = {
            "workers": [],
            "helmets": [],
            "ppe": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Simple face detection as placeholder
            # In production, use YOLO or other advanced models
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                detection = {
                    "box": (x, y, w, h),
                    "center": (x + w//2, y + h//2),
                    "confidence": 0.85,
                    "helmet_detected": np.random.rand() > 0.3  # Placeholder
                }
                detections["workers"].append(detection)
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
        
        return detections
    
    def _check_violations(self, camera_id: str, detections: Dict, 
                         frame: np.ndarray) -> List[Dict]:
        """Check for safety violations"""
        violations = []
        
        # Check helmet compliance
        workers_without_helmet = [d for d in detections.get("workers", []) 
                                 if not d.get("helmet_detected")]
        
        if workers_without_helmet:
            for worker in workers_without_helmet:
                violations.append({
                    "type": "missing_helmet",
                    "severity": "high",
                    "camera_id": camera_id,
                    "worker": worker,
                    "timestamp": datetime.now(),
                    "description": "Worker detected without safety helmet"
                })
        
        # Check zone violations
        zone_violations = self.system.analyzer.check_zone_violation(detections, frame)
        violations.extend(zone_violations)
        
        return violations
    
    def get_live_feed(self, camera_id: str) -> Optional[np.ndarray]:
        """Get current live frame for a camera"""
        if camera_id in self.detection_results:
            return self.detection_results[camera_id]["frame"]
        return None
    
    def get_dashboard_view(self) -> np.ndarray:
        """Get multi-camera dashboard view"""
        camera_feeds = {}
        for cam_id in self.system.cameras.keys():
            camera_feeds[cam_id] = self.get_live_feed(cam_id)
        
        return self.dashboard.create_multi_camera_view(
            camera_feeds,
            self.system.get_system_status()
        )
    
    def get_detailed_view(self, camera_id: str) -> Optional[np.ndarray]:
        """Get detailed view for single camera"""
        if camera_id not in self.detection_results:
            return None
        
        result = self.detection_results[camera_id]
        detections = result["detections"]
        alerts = self.system.alert_engine.get_active_alerts()
        
        return self.dashboard.create_single_camera_view(
            result["frame"],
            camera_id,
            detections,
            alerts
        )
    
    def start(self):
        """Start all monitoring"""
        self.is_running = True
        
        # Start monitoring for each registered camera
        for camera_id, camera_config in self.system.cameras.items():
            self.start_monitoring(camera_id, camera_config["source"])
            
            # Start recording thread
            recording_queue = queue.Queue(maxsize=30)
            self.frame_queues[f"{camera_id}_recording"] = recording_queue
            self.system.recorder.start_continuous_recording(camera_id, recording_queue)
        
        logger.info("CCTV Monitoring system started")
    
    def stop(self):
        """Stop all monitoring"""
        self.is_running = False
        
        # Wait for threads to finish
        for camera_id, threads in self.monitor_threads.items():
            for thread in threads.values():
                thread.join(timeout=5)
        
        logger.info("CCTV Monitoring system stopped")
    
    def get_performance_report(self) -> Dict:
        """Get system performance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "cameras": {}
        }
        
        for camera_id in self.system.cameras.keys():
            report["cameras"][camera_id] = {
                "fps": self.detection_metrics.get(camera_id, {}).get("fps", 0),
                "frames_processed": self.system.cameras[camera_id]["frames_processed"],
                "detections": self.system.cameras[camera_id]["detections"],
                "alerts": self.system.cameras[camera_id]["alerts"],
            }
        
        return report


class CCTVWebServer:
    """Web server for CCTV dashboard and API"""
    
    def __init__(self, monitor: RealtimeCCTVMonitor, port=5000):
        """Initialize web server"""
        self.monitor = monitor
        self.port = port
        self.app = None
        
        self._setup_endpoints()
    
    def _setup_endpoints(self):
        """Setup Flask endpoints"""
        from flask import Flask, Response, jsonify
        import json
        
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            """Dashboard page"""
            return '''
            <html>
                <head>
                    <title>CCTV Safety Monitoring System</title>
                    <style>
                        body { font-family: Arial; background: #1a1a1a; color: #fff; margin: 0; }
                        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
                        .header { text-align: center; margin-bottom: 30px; }
                        h1 { color: #00c864; }
                        .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
                        .card { background: #2a2a2a; border: 1px solid #444; padding: 20px; border-radius: 8px; }
                        .camera-feed { background: #000; border: 2px solid #00c864; padding: 10px; text-align: center; }
                        .status-good { color: #00c864; }
                        .status-warning { color: #ff6b00; }
                        .status-critical { color: #ff0000; }
                        button { background: #00c864; color: black; border: none; padding: 10px 20px; 
                                border-radius: 5px; cursor: pointer; font-weight: bold; }
                        button:hover { background: #00a850; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🎥 CCTV Safety Monitoring System</h1>
                            <p>Professional Employee Safety Detection & Monitoring</p>
                        </div>
                        
                        <div class="dashboard">
                            <div class="card">
                                <h2>System Status</h2>
                                <div id="status"></div>
                                <button onclick="updateStatus()">Refresh</button>
                            </div>
                            
                            <div class="card">
                                <h2>Active Cameras</h2>
                                <div id="cameras"></div>
                            </div>
                            
                            <div class="card">
                                <h2>Recent Incidents</h2>
                                <div id="incidents"></div>
                            </div>
                            
                            <div class="card">
                                <h2>Active Alerts</h2>
                                <div id="alerts"></div>
                            </div>
                        </div>
                    </div>
                    
                    <script>
                        function updateStatus() {
                            fetch('/api/system/status')
                                .then(r => r.json())
                                .then(data => {
                                    document.getElementById('status').innerHTML = `
                                        <p><strong>System:</strong> <span class="status-good">${data.status}</span></p>
                                        <p><strong>Uptime:</strong> ${Math.floor(data.uptime_seconds / 60)} minutes</p>
                                        <p><strong>Active Cameras:</strong> ${data.active_cameras}/${data.total_cameras}</p>
                                        <p><strong>Total Incidents:</strong> ${data.total_incidents}</p>
                                        <p><strong>Critical Alerts:</strong> <span class="status-critical">${data.critical_alerts}</span></p>
                                    `;
                                });
                        }
                        
                        updateStatus();
                        setInterval(updateStatus, 5000);
                    </script>
                </body>
            </html>
            '''
        
        @app.route('/api/system/status')
        def get_status():
            """Get system status"""
            return jsonify(self.monitor.system.get_system_status())
        
        @app.route('/api/camera/<camera_id>/feed')
        def get_camera_feed(camera_id):
            """Stream camera feed"""
            def generate():
                while True:
                    frame = self.monitor.get_live_feed(camera_id)
                    if frame is None:
                        continue
                    
                    ret, buffer = cv2.imencode('.jpg', frame)
                    yield (b'--frame\r\n'
                          b'Content-Type: image/jpeg\r\n'
                          b'Content-Length: ' + str(len(buffer)).encode() + b'\r\n\r\n'
                          + buffer.tobytes() + b'\r\n')
                    
                    time.sleep(0.033)  # ~30 FPS
            
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
        @app.route('/api/incidents/report')
        def get_incidents():
            """Get incident report"""
            report = self.monitor.system.analyzer.get_incident_report(hours=24)
            return jsonify(report)
        
        @app.route('/api/alerts/active')
        def get_alerts():
            """Get active alerts"""
            alerts = self.monitor.system.alert_engine.get_active_alerts()
            return jsonify(alerts)
        
        self.app = app
    
    def run(self, debug=False):
        """Run web server"""
        if self.app:
            self.app.run(host='0.0.0.0', port=self.port, debug=debug)


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Professional CCTV Safety Monitoring System")
    parser.add_argument('--web', action='store_true', help='Start web server')
    parser.add_argument('--port', type=int, default=5000, help='Web server port')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    
    args = parser.parse_args()
    
    # Initialize system
    system = ProfessionalCCTVSystem("Employee Safety CCTV")
    
    # Register cameras
    system.register_camera("CAM_001", 0, "Main Entrance")
    
    # Register safety zones
    system.analyzer.register_safety_zone(
        "ZONE_MAIN",
        "high_risk",
        [(100, 100), (400, 100), (400, 600), (100, 600)],
        min_ppe={"helmet": True},
        restricted=False
    )
    
    # Register employees
    system.analyzer.register_employee("EMP001", "John Doe", "Operator", {"helmet": True})
    
    # Start monitoring
    monitor = RealtimeCCTVMonitor(system)
    monitor.start()
    
    print("\n" + "="*60)
    print("PROFESSIONAL CCTV SAFETY MONITORING SYSTEM")
    print("="*60)
    print(f"System Status: {system.get_system_status()['status']}")
    print(f"Cameras: {system.get_system_status()['active_cameras']}/{system.get_system_status()['total_cameras']}")
    print("="*60 + "\n")
    
    try:
        if args.web:
            print(f"Starting web server on port {args.port}...")
            web_server = CCTVWebServer(monitor, port=args.port)
            web_server.run(debug=args.test)
        else:
            print("Monitoring running. Press Ctrl+C to stop...")
            while True:
                time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        monitor.stop()
