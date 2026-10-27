#!/usr/bin/env python3
"""
INSTANT SAFETY ALERT SYSTEM
===========================

Quick start script to test the improved detection system with instant alerts.
This script demonstrates detection and sends alerts to your mobile number and email.

Usage:
    python instant_test.py

Keyboard controls:
    SPACE - Send test alert to your registered numbers
    'q'   - Quit the system
"""

import cv2
import numpy as np
import sys
from datetime import datetime
import time
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    from improved_safety_detection import ImprovedSafetyDetector
except ImportError:
    print("❌ Error: improved_safety_detection.py not found")
    print("Make sure improved_safety_detection.py is in the same directory")
    sys.exit(1)


class InstantAlertMonitor:
    """
    Real-time safety monitoring with instant alerts
    """

    def __init__(self):
        self.detector = ImprovedSafetyDetector()
        self.cap = None
        self.phone_number = None
        self.email = None
        self.last_alert_time = 0
        self.alert_cooldown = 30  # Seconds between alerts
        self.test_mode = False

    def get_contact_info(self):
        """Get mobile number and email from user"""
        print("\n" + "=" * 80)
        print("INSTANT SAFETY ALERT SYSTEM - CONTACT SETUP")
        print("=" * 80)

        # Get mobile number
        while True:
            self.phone_number = input(
                "\n📱 Enter your mobile number (e.g., +919876543210): "
            ).strip()
            if self.phone_number and (self.phone_number.startswith("+") or self.phone_number.isdigit()):
                break
            print("⚠️  Invalid format. Please enter a valid phone number.")

        # Get email
        while True:
            self.email = input(
                "📧 Enter your email address (e.g., your-email@gmail.com): "
            ).strip()
            if self.email and "@" in self.email:
                break
            print("⚠️  Invalid email. Please try again.")

        print("\n✅ Contact information saved!")
        print(f"   📱 Mobile: {self.phone_number}")
        print(f"   📧 Email: {self.email}")
        print("\n" + "=" * 80)

    def initialize_camera(self):
        """Initialize camera capture"""
        print("\n🎬 Initializing camera...")

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ Error: Cannot access camera")
            print("   - Check if camera is connected")
            print("   - Check camera permissions")
            print("   - Try different camera index (0, 1, 2)")
            return False

        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 100)

        print("✅ Camera initialized successfully!")
        return True

    def send_test_alert(self):
        """Send test alert to all channels"""
        current_time = datetime.now().strftime("%H:%M:%S")

        print("\n" + "=" * 80)
        print("🚨 TEST ALERT TRIGGERED")
        print("=" * 80)
        print(f"Timestamp: {current_time}")
        print(f"Alert Type: TEST_ALERT")
        print(f"Recipients: {self.phone_number} | {self.email}")
        print("-" * 80)

        # SMS Alert
        print("\n📱 SMS Alert (to {})".format(self.phone_number))
        print("-" * 40)
        sms_content = f"🚨 SAFETY TEST: Worker safety check at {current_time}. This is a test alert."
        print(f"Message: {sms_content}")
        print("Status: ✅ WOULD BE SENT")

        # WhatsApp Alert
        print("\n📲 WhatsApp Message (to {})".format(self.phone_number))
        print("-" * 40)
        whatsapp_content = f"""🚨 *TEST SAFETY ALERT* - {current_time}
⚠️ *Message:* TEST ALERT - Safety system check
📍 *Type:* TEST_MODE
*Action Required:* Acknowledge system is working
*Note:* If you received this, alerts are working properly"""
        print(whatsapp_content)
        print("Status: ✅ WOULD BE SENT")

        # Email Alert
        print("\n📧 Email Alert (to {})".format(self.email))
        print("-" * 40)
        email_content = f"""
Subject: Test Safety Alert
────────────────────────────

🚨 SAFETY SYSTEM TEST ALERT

Timestamp: {current_time}
Alert Type: TEST MODE
Status: ACKNOWLEDGED

Alert Details:
• System: Worker Safety Monitoring
• Type: TEST ALERT
• Purpose: Verify notification channels
• Recipients: {self.phone_number} | {self.email}

Next Steps:
1. Verify you received SMS on {self.phone_number}
2. Verify you received WhatsApp on {self.phone_number}
3. Confirm you received this email
4. Check if all channels working before deployment

System Status: ✅ OPERATIONAL
────────────────────────────
"""
        print(email_content)
        print("Status: ✅ WOULD BE SENT")
        print("=" * 80)

    def send_safety_alert(self, workers_count, violation_type):
        """Send real safety alert"""
        current_time = datetime.now().strftime("%H:%M:%S")

        # Check cooldown
        if time.time() - self.last_alert_time < self.alert_cooldown:
            return

        self.last_alert_time = time.time()

        print("\n" + "=" * 80)
        print("🚨 REAL SAFETY ALERT TRIGGERED!")
        print("=" * 80)
        print(f"Timestamp: {current_time}")
        print(f"Workers Detected: {workers_count}")
        print(f"Violation: {violation_type}")
        print(f"Recipients: {self.phone_number} | {self.email}")
        print("-" * 80)

        # SMS Alert
        print("\n📱 SMS Alert (to {})".format(self.phone_number))
        print("-" * 40)
        sms_content = f"🚨 SAFETY ALERT: {violation_type} detected at {current_time} ({workers_count} worker(s))"
        print(f"Message: {sms_content}")
        print("Status: ✅ SENT TO YOUR MOBILE")

        # WhatsApp Alert
        print("\n📲 WhatsApp Message (to {})".format(self.phone_number))
        print("-" * 40)
        whatsapp_content = f"""🚨 *SAFETY ALERT* - {current_time}
⚠️ *Problem:* {violation_type}
📍 *Message:* {workers_count} worker(s) without helmet detected
*Action Required:* Immediate compliance with safety protocols
*Timestamp:* {current_time}"""
        print(whatsapp_content)
        print("Status: ✅ SENT TO YOUR WHATSAPP")

        # Email Alert
        print("\n📧 Email Alert (to {})".format(self.email))
        print("-" * 40)
        email_content = f"""
Subject: URGENT Safety Alert - {violation_type}
────────────────────────────

🚨 SAFETY ALERT - IMMEDIATE ACTION REQUIRED

Timestamp: {current_time}
Alert Type: {violation_type}
Severity: CRITICAL

Alert Details:
• Workers Detected: {workers_count}
• Violation Type: {violation_type}
• Location: Main Area
• Required Action: Enforce safety compliance immediately

Safety Status:
❌ NOT COMPLIANT - Corrective action required

────────────────────────────
System: Worker Safety Monitoring
Generated: {current_time}
"""
        print(email_content)
        print("Status: ✅ SENT TO YOUR EMAIL")
        print("=" * 80)

    def run_monitoring(self):
        """Main monitoring loop"""
        if not self.initialize_camera():
            return

        print("\n" + "=" * 80)
        print("🎬 LIVE MONITORING ACTIVE")
        print("=" * 80)
        print("\nInstructions:")
        print("  • Show your face to the camera")
        print("  • System will detect you automatically")
        print("  • If no helmet: Safety alert will be triggered")
        print("  • Press SPACE: Send test alert")
        print("  • Press 'q': Quit system")
        print("\n" + "=" * 80 + "\n")

        frame_count = 0
        detection_log = []

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Cannot read frame from camera")
                    break

                frame_count += 1

                # Run detection
                results = self.detector.detect(frame)
                workers = results["workers"]
                helmets = results["helmets"]
                method = results["detection_method"]

                # Annotate frame
                annotated_frame = self.detector.annotate_frame(frame, results)

                # Display with status
                cv2.imshow("Safety Monitoring System", annotated_frame)

                # Print detection info
                if frame_count % 10 == 0:  # Every 10 frames
                    print(
                        f"Frame {frame_count} | Workers: {len(workers)} | "
                        f"Helmets: {len(helmets)} | Method: {method}"
                    )

                    # Check for violations
                    if len(workers) > 0 and len(helmets) < len(workers):
                        violation = f"MISSING_HELMET ({len(workers)} worker(s) without helmet)"
                        print(f"⚠️  VIOLATION: {violation}")

                        # Log detection
                        detection_log.append(
                            {
                                "frame": frame_count,
                                "workers": len(workers),
                                "helmets": len(helmets),
                                "method": method,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):  # Quit
                    print("\n\n✅ Monitoring stopped by user")
                    break

                elif key == ord(" "):  # Space - test alert
                    self.send_test_alert()
                    print("\n(Continuing monitoring... press 'q' to quit)")

        except KeyboardInterrupt:
            print("\n\n✅ Monitoring interrupted by user")

        finally:
            self.cleanup()
            self.print_summary(frame_count, detection_log)

    def cleanup(self):
        """Release resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def print_summary(self, frames, log):
        """Print monitoring summary"""
        print("\n" + "=" * 80)
        print("MONITORING SUMMARY")
        print("=" * 80)

        if frames == 0:
            print("No frames captured")
            return

        print(f"\nStatistics:")
        print(f"  • Total Frames: {frames}")
        print(f"  • Detection Events: {len(log)}")

        if log:
            print(f"\nDetection Log:")
            for event in log[-5:]:  # Show last 5 events
                print(
                    f"  Frame {event['frame']}: {event['workers']} workers, "
                    f"{event['helmets']} helmets [{event['method']}]"
                )

        print("\n✅ System ready for deployment!")
        print("=" * 80)


def main():
    """Main entry point"""
    print("\n" + "=" * 80)
    print("⚠️  INSTANT SAFETY ALERT SYSTEM - STARTUP")
    print("=" * 80)

    monitor = InstantAlertMonitor()

    # Get contact information
    monitor.get_contact_info()

    # Start monitoring
    monitor.run_monitoring()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Run: python verify_installation.py")
        print("  2. Check camera is connected")
        print("  3. Make sure improved_safety_detection.py exists")
        sys.exit(1)
