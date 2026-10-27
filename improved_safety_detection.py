"""
IMPROVED Safety Detection Module with Multiple Detection Methods
Uses multiple detection techniques for robust worker and helmet detection
"""

import cv2
import numpy as np
import os
from datetime import datetime

class ImprovedSafetyDetector:
    """
    Advanced safety detection with multiple fallback detection methods
    """

    def __init__(self, model_type='advanced'):
        """Initialize detector with multiple methods"""
        self.model_type = model_type
        self.detect_history = {}

        # Initialize all cascade classifiers
        self.init_cascades()

        # Safety thresholds
        self.helmet_confidence_threshold = 0.4
        self.worker_detection_threshold = 0.3
        self.alert_cooldown = 5

        # Background subtraction for motion detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=False
        )

    def init_cascades(self):
        """Initialize all available cascade classifiers"""
        cascade_path = cv2.data.haarcascades

        # Load multiple cascade classifiers for robust detection
        self.face_cascade = cv2.CascadeClassifier(
            os.path.join(cascade_path, 'haarcascade_frontalface_default.xml')
        )

        self.face_alt_cascade = cv2.CascadeClassifier(
            os.path.join(cascade_path, 'haarcascade_frontalface_alt.xml')
        )

        self.face_alt2_cascade = cv2.CascadeClassifier(
            os.path.join(cascade_path, 'haarcascade_frontalface_alt2.xml')
        )

        # Try to load upper body cascade (if available)
        try:
            self.upperbody_cascade = cv2.CascadeClassifier(
                os.path.join(cascade_path, 'haarcascade_upperbody.xml')
            )
        except:
            self.upperbody_cascade = None

        print("✅ Cascade classifiers initialized")

    def detect(self, frame):
        """Main detection with improved methods"""
        results = {
            'workers_detected': 0,
            'helmets_detected': 0,
            'violations': [],
            'confidence': 0.0,
            'timestamp': datetime.utcnow().isoformat(),
            'frame_shape': frame.shape,
            'detection_method': 'primary'
        }

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply preprocessing to improve detection
            preprocessed = self._preprocess_frame(gray)

            # Primary detection: Multiple cascade classifiers
            workers = self._detect_workers_cascades(preprocessed)

            # Fallback 1: Motion detection (background subtraction)
            if len(workers) == 0:
                workers = self._detect_workers_motion(frame, gray)
                results['detection_method'] = 'motion'

            # Fallback 2: Skin tone detection
            if len(workers) == 0:
                workers = self._detect_workers_skin_tone(frame)
                results['detection_method'] = 'skin_tone'

            # Fallback 3: Edge-based detection
            if len(workers) == 0:
                workers = self._detect_workers_edges(gray)
                results['detection_method'] = 'edges'

            results['workers_detected'] = len(workers)

            # Detect helmets
            helmets = self._detect_helmets(gray, frame)
            results['helmets_detected'] = len(helmets)
            results['worker_boxes'] = workers
            results['helmet_boxes'] = helmets

            # Analyze safety compliance
            violations = self._analyze_safety(workers, helmets, frame)
            results['violations'] = violations

            # Calculate compliance
            if results['workers_detected'] > 0:
                results['confidence'] = results['helmets_detected'] / results['workers_detected']

            # Store history
            self._update_history(results)

            # Debug output
            if len(workers) > 0:
                print(f"✅ Detected {len(workers)} worker(s) | Method: {results['detection_method']}")

        except Exception as e:
            print(f"❌ Detection error: {e}")
            results['error'] = str(e)

        return results

    def _preprocess_frame(self, gray):
        """Preprocess frame for better detection"""
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Apply bilateral filter to reduce noise while keeping edges
        filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)

        return filtered

    def _detect_workers_cascades(self, gray):
        """Detect workers using multiple cascade classifiers"""
        workers = []
        detected_rects = []

        try:
            # Try primary face cascade with multiple scales
            for scale_factor in [1.05, 1.1, 1.15]:
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=scale_factor,
                    minNeighbors=3,
                    minSize=(30, 30),
                    maxSize=(400, 400)
                )
                detected_rects.extend(faces)

            # Try alternative face cascades
            if len(detected_rects) < 3:
                faces = self.face_alt_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=4,
                    minSize=(30, 30)
                )
                detected_rects.extend(faces)

            if len(detected_rects) < 3:
                faces = self.face_alt2_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                detected_rects.extend(faces)

            # Try upper body detection
            if self.upperbody_cascade is not None and len(detected_rects) < 3:
                bodies = self.upperbody_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=3,
                    minSize=(50, 100)
                )
                detected_rects.extend(bodies)

            # Remove duplicates and convert to worker boxes
            detected_rects = list(set(detected_rects.tolist()))

            for (x, y, w, h) in detected_rects:
                # Expand region to include full upper body
                expanded_y = max(0, y - int(h * 0.5))
                expanded_h = int(h * 2.5)

                worker_box = {
                    'x': max(0, x - int(w * 0.25)),
                    'y': expanded_y,
                    'w': int(w * 1.5),
                    'h': expanded_h,
                    'center': (x + w // 2, y + h // 2),
                    'confidence': 0.85
                }
                workers.append(worker_box)

        except Exception as e:
            print(f"Cascade detection error: {e}")

        return workers

    def _detect_workers_motion(self, frame, gray):
        """Detect workers using background subtraction and motion"""
        workers = []

        try:
            # Apply background subtraction
            fg_mask = self.bg_subtractor.apply(frame)

            # Apply morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)

            # Find contours
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Filter contours by area (people-sized objects)
            for contour in contours:
                area = cv2.contourArea(contour)
                if 3000 < area < 80000:  # Reasonable size for a person
                    x, y, w, h = cv2.boundingRect(contour)

                    if h > w * 1.5:  # Person-like aspect ratio
                        worker_box = {
                            'x': x,
                            'y': y,
                            'w': w,
                            'h': h,
                            'center': (x + w // 2, y + h // 2),
                            'confidence': 0.7
                        }
                        workers.append(worker_box)

            print(f"🎬 Motion detection found {len(workers)} potential worker(s)")

        except Exception as e:
            print(f"Motion detection error: {e}")

        return workers

    def _detect_workers_skin_tone(self, frame):
        """Detect workers using skin tone detection"""
        workers = []

        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Define skin tone ranges (HSV)
            lower_skin = np.array([0, 20, 70])
            upper_skin = np.array([20, 255, 255])

            lower_skin2 = np.array([170, 20, 70])
            upper_skin2 = np.array([180, 255, 255])

            # Create skin mask
            mask1 = cv2.inRange(hsv, lower_skin, upper_skin)
            mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
            skin_mask = cv2.bitwise_or(mask1, mask2)

            # Apply morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel, iterations=1)

            # Find contours
            contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)
                if 2000 < area < 50000:
                    x, y, w, h = cv2.boundingRect(contour)

                    if w > 30 and h > 30:  # Minimum size check
                        worker_box = {
                            'x': x,
                            'y': y,
                            'w': w,
                            'h': h,
                            'center': (x + w // 2, y + h // 2),
                            'confidence': 0.65
                        }
                        workers.append(worker_box)

            print(f"🌡️ Skin tone detection found {len(workers)} potential worker(s)")

        except Exception as e:
            print(f"Skin tone detection error: {e}")

        return workers

    def _detect_workers_edges(self, gray):
        """Detect workers using edge detection"""
        workers = []

        try:
            # Apply Canny edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Dilate to connect nearby edges
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            edges = cv2.dilate(edges, kernel, iterations=2)

            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)
                if 5000 < area < 100000:
                    x, y, w, h = cv2.boundingRect(contour)

                    if h > w and h > 100:  # Vertical object
                        worker_box = {
                            'x': x,
                            'y': y,
                            'w': w,
                            'h': h,
                            'center': (x + w // 2, y + h // 2),
                            'confidence': 0.6
                        }
                        workers.append(worker_box)

            print(f"🔍 Edge detection found {len(workers)} potential worker(s)")

        except Exception as e:
            print(f"Edge detection error: {e}")

        return workers

    def _detect_helmets(self, gray, frame):
        """Detect helmets using color and shape analysis"""
        helmets = []

        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Enhanced color ranges for helmets
            ranges = [
                (np.array([10, 40, 50]), np.array([40, 255, 255])),    # Yellow
                (np.array([0, 50, 50]), np.array([15, 255, 255])),      # Orange
                (np.array([0, 0, 130]), np.array([180, 50, 255])),      # White
                (np.array([0, 50, 50]), np.array([10, 255, 255])),      # Red
                (np.array([170, 50, 50]), np.array([180, 255, 255])),   # Red range 2
                (np.array([90, 50, 50]), np.array([130, 255, 255])),    # Blue
            ]

            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for lower, upper in ranges:
                mask |= cv2.inRange(hsv, lower, upper)

            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)

                if 50 < area < 15000:
                    x, y, w, h = cv2.boundingRect(contour)

                    if h > 0 and 0.5 < w / h < 2.0:
                        perimeter = cv2.arcLength(contour, True)
                        if perimeter > 0:
                            circularity = 4 * np.pi * area / (perimeter ** 2)
                            if circularity > 0.4:
                                helmet_box = {
                                    'x': x,
                                    'y': y,
                                    'w': w,
                                    'h': h,
                                    'area': area,
                                    'center': (x + w // 2, y + h // 2),
                                    'circularity': circularity
                                }
                                helmets.append(helmet_box)

        except Exception as e:
            print(f"❌ Helmet detection error: {e}")

        return helmets

    def _analyze_safety(self, workers, helmets, frame):
        """Analyze safety compliance"""
        violations = []

        try:
            if len(workers) == 0:
                return violations

            helmet_centers = [h['center'] for h in helmets]

            for worker in workers:
                has_helmet = False
                worker_top = (worker['center'][0], worker['y'])

                for helmet_center in helmet_centers:
                    distance = np.sqrt(
                        (worker_top[0] - helmet_center[0]) ** 2 +
                        (worker_top[1] - helmet_center[1]) ** 2
                    )

                    proximity_threshold = worker['h'] * 0.8

                    if helmet_center[1] < worker_top[1] and distance < proximity_threshold:
                        has_helmet = True
                        break

                if not has_helmet:
                    violations.append('MISSING_HELMET')
                    print(f"⚠️ SAFETY VIOLATION: Worker without helmet detected!")

            if len(workers) > 0 and len(helmets) == 0:
                violations.append('NO_SAFETY_GEAR_DETECTED')
                print(f"🚨 CRITICAL: NO HELMETS DETECTED - {len(workers)} workers visible!")

        except Exception as e:
            print(f"Safety analysis error: {e}")

        return violations

    def annotate_frame(self, frame, results):
        """Annotate frame with detection results"""
        annotated = frame.copy()
        height, width = frame.shape[:2]

        # Draw header
        cv2.rectangle(annotated, (0, 0), (width, 100), (0, 0, 0), -1)

        violations = results.get('violations', [])
        status_color = (0, 255, 0) if not violations else (0, 0, 255)
        status_text = "✅ NO VIOLATIONS" if not violations else f"🚨 VIOLATIONS: {len(violations)}"

        cv2.putText(annotated, status_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)

        helmet_coverage = results.get('confidence', 0)
        stats_text = f"Workers: {results.get('workers_detected', 0)} | Helmets: {results.get('helmets_detected', 0)} | Coverage: {int(helmet_coverage*100)}% | Method: {results.get('detection_method', 'primary')}"
        cv2.putText(annotated, stats_text, (10, 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

        cv2.putText(annotated, f"Time: {datetime.utcnow().strftime('%H:%M:%S')}",
                   (width - 300, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Draw helmets in green
        for helmet in results.get('helmet_boxes', []):
            x, y, w, h = helmet.get('x', 0), helmet.get('y', 0), helmet.get('w', 0), helmet.get('h', 0)
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(annotated, 'HELMET', (x, max(0, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Draw workers with green/red boxes based on PPE compliance
        for worker in results.get('worker_boxes', []):
            x, y, w, h = worker.get('x', 0), worker.get('y', 0), worker.get('w', 0), worker.get('h', 0)
            worker_center = worker.get('center', (x + w // 2, y + h // 2))
            has_helmet = False
            helmet_centers = [h.get('center') for h in results.get('helmet_boxes', []) if h.get('center')]
            for helmet_center in helmet_centers:
                distance = np.linalg.norm(np.array(worker_center) - np.array(helmet_center))
                if distance < max(w, h) * 0.8:
                    has_helmet = True
                    break

            box_color = (0, 255, 0) if has_helmet else (0, 0, 255)
            label = 'SAFE' if has_helmet else 'NO PPE'
            cv2.rectangle(annotated, (x, y), (x + w, y + h), box_color, 2)
            cv2.putText(annotated, label, (x, max(0, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, box_color, 2)

        return annotated

    def _update_history(self, results):
        """Update detection history"""
        timestamp = datetime.utcnow()
        self.detect_history[timestamp] = results


# For backward compatibility
SafetyDetector = ImprovedSafetyDetector