#!/usr/bin/env python3
"""
Color Analysis Script for Helmet Detection Debugging
Analyzes HSV color values in camera feed to understand helmet colors
"""

import cv2
import numpy as np
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

def analyze_colors():
    """Analyze colors in camera feed"""
    print("🎨 Starting color analysis...")
    print("   Analyzing 5 frames automatically\n")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    frame_count = 0
    max_frames = 5

    try:
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Analyze upper portion (where helmets would be)
            height, width = hsv.shape[:2]
            upper_region = hsv[0:int(height*0.6), :]  # Top 60% of frame

            # Calculate average HSV values
            avg_h = np.mean(upper_region[:, :, 0])
            avg_s = np.mean(upper_region[:, :, 1])
            avg_v = np.mean(upper_region[:, :, 2])

            # Find dominant colors (simplified without sklearn)
            pixels = upper_region.reshape(-1, 3)
            if len(pixels) > 100:
                # Simple histogram-based dominant color detection
                h_bins = np.histogram(pixels[:, 0], bins=8, range=(0, 180))[0]
                s_bins = np.histogram(pixels[:, 1], bins=4, range=(0, 255))[0]
                v_bins = np.histogram(pixels[:, 2], bins=4, range=(0, 255))[0]

                # Find peaks in histograms
                h_peak = np.argmax(h_bins) * 22.5  # 180/8
                s_peak = np.argmax(s_bins) * 63.75  # 255/4
                v_peak = np.argmax(v_bins) * 63.75

                print(f"\n🎨 Dominant Color Ranges:")
                print(".1f")
                print(".1f")
                print(".1f")

                # Suggest helmet color match
                if 10 <= h_peak <= 40 and s_peak >= 40:  # Yellow range
                    print(f"      → Yellow helmet candidate")
                elif 0 <= h_peak <= 15 and s_peak >= 50:  # Orange range
                    print(f"      → Orange helmet candidate")
                elif 90 <= h_peak <= 130 and s_peak >= 50:  # Blue range
                    print(f"      → Blue helmet candidate")
                elif 0 <= h_peak <= 10 and s_peak >= 50 or 170 <= h_peak <= 180 and s_peak >= 50:  # Red range
                    print(f"      → Red helmet candidate")
                elif 35 <= h_peak <= 80 and s_peak >= 50:  # Green range
                    print(f"      → Green helmet candidate")
                elif s_peak <= 30:  # Low saturation = gray/white
                    print(f"      → Gray/White helmet candidate")
                else:
                    print(f"      → Unknown color - may need custom helmet detection")

            # Small delay
            cv2.waitKey(500)

    except Exception as e:
        print(f"❌ Analysis error: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Color analysis complete")

if __name__ == '__main__':
    analyze_colors()