#!/usr/bin/env python3
"""
Quick Test Script for Helmet Detection
Tests the detection system with a sample image or webcam
"""

import cv2
import numpy as np
import sys
import os
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

def test_detection_system():
    """Test helmet detection system"""
    
    print("\n" + "="*70)
    print("🧪 HELMET DETECTION SYSTEM - QUICK TEST")
    print("="*70 + "\n")
    
    # Test imports
    print("1️⃣  Testing imports...")
    try:
        from safety_detection import SafetyDetector
        print("   ✅ SafetyDetector imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import SafetyDetector: {e}")
        return False
    
    # Initialize detector
    print("\n2️⃣  Initializing detector...")
    try:
        detector = SafetyDetector(model_type='cascade')
        print("   ✅ SafetyDetector initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False
    
    # Test with sample frame
    print("\n3️⃣  Testing with sample frame...")
    try:
        # Create a dummy frame (blue background)
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add green rectangle (simulating helmet)
        cv2.rectangle(test_frame, (200, 100), (250, 150), (0, 255, 0), -1)
        # Add face outline rectangle (simulating worker)
        cv2.rectangle(test_frame, (190, 150), (260, 280), (0, 165, 255), 2)
        
        # Run detection
        results = detector.detect(test_frame)
        print(f"   ✅ Detection completed")
        print(f"      - Workers detected: {results.get('workers_detected', 0)}")
        print(f"      - Helmets detected: {results.get('helmets_detected', 0)}")
        print(f"      - Violations: {results.get('violations', [])}")
        
    except Exception as e:
        print(f"   ❌ Detection failed: {e}")
        return False
    
    # Test with webcam
    print("\n4️⃣  Testing webcam access...")
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("   ✅ Webcam accessible")
                print(f"      Frame size: {frame.shape}")
            else:
                print("   ⚠️  Webcam opened but no frame captured")
        else:
            print("   ⚠️  Webcam not accessible")
    except Exception as e:
        print(f"   ⚠️  Webcam test failed: {e}")
    
    print("\n" + "="*70)
    print("✅ SYSTEM CHECK COMPLETE - Ready to run real-time monitoring")
    print("="*70 + "\n")
    print("📌 Run real-time monitoring with:")
    print("   python real_time_monitoring.py")
    print("\n")
    
    return True


def test_with_live_camera():
    """Interactive camera test"""
    print("🎥 Starting live camera test (60 seconds)...")
    print("   Press 'q' to quit early\n")
    
    try:
        from safety_detection import SafetyDetector
        
        detector = SafetyDetector()
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Cannot open camera")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        start_time = cv2.getTickCount()
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run detection
            results = detector.detect(frame)
            annotated = detector.annotate_frame(frame, results)
            
            # Display
            cv2.imshow("Helmet Detection Test", annotated)
            
            frame_count += 1
            
            # Check timeout (60 seconds)
            elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
            if elapsed > 60:
                print(f"\n⏱️  Test complete - 60 seconds elapsed")
                break
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n✋ Test stopped by user")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"✅ Captured {frame_count} frames in {int(elapsed)} seconds")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test detection system')
    parser.add_argument('--live', action='store_true', help='Test with live camera')
    args = parser.parse_args()
    
    if args.live:
        test_with_live_camera()
    else:
        test_detection_system()
