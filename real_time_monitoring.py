#!/usr/bin/env python3
"""
Standalone Real-Time Safety Monitoring Script
Run this directly to start helmet detection and safety alerts
Usage: python real_time_monitoring.py
"""

import cv2
import numpy as np
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import logging

#!/usr/bin/env python3
"""
Enhanced Real-Time Safety Monitoring Script with Employee Recognition
Run this directly to start helmet detection, employee recognition, and automated alerts
Usage: python real_time_monitoring.py
"""

import cv2
import numpy as np
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)

class EnhancedRealtimeSafetyMonitor:
    """Enhanced real-time safety monitoring with employee recognition and notifications"""

    def __init__(self, camera_source=0, camera_id=None, location="Main Entrance"):
        """
        Initialize enhanced real-time monitor

        Args:
            camera_source: 0 for webcam, or video file path
            camera_id: Camera identifier for database logging
            location: Location description
        """
        self.camera_source = camera_source
        self.camera_id = camera_id
        self.location = location
        self.frame = None
        self.is_running = False

        # Initialize services
        self.db_session = None
        self.employee_service = None
        self.enhanced_monitor = None

        # Initialize core services
        self._init_services()

        # Alert tracking
        self.alert_history = defaultdict(lambda: datetime.min)
        self.alert_cooldown = 300  # 5 minutes between same alerts

        # Statistics
        self.frame_count = 0
        self.total_detections = 0
        self.start_time = None

    def _init_services(self):
        """Initialize database and services"""
        try:
            # Initialize database
            from backend.database.models import db
            from config import Config

            config = Config()
            self.db_session = db

            # Initialize employee service
            from backend.services.employee_service import EmployeeService
            self.employee_service = EmployeeService(self.db_session)

            # Initialize notification services
            from backend.services.notification_service import NotificationService
            notification_service = NotificationService(config.get_notification_config())

            # Initialize WhatsApp service (optional)
            whatsapp_service = None
            try:
                from backend.services.whatsapp_service import WhatsAppService
                whatsapp_service = WhatsAppService(config.get_whatsapp_config())
            except Exception as e:
                logger.warning(f"WhatsApp service not available: {e}")

            # Initialize enhanced safety monitor
            from backend.services.enhanced_safety_monitor import EnhancedSafetyMonitor
            self.enhanced_monitor = EnhancedSafetyMonitor(
                self.db_session,
                self.employee_service,
                notification_service,
                whatsapp_service,
                alert_cooldown=self.alert_cooldown
            )

            logger.info("✅ All services initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize services: {e}")
            self.employee_service = None
            self.enhanced_monitor = None

    def process_frame(self, frame):
        """Process single frame with enhanced detection"""
        if self.enhanced_monitor is None:
            # Fallback to basic detection
            return self._fallback_detection(frame)

        try:
            results = self.enhanced_monitor.process_frame(
                frame,
                camera_id=self.camera_id,
                location=self.location
            )
            self.total_detections += 1
            return results
        except Exception as e:
            logger.error(f"Enhanced detection error: {e}")
            return self._fallback_detection(frame)

    def _fallback_detection(self, frame):
        """Fallback to basic safety detection"""
        try:
            from safety_detection import SafetyDetector
            detector = SafetyDetector()
            results = detector.detect(frame)
            results['fallback_mode'] = True
            return results
        except Exception as e:
            logger.error(f"Fallback detection error: {e}")
            return {
                'error': 'Detection failed',
                'fallback_mode': True,
                'timestamp': datetime.utcnow().isoformat()
            }

    def run(self, test_video=None):
        """
        Run enhanced real-time monitoring

        Args:
            test_video: Optional path to test video file
        """
        source = test_video if test_video else self.camera_source
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            logger.error(f"❌ Failed to open video source: {source}")
            return

        # Configure camera
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        self.is_running = True
        self.start_time = datetime.utcnow()

        print("\n" + "="*80)
        print("🚀 ENHANCED AI SAFETY MONITORING SYSTEM WITH EMPLOYEE RECOGNITION")
        print("="*80)
        print(f"  Source: {source if isinstance(source, str) else 'Webcam'}")
        print(f"  Camera ID: {self.camera_id or 'N/A'}")
        print(f"  Location: {self.location}")
        print(f"  Employee Recognition: {'✅ Enabled' if self.employee_service else '❌ Disabled'}")
        print(f"  Notifications: {'✅ Enabled' if self.enhanced_monitor else '❌ Disabled'}")
        print(f"  Status: ACTIVE")
        print(f"  Time:   {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n  Press 'q' to quit, 's' to save screenshot, 'i' for system info")
        print("="*80 + "\n")

        frame_count = 0

        try:
            while self.is_running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    logger.warning("End of video or camera disconnected")
                    break

                frame_count += 1

                # Process frame
                results = self.process_frame(frame)
                if results is None:
                    continue

                # Display results
                self._display_results(results)

                # Annotate frame
                annotated = self._annotate_frame(frame, results)

                # Display
                cv2.imshow("🛡️  Enhanced AI Safety Monitoring - EMPLOYEE RECOGNITION", annotated)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self._save_screenshot(annotated, results)
                elif key == ord('i'):
                    self._print_system_info()

                # Status update every 100 frames
                if frame_count % 100 == 0:
                    self._print_status(frame_count)

        except KeyboardInterrupt:
            logger.info("Interrupt signal received")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.is_running = False
            self._print_final_stats()

    def _display_results(self, results):
        """Display detection results"""
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            return

        recognized = results.get('recognized_employees', [])
        violations = results.get('violations', [])
        alerts = results.get('alerts_sent', [])

        if recognized:
            print(f"👤 Recognized {len(recognized)} employee(s):")
            for emp in recognized:
                status = emp.get('compliance', {}).get('status', 'unknown')
                status_icon = "✅" if status == 'compliant' else "❌" if status == 'non_compliant' else "❓"
                print(f"   {status_icon} {emp['name']} ({emp['employee_id']}) - {status}")

        if violations:
            print(f"🚨 {len(violations)} violation(s) detected:")
            for violation in violations:
                print(f"   ⚠️  {violation['employee_name']} - {', '.join(violation['violations'])}")

        if alerts:
            print(f"📤 {len(alerts)} alert(s) sent")

    def _annotate_frame(self, frame, results):
        """Annotate frame with detection results"""
        annotated = frame.copy()

        try:
            height, width = frame.shape[:2]

            # Draw header
            cv2.rectangle(annotated, (0, 0), (width, 120), (0, 0, 0), -1)

            # Title
            cv2.putText(annotated, "ENHANCED AI SAFETY MONITORING", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            # System status
            status_text = f"Camera: {self.camera_id or 'N/A'} | Location: {self.location}"
            cv2.putText(annotated, status_text, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

            # Employee recognition status
            recognized = results.get('recognized_employees', [])
            emp_text = f"Employees Recognized: {len(recognized)}"
            cv2.putText(annotated, emp_text, (10, 85),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 255), 1)

            # Violations
            violations = results.get('violations', [])
            if violations:
                viol_text = f"Active Violations: {len(violations)}"
                cv2.putText(annotated, viol_text, (10, 105),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
            else:
                cv2.putText(annotated, "Status: All Clear", (10, 105),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

            # Draw employee bounding boxes
            for emp in recognized:
                face_loc = emp.get('face_location')
                if face_loc:
                    top, right, bottom, left = face_loc
                    compliance = emp.get('compliance', {})
                    color = (0, 255, 0) if compliance.get('status') == 'compliant' else (0, 0, 255)

                    # Draw rectangle around face
                    cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)

                    # Draw employee info
                    label = f"{emp['name']} ({emp['confidence']:.2f})"
                    cv2.putText(annotated, label, (left, top - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # Timestamp
            cv2.putText(annotated, f"Time: {datetime.utcnow().strftime('%H:%M:%S')}",
                       (width - 250, height - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        except Exception as e:
            logger.error(f"Error annotating frame: {e}")

        return annotated

    def _save_screenshot(self, frame, results):
        """Save screenshot with results"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.jpg"
            filepath = Path('screenshots')
            filepath.mkdir(exist_ok=True)
            cv2.imwrite(str(filepath / filename), frame)
            print(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")

    def _print_system_info(self):
        """Print system information"""
        print("\n" + "="*60)
        print("SYSTEM INFORMATION")
        print("="*60)
        print(f"Camera Source: {self.camera_source}")
        print(f"Camera ID: {self.camera_id or 'N/A'}")
        print(f"Location: {self.location}")
        print(f"Employee Service: {'✅ Active' if self.employee_service else '❌ Inactive'}")
        print(f"Enhanced Monitor: {'✅ Active' if self.enhanced_monitor else '❌ Inactive'}")
        print(f"Alert Cooldown: {self.alert_cooldown} seconds")
        print(f"Total Frames Processed: {self.frame_count}")
        print(f"Total Detections: {self.total_detections}")
        print("="*60 + "\n")

    def _print_status(self, frame_count):
        """Print periodic status"""
        elapsed = datetime.utcnow() - self.start_time
        fps = frame_count / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
        print(f"📊 Status: {frame_count} frames processed | {fps:.1f} FPS | {elapsed}")

    def _print_final_stats(self):
        """Print final statistics"""
        if self.start_time:
            elapsed = datetime.utcnow() - self.start_time
            avg_fps = self.frame_count / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0

            print("\n" + "="*60)
            print("FINAL STATISTICS")
            print("="*60)
            print(f"Total Runtime: {elapsed}")
            print(f"Frames Processed: {self.frame_count}")
            print(f"Average FPS: {avg_fps:.1f}")
            print(f"Total Detections: {self.total_detections}")
            print(f"Employee Service: {'Active' if self.employee_service else 'Inactive'}")
            print(f"Notifications: {'Active' if self.enhanced_monitor else 'Inactive'}")
            print("="*60 + "\n")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced AI Safety Monitoring System')
    parser.add_argument('--camera', type=int, default=0, help='Camera source (default: 0)')
    parser.add_argument('--video', type=str, help='Video file path')
    parser.add_argument('--camera-id', type=int, help='Camera ID for database')
    parser.add_argument('--location', type=str, default='Main Entrance', help='Location description')

    args = parser.parse_args()

    # Initialize enhanced monitor
    monitor = EnhancedRealtimeSafetyMonitor(
        camera_source=args.video if args.video else args.camera,
        camera_id=args.camera_id,
        location=args.location
    )

    # Run monitoring
    monitor.run(test_video=args.video)


if __name__ == "__main__":
    main()
    """Real-time helmet and PPE safety monitoring"""
    
    def __init__(self, camera_source=0, model_type='cascade'):
        """
        Initialize real-time monitor
        
        Args:
            camera_source: 0 for webcam, or video file path
            model_type: Detection model type ('cascade' or 'advanced')
        """
        self.camera_source = camera_source
        self.model_type = model_type
        self.frame = None
        self.is_running = False
        
        # Initialize detector
        try:
            from safety_detection import SafetyDetector
            self.detector = SafetyDetector(model_type='cascade')
            logger.info("✅ SafetyDetector initialized successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import SafetyDetector: {e}")
            self.detector = None
        
        # Alert tracking
        self.alert_history = defaultdict(lambda: datetime.min)
        self.alert_cooldown = 5  # seconds between same alerts
        self.violation_log = []
        
        # Statistics
        self.frame_count = 0
        self.total_detections = 0
        self.start_time = None
    
    def process_frame(self, frame):
        """Process single frame with detection"""
        if self.detector is None:
            return None
        
        try:
            results = self.detector.detect(frame)
            self.total_detections += 1
            return results
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return None
    
    def handle_violations(self, violations, results):
        """Handle detected safety violations"""
        if not violations:
            return
        
        for violation in violations:
            last_alert = self.alert_history.get(violation, datetime.min)
            if (datetime.utcnow() - last_alert).total_seconds() < self.alert_cooldown:
                continue
            
            # Update alert tracking
            self.alert_history[violation] = datetime.utcnow()
            self.violation_log.append({
                'time': datetime.utcnow(),
                'violation': violation,
                'workers': results.get('workers_detected', 0),
                'helmets': results.get('helmets_detected', 0)
            })
            
            # Display alert
            self._display_alert(violation, results)
    
    def _display_alert(self, violation, results):
        """Display violation alert"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        workers = results.get('workers_detected', 0)
        helmets = results.get('helmets_detected', 0)
        confidence = results.get('confidence', 0)
        
        print("\n" + "="*70)
        print(f"🚨 SAFETY VIOLATION ALERT - {timestamp}")
        print("="*70)
        print(f"  Violation Type:    {violation}")
        print(f"  Workers Detected:  {workers}")
        print(f"  Helmets Detected:  {helmets}")
        print(f"  Compliance Rate:   {int(confidence*100)}%")
        print(f"  Severity:          {'CRITICAL' if workers > 1 else 'HIGH'}")
        print("  Action:            ⚠️  IMMEDIATE ACTION REQUIRED")
        print("="*70 + "\n")
    
    def run(self, test_video=None):
        """
        Run real-time monitoring
        
        Args:
            test_video: Optional path to test video file
        """
        if self.detector is None:
            logger.error("❌ Cannot start monitoring - detector not initialized")
            return
        
        source = test_video if test_video else self.camera_source
        cap = cv2.VideoCapture(source)
        
        if not cap.isOpened():
            logger.error(f"❌ Failed to open video source: {source}")
            return
        
        # Configure camera
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.is_running = True
        self.start_time = datetime.utcnow()
        
        print("\n" + "="*70)
        print("🚀 REAL-TIME SAFETY MONITORING SYSTEM")
        print("="*70)
        print(f"  Source: {source if isinstance(source, str) else 'Webcam'}")
        print(f"  Model:  {self.model_type}")
        print(f"  Status: ACTIVE")
        print(f"  Time:   {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n  Press 'q' to quit, 's' to save screenshot")
        print("="*70 + "\n")
        
        frame_count = 0
        
        try:
            while self.is_running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    logger.warning("End of video or camera disconnected")
                    break
                
                frame_count += 1
                
                # Process frame
                results = self.process_frame(frame)
                if results is None:
                    continue
                
                # Handle violations
                violations = results.get('violations', [])
                self.handle_violations(violations, results)
                
                # Annotate frame
                annotated = self.detector.annotate_frame(frame, results)
                
                # Display
                cv2.imshow("🛡️  AI Safety Monitoring - LIVE", annotated)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self._save_screenshot(annotated, results)
                
                # Status update every 100 frames
                if frame_count % 100 == 0:
                    self._print_status(frame_count)
        
        except KeyboardInterrupt:
            logger.info("Interrupt signal received")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.is_running = False
            self._print_final_stats()
    
    def _save_screenshot(self, frame, results):
        """Save annotated frame screenshot"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"safety_screenshot_{timestamp}.png"
            cv2.imwrite(filename, frame)
            logger.info(f"✅ Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
    
    def _print_status(self, frame_count):
        """Print current monitoring status"""
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        fps = frame_count / elapsed if elapsed > 0 else 0
        violations_count = len(self.violation_log)
        
        print(f"[Frame {frame_count}] FPS: {fps:.1f} | Detections: {self.total_detections} | Violations: {violations_count}")
    
    def _print_final_stats(self):
        """Print final statistics"""
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        
        print("\n" + "="*70)
        print("📊 MONITORING SESSION SUMMARY")
        print("="*70)
        print(f"  Duration:          {int(elapsed)} seconds")
        print(f"  Frames Processed:  {self.frame_count}")
        print(f"  Total Detections:  {self.total_detections}")
        print(f"  Violations Found:  {len(self.violation_log)}")
        
        if self.violation_log:
            print("\n  Violation History:")
            for entry in self.violation_log[-10:]:  # Last 10
                print(f"    - {entry['time'].strftime('%H:%M:%S')}: {entry['violation']} "
                      f"({entry['workers']} workers, {entry['helmets']} helmets)")
        
        print("="*70 + "\n")
        logger.info("✅ Monitoring stopped successfully")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='AI Safety Helmet Detection System'
    )
    parser.add_argument(
        '--camera', '-c',
        type=int,
        default=0,
        help='Camera index (default: 0 for webcam)'
    )
    parser.add_argument(
        '--model', '-m',
        type=str,
        choices=['cascade', 'advanced'],
        default='cascade',
        help='Detection model type'
    )
    parser.add_argument(
        '--video', '-v',
        type=str,
        help='Path to test video file'
    )
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = RealtimeSafetyMonitor(
        camera_source=args.camera,
        model_type=args.model
    )
    
    # Start monitoring
    try:
        monitor.run(test_video=args.video)
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
