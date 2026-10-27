"""
Real-Time Safety Monitoring with OpenCV
Continuously captures frames and triggers safety alerts
"""

import cv2
import numpy as np
import sys
import os
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class RealtimeSafetyMonitor:
    """Real-time helmet and safety monitoring"""
    
    def __init__(self, camera_source=0, enable_alerts=True):
        """
        Initialize real-time monitor
        
        Args:
            camera_source: 0 for webcam, or video file path/URL
            enable_alerts: Whether to send emergency alerts
        """
        self.camera_source = camera_source
        self.enable_alerts = enable_alerts
        self.is_running = False
        self.frame = None
        self.detection_results = {}
        
        # Initialize detector
        from safety_detection import SafetyDetector
        self.detector = SafetyDetector()
        
        # Alert tracking to prevent spam
        self.alert_history = defaultdict(lambda: datetime.min)
        self.alert_cooldown = 5  # seconds
        
        # Performance tracking
        self.fps_times = []
        self.frame_count = 0
        
    def process_frame(self, frame):
        """Process single frame with detection and alerting"""
        # Run detection
        results = self.detector.detect(frame)
        self.detection_results = results
        
        # Check for violations and trigger alerts
        violations = results.get('violations', [])
        if violations:
            self.handle_violations(violations, results, frame)
        
        return results
    
    def handle_violations(self, violations, results, frame):
        """Handle detected safety violations"""
        for violation in violations:
            # Check cooldown to avoid alert spam
            last_alert = self.alert_history.get(violation, datetime.min)
            if (datetime.utcnow() - last_alert).total_seconds() < self.alert_cooldown:
                continue
            
            # Update alert history
            self.alert_history[violation] = datetime.utcnow()
            
            # Trigger emergency alert
            if self.enable_alerts:
                self.trigger_emergency_alert(violation, results, frame)
            
            print(f"⚠️  VIOLATION DETECTED: {violation}")
            print(f"   Workers: {results.get('workers_detected', 0)}")
            print(f"   Helmets: {results.get('helmets_detected', 0)}")
            print(f"   Confidence: {results.get('confidence', 0):.2f}")
    
    def trigger_emergency_alert(self, violation, results, frame):
        """Trigger emergency alert via AlertDispatcher"""
        try:
            from backend.services.alert_dispatcher import get_alert_dispatcher, AlertTrigger
            
            dispatcher = get_alert_dispatcher()
            if dispatcher:
                alert = AlertTrigger(
                    camera_id=0,
                    risk_type='not_wearing_helmet' if 'HELMET' in violation else 'unsafe_behavior',
                    risk_category='PPE',
                    severity='CRITICAL' if results.get('workers_detected', 0) > 1 else 'HIGH',
                    confidence_score=results.get('confidence', 0),
                    risk_score=int((1 - results.get('confidence', 0)) * 100),
                    location='Factory Floor',
                    details=f"Safety Violation: {violation}. Detected {results.get('workers_detected', 0)} workers, {results.get('helmets_detected', 0)} wearing helmets"
                )
                
                dispatcher.dispatch_alert(alert)
                print(f"✅ Emergency Alert Sent - {violation}")
        except Exception as e:
            print(f"❌ Failed to send alert: {e}")
    
    def run_monitoring(self):
        """Main monitoring loop"""
        cap = cv2.VideoCapture(self.camera_source)
        
        # Set camera resolution for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.is_running = True
        print("🚀 Real-time Safety Monitoring Started")
        print("Press 'q' to quit\n")
        
        while self.is_running:
            try:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read frame from camera")
                    break
                
                # Process frame with detection and alerts
                results = self.process_frame(frame)
                
                # Annotate frame with results
                frame = self.annotate_frame(frame, results)
                
                # Display frame
                cv2.imshow("AI Safety Monitoring - LIVE", frame)
                
                # Performance tracking
                self.frame_count += 1
                fps = self.calculate_fps()
                
                # Check for quit command
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(0.1)
        
        cap.release()
        cv2.destroyAllWindows()
        self.is_running = False
        print("\n✅ Monitoring stopped")
    
    def annotate_frame(self, frame, results):
        """Annotate frame with detection results"""
        try:
            annotated = self.detector.annotate_frame(frame, results)
            return annotated
        except:
            return frame
    
    def calculate_fps(self):
        """Calculate frames per second"""
        now = time.time()
        self.fps_times.append(now)
        self.fps_times = [t for t in self.fps_times if now - t < 1]
        return len(self.fps_times)
    
    def stop(self):
        """Stop monitoring"""
        self.is_running = False

if __name__ == '__main__':
    # Start real-time monitoring
    monitor = RealtimeSafetyMonitor(camera_source=0, enable_alerts=True)
    monitor.run_monitoring()
