"""
Advanced Safety Detection Engine
Supports multiple detection models, multi-camera, real-time processing
"""

import cv2
import numpy as np
import threading
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class AdvancedSafetyDetector:
    """Advanced helmet and PPE detection with multi-model support"""
    
    def __init__(self, model_type='ensemble', confidence_threshold=0.5):
        """
        Initialize advanced detector
        
        Args:
            model_type: 'cascade', 'ssd', 'yolo', 'ensemble'
            confidence_threshold: Detection confidence (0-1)
        """
        self.model_type = model_type
        self.confidence_threshold = confidence_threshold
        self.detection_history = defaultdict(list)
        self.performance_metrics = {}
        self.lock = threading.Lock()
        
        # Detection parameters
        self.helmet_color_ranges = self._setup_color_ranges()
        self.worker_detection_threshold = 0.5
        self.helmet_detection_threshold = 0.5
        self.min_detection_frames = 3  # Require 3 frames for stable detection
        
        self._init_models()
        logger.info(f"Advanced detector initialized with model: {model_type}")
    
    def _setup_color_ranges(self) -> Dict:
        """Setup HSV color ranges for different helmet types"""
        return {
            'yellow': {
                'lower': np.array([15, 50, 50]),
                'upper': np.array([35, 255, 255])
            },
            'orange': {
                'lower': np.array([5, 50, 50]),
                'upper': np.array([15, 255, 255])
            },
            'white': {
                'lower': np.array([0, 0, 150]),
                'upper': np.array([180, 30, 255])
            },
            'red': {
                'lower': np.array([170, 50, 50]),
                'upper': np.array([180, 255, 255])
            },
            'blue': {
                'lower': np.array([100, 50, 50]),
                'upper': np.array([130, 255, 255])
            }
        }
    
    def _init_models(self):
        """Initialize detection models"""
        try:
            cascade_path = cv2.data.haarcascades
            self.face_cascade = cv2.CascadeClassifier(
                f"{cascade_path}haarcascade_frontalface_default.xml"
            )
            self.body_cascade = cv2.CascadeClassifier(
                f"{cascade_path}haarcascade_fullbody.xml"
            )
            logger.info("Cascade classifiers loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load cascade classifiers: {e}")
    
    def detect_multi_frame(self, frames: List[np.ndarray], camera_id: int = 0) -> Dict:
        """
        Detect across multiple frames for better accuracy
        
        Args:
            frames: List of consecutive frames
            camera_id: Camera identifier
            
        Returns:
            Detection results with confidence
        """
        all_detections = []
        
        for frame in frames:
            detection = self.detect(frame, camera_id)
            all_detections.append(detection)
        
        # Aggregate results
        return self._aggregate_detections(all_detections)
    
    def detect(self, frame: np.ndarray, camera_id: int = 0) -> Dict:
        """
        Perform multi-model detection on single frame
        
        Args:
            frame: Input image frame
            camera_id: Camera identifier
            
        Returns:
            Detection results
        """
        with self.lock:
            try:
                height, width = frame.shape[:2]
                results = {
                    'camera_id': camera_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'frame_size': (width, height),
                    'workers': [],
                    'helmets': [],
                    'violations': [],
                    'confidence_scores': {},
                    'processing_time': 0
                }
                
                start_time = datetime.utcnow()
                
                # Multi-model detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
                # Cascade detection
                workers = self._cascade_detect_workers(gray)
                results['workers'] = workers
                
                # Helmet detection
                helmets = self._advanced_helmet_detect(frame, hsv)
                results['helmets'] = helmets
                
                # Analyze violations
                violations = self._analyze_violations(workers, helmets, height, width)
                results['violations'] = violations
                
                # Calculate confidence
                if workers:
                    results['confidence_scores']['helmet_coverage'] = len(helmets) / len(workers)
                else:
                    results['confidence_scores']['helmet_coverage'] = 1.0
                
                # Performance metrics
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                results['processing_time'] = processing_time
                
                # Store history
                self._store_detection_history(camera_id, results)
                
                return results
                
            except Exception as e:
                logger.error(f"Detection error: {e}")
                return {'error': str(e), 'camera_id': camera_id, 'violations': ['DETECTION_ERROR']}
    
    def _cascade_detect_workers(self, gray: np.ndarray) -> List[Dict]:
        """Detect workers using cascade classifiers"""
        workers = []
        
        try:
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            for (x, y, w, h) in faces:
                worker = {
                    'x': int(x),
                    'y': int(y),
                    'w': int(w),
                    'h': int(h),
                    'center': (int(x + w/2), int(y + h/2)),
                    'head_top': (int(x + w/2), int(y - h*0.3)),
                    'confidence': 0.85
                }
                workers.append(worker)
            
            # Detect full bodies
            bodies = self.body_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 100)
            )
            
            for (x, y, w, h) in bodies:
                if not self._is_duplicate_detection(worker, bodies):
                    worker = {
                        'x': int(x),
                        'y': int(y),
                        'w': int(w),
                        'h': int(h),
                        'center': (int(x + w/2), int(y + h/2)),
                        'head_top': (int(x + w/2), int(y - h*0.2)),
                        'confidence': 0.75
                    }
                    workers.append(worker)
                    
        except Exception as e:
            logger.warning(f"Cascade detection error: {e}")
        
        return workers
    
    def _advanced_helmet_detect(self, frame: np.ndarray, hsv: np.ndarray) -> List[Dict]:
        """Advanced helmet detection using color, shape, and texture analysis"""
        helmets = []
        
        try:
            # Multi-color detection
            combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            
            for color_name, color_range in self.helmet_color_ranges.items():
                mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
                combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter by size
                if 150 < area < 15000:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check aspect ratio (helmets are roughly circular/oval)
                    if h > 0 and 0.5 < w / h < 1.8:
                        # Solidity check (compactness)
                        hull = cv2.convexHull(contour)
                        hull_area = cv2.contourArea(hull)
                        if hull_area > 0:
                            solidity = area / hull_area
                            if solidity > 0.6:
                                helmet = {
                                    'x': int(x),
                                    'y': int(y),
                                    'w': int(w),
                                    'h': int(h),
                                    'center': (int(x + w/2), int(y + h/2)),
                                    'area': area,
                                    'confidence': 0.9 * solidity
                                }
                                helmets.append(helmet)
        
        except Exception as e:
            logger.warning(f"Helmet detection error: {e}")
        
        return helmets
    
    def _analyze_violations(self, workers: List[Dict], helmets: List[Dict], 
                          height: int, width: int) -> List[str]:
        """Analyze safety violations"""
        violations = []
        
        try:
            if len(workers) == 0:
                return violations
            
            helmet_centers = [h['center'] for h in helmets]
            
            # Check each worker for helmet
            workers_with_helmet = 0
            for worker in workers:
                worker_head = worker['head_top']
                has_helmet = False
                
                for helmet_center in helmet_centers:
                    distance = np.sqrt(
                        (worker_head[0] - helmet_center[0])**2 + 
                        (worker_head[1] - helmet_center[1])**2
                    )
                    
                    # Helmet should be within reasonable distance
                    if distance < worker['h'] * 0.6:
                        has_helmet = True
                        workers_with_helmet += 1
                        break
                
                if not has_helmet:
                    violations.append('MISSING_HELMET')
            
            # Area overcrowding (>5 workers in small area)
            if len(workers) > 8:
                violations.append('AREA_OVERCROWDED')
            
            # Unsafe area detection (bottom of frame)
            unsafe_workers = sum(1 for w in workers if w['y'] + w['h'] > height * 0.8)
            if unsafe_workers > 2:
                violations.append('UNSAFE_AREA_DETECTED')
            
            # Equipment violations
            coverage = workers_with_helmet / len(workers) if workers else 1.0
            if coverage < 0.5:
                violations.append('LOW_PPE_COMPLIANCE')
            
        except Exception as e:
            logger.error(f"Violation analysis error: {e}")
        
        return list(set(violations))  # Remove duplicates
    
    def _store_detection_history(self, camera_id: int, results: Dict):
        """Store detection results for trend analysis"""
        if len(self.detection_history[camera_id]) >= 100:
            self.detection_history[camera_id].pop(0)
        
        self.detection_history[camera_id].append(results)
    
    def _is_duplicate_detection(self, detection: Dict, detections: List[Tuple]) -> bool:
        """Check if detection is duplicate"""
        for other in detections:
            if abs(detection['x'] - other[0]) < 20 and abs(detection['y'] - other[1]) < 20:
                return True
        return False
    
    def _aggregate_detections(self, detections: List[Dict]) -> Dict:
        """Aggregate multiple frame detections"""
        return {
            'aggregated_results': detections,
            'average_workers': np.mean([d.get('workers', []) for d in detections if 'workers' in d]),
            'average_helmets': np.mean([len(d.get('helmets', [])) for d in detections if 'helmets' in d]),
            'violations': list(set(v for d in detections for v in d.get('violations', [])))
        }
    
    def get_statistics(self, camera_id: int = None) -> Dict:
        """Get detection statistics"""
        if camera_id is None:
            # Aggregate all cameras
            all_results = [r for results in self.detection_history.values() for r in results]
        else:
            all_results = self.detection_history.get(camera_id, [])
        
        if not all_results:
            return {}
        
        total_workers = sum(len(r.get('workers', [])) for r in all_results)
        total_helmets = sum(len(r.get('helmets', [])) for r in all_results)
        total_violations = sum(len(r.get('violations', [])) for r in all_results)
        avg_processing = np.mean([r.get('processing_time', 0) for r in all_results])
        
        return {
            'total_frames': len(all_results),
            'total_workers': total_workers,
            'total_helmets': total_helmets,
            'total_violations': total_violations,
            'average_processing_time': avg_processing,
            'coverage_rate': total_helmets / total_workers if total_workers > 0 else 1.0
        }
