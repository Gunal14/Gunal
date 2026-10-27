"""
Safety Detection Module using OpenCV and pre-trained models
Detects helmet usage, PPE compliance, and safety violations
"""

import cv2
import numpy as np
import os
from datetime import datetime

class SafetyDetector:
    """
    Main safety detection class using OpenCV and cascade/DNN models
    Detects helmets, workers, and safety violations
    """
    
    def __init__(self, model_type='cascade', debug_mode=False):
        """
        Initialize detector
        model_type: 'cascade' for Haar Cascade, 'yolo' for YOLO, 'ssd' for SSD
        debug_mode: Enable debug output and visualizations
        """
        self.model_type = model_type
        self.debug_mode = debug_mode
        self.detect_history = {}
        self.init_models()
        
        # Safety violation thresholds
        self.helmet_confidence_threshold = 0.5
        self.worker_detection_threshold = 0.5
        self.alert_cooldown = 5  # seconds between same type alerts
        
    def init_models(self):
        """Initialize detection models"""
        try:
            # Cascade classifiers for basic detection
            cascade_path = cv2.data.haarcascades
            self.face_cascade = cv2.CascadeClassifier(
                os.path.join(cascade_path, 'haarcascade_frontalface_default.xml'))
            
            # Load pre-trained models if available
            self.net = None
            self.load_pretrained_models()
            
        except Exception as e:
            print(f"Warning: Could not load all models: {e}")
            # Continue with basic cascade detection
    
    def load_pretrained_models(self):
        """Load pre-trained DNN models"""
        try:
            # Example: Load MobileNet-SSD for object detection
            modelFile = "opencv_model/MobileNetSSD_deploy.caffemodel"
            configFile = "opencv_model/MobileNetSSD_deploy.prototxt.txt"
            
            if os.path.exists(modelFile) and os.path.exists(configFile):
                self.net = cv2.dnn.readNetFromCaffe(configFile, modelFile)
                print("Loaded MobileNet SSD model")
        except:
            print("Pre-trained models not found. Using cascade classifiers.")
    
    def detect(self, frame):
        """
        Main detection method
        Returns detection results with violations
        """
        results = {
            'workers_detected': 0,
            'helmets_detected': 0,
            'violations': [],
            'confidence': 0.0,
            'timestamp': datetime.utcnow().isoformat(),
            'frame_shape': frame.shape
        }
        
        try:
            # Preprocess frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect workers/people using cascade
            workers = self._detect_workers(gray)
            results['workers_detected'] = len(workers)
            
            # Detect helmets
            helmets = self._detect_helmets(gray, frame)
            results['helmets_detected'] = len(helmets)
            
            # Analyze safety compliance
            violations = self._analyze_safety(workers, helmets, frame)
            results['violations'] = violations
            
            # Calculate confidence score
            if results['workers_detected'] > 0:
                results['confidence'] = results['helmets_detected'] / results['workers_detected']
            
            # Store detection results
            self._update_history(results)
            
        except Exception as e:
            print(f"Detection error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _detect_workers(self, gray):
        """Detect workers/people in frame using cascade classifier with fallback"""
        workers = []
        try:
            # Primary detection: Face detection (more reliable for detecting people)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,  # Slightly more sensitive
                minNeighbors=4,    # Reduce to 4 for better detection
                minSize=(25, 25),
                maxSize=(400, 400),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Convert faces to worker bounding boxes (expand face region for full body)
            for (x, y, w, h) in faces:
                # Expand detection to include upper body/head area
                expanded_height = int(h * 3)  # Expand more for full upper body
                expanded_width = int(w * 1.5)
                
                worker_box = {
                    'x': max(0, x - int(w * 0.25)),
                    'y': max(0, y - int(h * 0.5)),
                    'w': expanded_width,
                    'h': expanded_height,
                    'center': (x + w // 2, y + h // 2),
                    'face_rect': (x, y, w, h),
                    'confidence': 0.8
                }
                workers.append(worker_box)
            
            # If face detection returns few results, try alternative approach
            if len(workers) == 0:
                # Alternative: Look for skin color regions (fallback method)
                workers = self._detect_workers_by_skin_tone(gray, frame)
            
            # If still no workers, try motion detection as last resort
            if len(workers) == 0:
                workers = self._detect_workers_by_motion(frame)
            
        except Exception as e:
            print(f"Worker detection error: {e}")
        
        return workers
    
    def _detect_workers_by_skin_tone(self, gray, frame):
        """Alternative worker detection using skin tone - now with frame"""
        workers = []
        try:
            # Convert to HSV for skin tone detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Skin tone ranges
            lower_skin = np.array([0, 20, 70])
            upper_skin = np.array([20, 255, 255])
            
            # Create skin mask
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # Apply morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Find contours
            contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter by reasonable person size
                if 1000 < area < 50000:  # Person-sized areas
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check aspect ratio for person shape
                    if h > 0 and 0.3 < w / h < 1.0:  # Persons are taller than wide
                        worker_box = {
                            'x': x,
                            'y': y,
                            'w': w,
                            'h': h,
                            'center': (x + w // 2, y + h // 2),
                            'face_rect': (x, y, w, h),  # Use full body as face approximation
                            'confidence': 0.6,
                            'method': 'skin_tone'
                        }
                        workers.append(worker_box)
        
        except Exception as e:
            print(f"Skin tone detection error: {e}")
        
        return workers
    
    def _detect_workers_by_motion(self, frame):
        """Motion-based worker detection as last resort"""
        workers = []
        
        try:
            # Initialize background subtractor if not exists
            if not hasattr(self, 'bg_subtractor'):
                self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                    history=100, varThreshold=50, detectShadows=True)
            
            # Apply background subtraction
            fg_mask = self.bg_subtractor.apply(frame)
            
            # Apply morphological operations to clean up
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=1)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter by motion area size
                if 500 < area < 30000:  # Moving object sized areas
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check aspect ratio
                    if h > 0 and 0.2 < w / h < 2.0:
                        worker_box = {
                            'x': x,
                            'y': y,
                            'w': w,
                            'h': h,
                            'center': (x + w // 2, y + h // 2),
                            'face_rect': (x, y, w, h),
                            'confidence': 0.4,
                            'method': 'motion'
                        }
                        workers.append(worker_box)
        
        except Exception as e:
            print(f"Motion detection error: {e}")
        
        return workers
    
    def _detect_helmets(self, gray, frame):
        """Detect helmets using advanced color and shape analysis"""
        helmets = []
        
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Enhanced color ranges for various helmet types
            # Yellow helmets (most common)
            lower_yellow = np.array([10, 40, 50])
            upper_yellow = np.array([40, 255, 255])
            
            # Orange helmets
            lower_orange = np.array([0, 50, 50])
            upper_orange = np.array([15, 255, 255])
            
            # White helmets
            lower_white = np.array([0, 0, 130])
            upper_white = np.array([180, 50, 255])
            
            # Red helmets
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            
            # Blue/Hard hat colors
            lower_blue = np.array([90, 50, 50])
            upper_blue = np.array([130, 255, 255])
            
            # Green helmets (safety vests often green)
            lower_green = np.array([35, 50, 50])
            upper_green = np.array([80, 255, 255])
            
            # Gray/Dark helmets
            lower_gray = np.array([0, 0, 0])
            upper_gray = np.array([180, 30, 100])
            
            # Create masks for different helmet color ranges
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            mask |= cv2.inRange(hsv, lower_yellow, upper_yellow)
            mask |= cv2.inRange(hsv, lower_orange, upper_orange)
            mask |= cv2.inRange(hsv, lower_white, upper_white)
            mask |= cv2.inRange(hsv, lower_red1, upper_red1)
            mask |= cv2.inRange(hsv, lower_red2, upper_red2)
            mask |= cv2.inRange(hsv, lower_blue, upper_blue)
            mask |= cv2.inRange(hsv, lower_green, upper_green)
            mask |= cv2.inRange(hsv, lower_gray, upper_gray)
            
            # Apply morphological operations to clean up mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Apply Gaussian blur to smoothen
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            
            # Debug: Show mask for troubleshooting
            if hasattr(self, 'debug_mode') and self.debug_mode:
                cv2.imshow("Helmet Mask", mask)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size and shape
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter by area - expanded range for better detection
                if 30 < area < 20000:  # More flexible area range
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check aspect ratio for helmet shape (more relaxed - 0.3 to 3.0)
                    if h > 0 and 0.3 < w / h < 3.0:
                        # Additional check: circularity for helmet shape
                        perimeter = cv2.arcLength(contour, True)
                        if perimeter > 0:
                            circularity = 4 * np.pi * area / (perimeter ** 2)
                            if circularity > 0.3:  # More relaxed circularity
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
            
            # If no helmets found with color detection, try shape-based detection
            if len(helmets) == 0:
                helmets = self._detect_helmets_by_shape(gray, frame)
                
        except Exception as e:
            print(f"Helmet detection error: {e}")
        
        return helmets
    
    def _detect_helmets_by_shape(self, gray, frame):
        """Fallback helmet detection using shape analysis when color fails"""
        helmets = []
        
        try:
            # Use edge detection to find circular/oval shapes
            edges = cv2.Canny(gray, 50, 150)
            
            # Apply morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            # Find contours in edges
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Look for helmet-sized objects
                if 100 < area < 10000:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check aspect ratio for helmet-like shapes
                    if h > 0 and 0.4 < w / h < 2.5:
                        # Check circularity
                        perimeter = cv2.arcLength(contour, True)
                        if perimeter > 0:
                            circularity = 4 * np.pi * area / (perimeter ** 2)
                            if circularity > 0.5:  # Look for more circular shapes
                                # Additional check: position should be in upper part of frame
                                frame_height = frame.shape[0]
                                if y < frame_height * 0.7:  # Helmets typically in upper 70% of frame
                                    helmet_box = {
                                        'x': x,
                                        'y': y,
                                        'w': w,
                                        'h': h,
                                        'area': area,
                                        'center': (x + w // 2, y + h // 2),
                                        'circularity': circularity,
                                        'method': 'shape'
                                    }
                                    helmets.append(helmet_box)
        
        except Exception as e:
            print(f"Shape-based helmet detection error: {e}")
        
        return helmets
    
    def _analyze_safety(self, workers, helmets, frame):
        """Analyze safety compliance and identify violations with improved matching"""
        violations = []
        
        try:
            if len(workers) == 0:
                return violations
            
            helmet_centers = [h['center'] for h in helmets]
            
            # Better helmet-worker pairing algorithm
            helmets_matched = []
            workers_without_helmets = []
            
            # Check each worker for helmet compliance
            for worker in workers:
                worker_center = worker['center']
                worker_top = (worker_center[0], worker['y'])  # Top of worker's head
                
                has_helmet = False
                closest_helmet_distance = float('inf')
                
                # Check proximity to helmets
                for i, helmet_center in enumerate(helmet_centers):
                    # Calculate distance between worker's head and helmet
                    distance = np.sqrt(
                        (worker_top[0] - helmet_center[0])**2 + 
                        (worker_top[1] - helmet_center[1])**2
                    )
                    
                    closest_helmet_distance = min(closest_helmet_distance, distance)
                    
                    # Helmet should be above worker's head and within reasonable distance
                    # Threshold is based on worker's height
                    proximity_threshold = worker['h'] * 0.6
                    
                    if (helmet_center[1] < worker_top[1] and  # Helmet above head
                        distance < proximity_threshold):
                        has_helmet = True
                        if i not in helmets_matched:
                            helmets_matched.append(i)
                        break
                
                if not has_helmet:
                    workers_without_helmets.append(worker)
            
            # Generate violations
            if len(workers_without_helmets) > 0:
                # Calculate compliance ratio
                compliance_ratio = len(helmets_matched) / len(workers)
                
                if compliance_ratio < 1.0:
                    violations.append('MISSING_HELMET')
                    print(f"   ⚠️  {len(workers_without_helmets)} worker(s) without helmet detected")
            
            # Check for workers detected but no visible helmets
            if len(workers) > 0 and len(helmets) == 0:
                violations.append('NO_SAFETY_GEAR_DETECTED')
                print(f"   ❌ NO HELMETS DETECTED - {len(workers)} workers visible")
            
            # Check for crowding/unusual activity
            if len(workers) > 10:
                violations.append('AREA_OVERCROWDED')
            
        except Exception as e:
            print(f"Safety analysis error: {e}")
        
        return violations
    
    def annotate_frame(self, frame, results):
        """
        Annotate frame with detection results and bounding boxes
        """
        annotated = frame.copy()
        
        try:
            height, width = frame.shape[:2]
            
            # Draw header with status
            cv2.rectangle(annotated, (0, 0), (width, 80), (0, 0, 0), -1)
            
            violations = results.get('violations', [])
            status_color = (0, 255, 0) if not violations else (0, 0, 255)
            status_text = "✅ NO VIOLATIONS" if not violations else f"🚨 VIOLATIONS: {', '.join(violations)}"
            
            cv2.putText(annotated, status_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
            
            # Statistics
            helmet_coverage = results.get('confidence', 0)
            stats_text = f"Workers: {results['workers_detected']} | Helmets: {results['helmets_detected']} | Coverage: {int(helmet_coverage*100)}%"
            cv2.putText(annotated, stats_text, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Calculate and display FPS
            cv2.putText(annotated, f"Time: {datetime.utcnow().strftime('%H:%M:%S')}",
                       (width - 280, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            # Draw worker detections (if available in storage)
            # This assumes _detect_workers and _detect_helmets results are stored
            try:
                gray = cv2.cvtColor(annotated, cv2.COLOR_BGR2GRAY)
                hsv = cv2.cvtColor(annotated, cv2.COLOR_BGR2HSV)
                
                # Re-detect for visualization
                workers = self._detect_workers(gray)
                helmets = self._detect_helmets(gray, annotated)
                
                # Draw helmet detections (green boxes)
                for helmet in helmets:
                    x, y, w, h = helmet['x'], helmet['y'], helmet['w'], helmet['h']
                    cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.circle(annotated, helmet['center'], 3, (0, 255, 0), -1)
                    cv2.putText(annotated, "Helmet", (x, y-5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                
                # Draw worker detections (red boxes for those without helmets, blue for those with)
                for worker in workers:
                    x, y, w, h = worker['x'], worker['y'], worker['w'], worker['h']
                    # Check if this worker has a helmet
                    has_helmet = False
                    for helmet in helmets:
                        distance = np.sqrt(
                            (worker['center'][0] - helmet['center'][0])**2 + 
                            (worker['center'][1] - helmet['center'][1])**2
                        )
                        if distance < h * 0.6:
                            has_helmet = True
                            break
                    
                    color = (255, 0, 0) if has_helmet else (0, 0, 255)  # Blue if has helmet, Red if not
                    cv2.rectangle(annotated, (x, y), (x+w, y+h), color, 2)
                    label = "✓ Protected" if has_helmet else "✗ DANGER"
                    cv2.putText(annotated, label, (x, y-5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                
            except Exception as e:
                pass  # Don't fail annotation if visualization fails
            
            # Draw safety warning if violations
            if violations:
                cv2.rectangle(annotated, (10, height-50), (width-10, height-10), (0, 0, 200), -1)
                warning_text = "⚠️  IMMEDIATE ACTION REQUIRED - SAFETY VIOLATION DETECTED"
                cv2.putText(annotated, warning_text, (20, height-20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
        except Exception as e:
            print(f"Annotation error: {e}")
        
        return annotated
    
    def _update_history(self, results):
        """Update detection history for trend analysis"""
        timestamp = datetime.utcnow()
        self.detect_history[timestamp] = results
        
        # Keep only last 100 detections in memory
        if len(self.detect_history) > 100:
            oldest_key = min(self.detect_history.keys())
            del self.detect_history[oldest_key]
    
    def get_statistics(self):
        """Get detection statistics"""
        if not self.detect_history:
            return {'avg_workers': 0, 'avg_helmets': 0, 'total_violations': 0}
        
        values = list(self.detect_history.values())
        avg_workers = sum(v['workers_detected'] for v in values) / len(values)
        avg_helmets = sum(v['helmets_detected'] for v in values) / len(values)
        total_violations = sum(len(v['violations']) for v in values)
        
        return {
            'avg_workers': avg_workers,
            'avg_helmets': avg_helmets,
            'total_violations': total_violations
        }

    def get_latest_statistics(self):
        """Get latest frame statistics (most recent detection result)"""
        if not self.detect_history:
            return {
                'workers_detected': 0,
                'helmets_detected': 0,
                'violations': [],
                'confidence': 0.0
            }

        latest_timestamp = max(self.detect_history.keys())
        latest = self.detect_history[latest_timestamp]
        return {
            'workers_detected': latest.get('workers_detected', 0),
            'helmets_detected': latest.get('helmets_detected', 0),
            'violations': latest.get('violations', []),
            'confidence': latest.get('confidence', 0.0)
        }
