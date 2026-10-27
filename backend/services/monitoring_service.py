"""
Camera Monitoring Service
Continuous 24/7 monitoring with real-time frame capture and detection
"""

import logging
import threading
import time
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque
from queue import Queue, Empty
import uuid

try:
    from improved_safety_detection import ImprovedSafetyDetector
except Exception:
    ImprovedSafetyDetector = None

logger = logging.getLogger(__name__)

class CameraMonitor:
    """Monitor a single camera with continuous frame capture"""
    
    def __init__(self, camera_id: int, source: str, location: str = None,
                 detection_interval: int = 1, frame_buffer_size: int = 300):
        """
        Initialize camera monitor
        
        Args:
            camera_id: Unique camera identifier
            source: Video source (0 for webcam, URL for IP camera)
            location: Camera location name
            detection_interval: Detection interval in seconds (default 1)
            frame_buffer_size: Max frames to buffer
        """
        self.camera_id = camera_id
        self.source = source
        self.location = location or f"Camera {camera_id}"
        self.detection_interval = detection_interval
        self.frame_buffer_size = frame_buffer_size
        
        # Frame management
        self.frame_buffer = deque(maxlen=frame_buffer_size)
        self.current_frame = None
        self.frame_timestamp = None
        self.detection_results = None
        self.detection_timestamp = None
        
        # Monitoring state
        self.is_running = False
        self.is_connected = False
        self.capture_thread = None
        self.detection_thread = None
        
        # Statistics
        self.total_frames_captured = 0
        self.total_detections = 0
        self.average_fps = 0
        self.last_error = None
        self.errors_count = 0
        self.uptime_start = None
        self.alert_active = False
        self.current_alerts = []
        self.annotated_frame = None
        
        # Detection helper
        self.detector = ImprovedSafetyDetector() if CV2_AVAILABLE and ImprovedSafetyDetector is not None else None
        
        # Locking
        self.lock = threading.RLock()
        
        # Queues
        self.frame_queue = Queue(maxsize=10)
        self.detection_queue = Queue()
    
    def start(self):
        """Start monitoring"""
        try:
            if self.is_running:
                logger.warning(f"Camera {self.camera_id} already running")
                return
            
            self.is_running = True
            self.uptime_start = datetime.utcnow()
            
            # Start capture thread
            self.capture_thread = threading.Thread(
                target=self._capture_loop,
                name=f"CameraCapture-{self.camera_id}",
                daemon=True
            )
            self.capture_thread.start()
            
            # Start detection thread
            self.detection_thread = threading.Thread(
                target=self._detection_loop,
                name=f"CameraDetection-{self.camera_id}",
                daemon=True
            )
            self.detection_thread.start()
            
            logger.info(f"Camera {self.camera_id} monitoring started")
            
        except Exception as e:
            logger.error(f"Error starting camera monitor: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop monitoring"""
        try:
            self.is_running = False
            
            # Wait for threads to finish
            if self.capture_thread and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=5)
            
            if self.detection_thread and self.detection_thread.is_alive():
                self.detection_thread.join(timeout=5)
            
            logger.info(f"Camera {self.camera_id} monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping camera monitor: {e}")
    
    def _capture_loop(self):
        """Continuous frame capture loop"""
        cap = None
        frame_count = 0
        start_time = time.time()
        
        try:
            # Open video source
            cap = cv2.VideoCapture(self.source)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video source: {self.source}")
            
            # Set camera properties for better performance
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_connected = True
            logger.info(f"Camera {self.camera_id} connected successfully")
            
            while self.is_running:
                try:
                    ret, frame = cap.read()
                    
                    if not ret:
                        self.errors_count += 1
                        if self.errors_count > 10:
                            raise ValueError("Cannot read frames from camera")
                        time.sleep(0.1)
                        continue
                    
                    # Reset error count on successful read
                    self.errors_count = 0
                    
                    # Resize if needed (important for performance)
                    frame = cv2.resize(frame, (640, 480))
                    
                    # Update current frame
                    with self.lock:
                        self.current_frame = frame.copy()
                        self.frame_timestamp = datetime.utcnow()
                        self.frame_buffer.append(frame.copy())
                    
                    # Add to detection queue
                    try:
                        self.frame_queue.put_nowait((frame.copy(), datetime.utcnow()))
                    except:
                        pass  # Queue full, skip this frame
                    
                    frame_count += 1
                    self.total_frames_captured = frame_count
                    
                    # Calculate FPS every 30 frames
                    if frame_count % 30 == 0:
                        elapsed = time.time() - start_time
                        self.average_fps = frame_count / elapsed
                    
                    # ~1 second interval between captures
                    # (adjust based on camera FPS)
                    
                except Exception as e:
                    logger.debug(f"Frame capture error: {e}")
                    time.sleep(0.01)
        
        except Exception as e:
            self.is_connected = False
            self.last_error = str(e)
            logger.error(f"Camera {self.camera_id} capture error: {e}")
        
        finally:
            if cap:
                cap.release()
    
    def _detection_loop(self):
        """Detection processing loop"""
        last_detection = 0
        
        while self.is_running:
            try:
                # Check if enough time has passed since last detection
                current_time = time.time()
                if current_time - last_detection < self.detection_interval:
                    time.sleep(0.1)
                    continue
                
                # Get frame from queue
                try:
                    frame, timestamp = self.frame_queue.get(timeout=1)
                except Empty:
                    continue
                
                # Process frame with helmet/safety detection
                if self.detector:
                    results = self.detector.detect(frame.copy())
                else:
                    results = {
                        'workers_detected': 0,
                        'helmets_detected': 0,
                        'violations': [],
                        'timestamp': timestamp,
                        'camera_id': self.camera_id
                    }

                annotated = None
                if self.detector:
                    try:
                        annotated = self.detector.annotate_frame(frame.copy(), results)
                    except Exception as e:
                        logger.debug(f"Annotation failed: {e}")
                        annotated = frame.copy()

                with self.lock:
                    self.detection_results = results
                    self.detection_timestamp = datetime.utcnow()
                    self.current_alerts = results.get('violations', []) or []
                    self.alert_active = bool(self.current_alerts)
                    self.annotated_frame = annotated
                    self.total_detections += 1

                last_detection = current_time
                
            except Exception as e:
                logger.debug(f"Detection error: {e}")
                time.sleep(0.1)
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get current frame"""
        with self.lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def get_frame_jpeg(self) -> Optional[bytes]:
        """Get current frame as JPEG bytes"""
        try:
            with self.lock:
                frame = self.annotated_frame if self.annotated_frame is not None else self.get_current_frame()
            if frame is None:
                return None
            
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                return buffer.tobytes()
            return None
        except Exception as e:
            logger.error(f"Error encoding frame: {e}")
            return None
    
    def get_detection_results(self) -> Optional[Dict]:
        """Get latest detection results"""
        with self.lock:
            return self.detection_results
    
    def get_status(self) -> Dict:
        """Get camera status"""
        uptime = None
        if self.uptime_start:
            uptime = (datetime.utcnow() - self.uptime_start).total_seconds()
        
        return {
            'camera_id': self.camera_id,
            'location': self.location,
            'is_running': self.is_running,
            'is_connected': self.is_connected,
            'total_frames': self.total_frames_captured,
            'total_detections': self.total_detections,
            'average_fps': round(self.average_fps, 2),
            'uptime_seconds': uptime,
            'last_frame_time': self.frame_timestamp.isoformat() if self.frame_timestamp else None,
            'last_detection_time': self.detection_timestamp.isoformat() if self.detection_timestamp else None,
            'alert_active': self.alert_active,
            'current_alerts': self.current_alerts,
            'detection_results': self.detection_results,
            'errors': self.errors_count,
            'last_error': self.last_error
        }

class ContinuousMonitoringService:
    """Manage multiple cameras with continuous 24/7 monitoring"""
    
    def __init__(self, max_cameras: int = 16):
        """
        Initialize monitoring service
        
        Args:
            max_cameras: Maximum number of cameras
        """
        self.max_cameras = max_cameras
        self.cameras: Dict[int, CameraMonitor] = {}
        self.monitoring_enabled = False
        self.lock = threading.RLock()
        self.health_check_thread = None
        self.monitoring_start_time = None
    
    def add_camera(self, camera_id: int, source: str, location: str = None,
                   auto_start: bool = True) -> bool:
        """
        Add camera for monitoring
        
        Args:
            camera_id: Unique camera ID
            source: Video source
            location: Camera location
            auto_start: Automatically start monitoring
        
        Returns:
            True if successful
        """
        try:
            with self.lock:
                if camera_id in self.cameras:
                    logger.warning(f"Camera {camera_id} already exists")
                    return False
                
                if len(self.cameras) >= self.max_cameras:
                    logger.error(f"Maximum cameras ({self.max_cameras}) reached")
                    return False
                
                monitor = CameraMonitor(camera_id, source, location)
                self.cameras[camera_id] = monitor
                
                if auto_start and self.monitoring_enabled:
                    monitor.start()
                
                logger.info(f"Camera {camera_id} added: {location}")
                return True
        
        except Exception as e:
            logger.error(f"Error adding camera: {e}")
            return False
    
    def remove_camera(self, camera_id: int) -> bool:
        """Stop and remove camera"""
        try:
            with self.lock:
                if camera_id not in self.cameras:
                    return False
                
                camera = self.cameras[camera_id]
                camera.stop()
                del self.cameras[camera_id]
                
                logger.info(f"Camera {camera_id} removed")
                return True
        
        except Exception as e:
            logger.error(f"Error removing camera: {e}")
            return False
    
    def start_monitoring(self):
        """Start all cameras monitoring"""
        try:
            with self.lock:
                self.monitoring_enabled = True
                self.monitoring_start_time = datetime.utcnow()
                
                for camera in self.cameras.values():
                    if not camera.is_running:
                        camera.start()
                
                # Start health check thread
                if not self.health_check_thread or not self.health_check_thread.is_alive():
                    self.health_check_thread = threading.Thread(
                        target=self._health_check_loop,
                        name="MonitoringHealthCheck",
                        daemon=True
                    )
                    self.health_check_thread.start()
                
                logger.info(f"Started monitoring {len(self.cameras)} cameras")
        
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop all cameras monitoring"""
        try:
            with self.lock:
                self.monitoring_enabled = False
                
                for camera in self.cameras.values():
                    if camera.is_running:
                        camera.stop()
                
                logger.info("Stopped monitoring all cameras")
        
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
    
    def get_all_cameras_status(self) -> List[Dict]:
        """Get status of all cameras"""
        with self.lock:
            return [camera.get_status() for camera in self.cameras.values()]
    
    def get_camera_status(self, camera_id: int) -> Optional[Dict]:
        """Get status of specific camera"""
        with self.lock:
            if camera_id not in self.cameras:
                return None
            return self.cameras[camera_id].get_status()
    
    def get_all_detection_results(self) -> List[Dict]:
        """Get latest detection results from all cameras"""
        with self.lock:
            results = []
            for camera in self.cameras.values():
                detection = camera.get_detection_results()
                if detection:
                    results.append(detection)
            return results
    
    def get_camera_frame_jpeg(self, camera_id: int) -> Optional[bytes]:
        """Get current frame from camera as JPEG"""
        with self.lock:
            if camera_id not in self.cameras:
                return None
            return self.cameras[camera_id].get_frame_jpeg()
    
    def get_monitoring_status(self) -> Dict:
        """Get overall monitoring status"""
        with self.lock:
            uptime = None
            if self.monitoring_start_time:
                uptime = (datetime.utcnow() - self.monitoring_start_time).total_seconds()
            
            total_frames = sum(c.total_frames_captured for c in self.cameras.values())
            total_detections = sum(c.total_detections for c in self.cameras.values())
            connected_cameras = sum(1 for c in self.cameras.values() if c.is_connected)
            
            return {
                'monitoring_enabled': self.monitoring_enabled,
                'total_cameras': len(self.cameras),
                'connected_cameras': connected_cameras,
                'total_frames_captured': total_frames,
                'total_detections': total_detections,
                'uptime_seconds': uptime,
                'start_time': self.monitoring_start_time.isoformat() if self.monitoring_start_time else None,
                'active_alerts': sum(1 for camera in self.cameras.values() if camera.alert_active)
            }
    
    def _health_check_loop(self):
        """Monitor health of all cameras"""
        while self.monitoring_enabled:
            try:
                with self.lock:
                    for camera in self.cameras.values():
                        if not camera.is_running and self.monitoring_enabled:
                            logger.warning(f"Camera {camera.camera_id} stopped, restarting...")
                            camera.start()
                
                # Check every 5 seconds
                time.sleep(5)
            
            except Exception as e:
                logger.error(f"Health check error: {e}")
                time.sleep(5)
