"""
Scalable Multi-Camera Coordinator
Manages 30-40+ simultaneous camera streams with resource optimization
Integrates with enhanced risk prediction and notification system
"""

import logging
import threading
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import queue
import psutil
import numpy as np

logger = logging.getLogger(__name__)


class CameraStreamOptimizer:
    """Optimize resource usage across multiple camera streams"""
    
    def __init__(self, max_cameras: int = 40):
        """Initialize optimizer"""
        self.max_cameras = max_cameras
        self.active_cameras = {}
        self.resource_limits = {
            'max_cpu_percent': 80,
            'max_memory_mb': 4000,
            'max_threads': 50,
        }
        self.monitoring_enabled = True
    
    def get_system_resources(self) -> Dict:
        """Get current system resource usage"""
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_mb': psutil.virtual_memory().used / 1024 / 1024,
            'memory_percent': psutil.virtual_memory().percent,
            'thread_count': threading.active_count(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024,
            'timestamp': datetime.utcnow().isoformat(),
        }
    
    def calculate_optimal_fps(self) -> int:
        """Dynamically calculate optimal FPS based on system load"""
        
        resources = self.get_system_resources()
        base_fps = 30
        
        # Reduce FPS if system is loaded
        if resources['cpu_percent'] > 80:
            base_fps = 15
        elif resources['cpu_percent'] > 60:
            base_fps = 20
        elif resources['memory_percent'] > 80:
            base_fps = 15
        
        return base_fps
    
    def calculate_optimal_resolution(self) -> Tuple[int, int]:
        """Dynamically calculate resolution based on system load"""
        
        resources = self.get_system_resources()
        
        # Default resolution
        width, height = 640, 480
        
        # Reduce if system loaded
        if resources['cpu_percent'] > 80 or resources['memory_percent'] > 85:
            width, height = 416, 312
        elif resources['cpu_percent'] > 70 or resources['memory_percent'] > 75:
            width, height = 528, 396
        
        return width, height
    
    def should_skip_frame(self, camera_id: int) -> bool:
        """Determine if frame should be skipped to reduce load"""
        
        resources = self.get_system_resources()
        
        # Skip frames if system is heavily loaded
        if resources['cpu_percent'] > 85:
            return True
        if resources['memory_percent'] > 90:
            return True
        
        return False


class MultiCameraCoordinator:
    """
    Coordinates monitoring of 30-40+ cameras
    Manages resource allocation, frame routing, and risk triggering
    """
    
    def __init__(self, max_cameras: int = 40, risk_engine=None, notification_service=None):
        """
        Initialize coordinator
        
        Args:
            max_cameras: Maximum cameras to handle simultaneously
            risk_engine: Risk prediction engine for scoring
            notification_service: Notification service for alerts
        """
        self.max_cameras = max_cameras
        self.risk_engine = risk_engine
        self.notification_service = notification_service
        
        # Camera management
        self.cameras = {}  # camera_id -> CameraMonitor
        self.camera_status = {}  # camera_id -> status info
        self.camera_alerts = defaultdict(list)  # camera_id -> [alerts]
        
        # Thread management
        self.executor = ThreadPoolExecutor(max_workers=max_cameras)
        self.optimizer = CameraStreamOptimizer(max_cameras)
        
        # Queuing system
        self.frame_queue = queue.PriorityQueue()
        self.detection_queue = queue.Queue()
        self.alert_queue = queue.Queue()
        
        # Statistics
        self.stats = {
            'total_frames': 0,
            'total_detections': 0,
            'total_alerts': defaultdict(int),
            'start_time': datetime.utcnow(),
            'camera_stats': defaultdict(lambda: {
                'frames_processed': 0,
                'detections': 0,
                'alerts': 0,
                'uptime': 0,
                'errors': 0,
            })
        }
        
        # Control
        self.running = False
        self.lock = threading.RLock()
        
        # Background threads
        self.monitor_thread = None
        self.alert_processor_thread = None
    
    def add_camera(self, camera_id: int, config: Dict) -> bool:
        """Add a camera to monitor"""
        
        if len(self.cameras) >= self.max_cameras:
            logger.warning(f"Cannot add camera {camera_id}: max capacity ({self.max_cameras}) reached")
            return False
        
        try:
            with self.lock:
                self.cameras[camera_id] = {
                    'id': camera_id,
                    'config': config,
                    'status': 'initializing',
                    'frame_count': 0,
                    'last_frame_time': None,
                    'detections': [],
                    'errors': 0,
                }
                
                self.camera_status[camera_id] = {
                    'connected': False,
                    'fps': 0,
                    'frame_drop_rate': 0,
                    'last_update': datetime.utcnow(),
                    'uptime_seconds': 0,
                }
                
                logger.info(f"Camera {camera_id} added successfully")
                return True
        
        except Exception as e:
            logger.error(f"Error adding camera {camera_id}: {e}")
            return False
    
    def remove_camera(self, camera_id: int) -> bool:
        """Remove a camera from monitoring"""
        
        try:
            with self.lock:
                if camera_id in self.cameras:
                    del self.cameras[camera_id]
                    if camera_id in self.camera_status:
                        del self.camera_status[camera_id]
                    logger.info(f"Camera {camera_id} removed")
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error removing camera {camera_id}: {e}")
            return False
    
    def start_monitoring(self):
        """Start monitoring all cameras"""
        
        if self.running:
            logger.warning("Monitoring already running")
            return
        
        self.running = True
        
        # Start background processor
        self.alert_processor_thread = threading.Thread(
            target=self._alert_processor_loop,
            name="AlertProcessor",
            daemon=True
        )
        self.alert_processor_thread.start()
        
        # Start resource monitor
        self.monitor_thread = threading.Thread(
            target=self._resource_monitor_loop,
            name="ResourceMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        
        # Start camera monitoring tasks
        for camera_id in list(self.cameras.keys()):
            self.executor.submit(self._monitor_camera, camera_id)
        
        logger.info(f"Multi-camera monitoring started for {len(self.cameras)} cameras")
    
    def stop_monitoring(self):
        """Stop monitoring all cameras"""
        
        self.running = False
        self.executor.shutdown(wait=False)
        logger.info("Multi-camera monitoring stopped")
    
    def process_frame(self, camera_id: int, frame: np.ndarray,
                     detections: List[Dict]) -> Optional[Dict]:
        """
        Process frame and detections for a camera
        
        Args:
            camera_id: Camera identifier
            frame: Frame data
            detections: List of detections from AI model
        
        Returns:
            Risk assessment if alert triggered, None otherwise
        """
        
        with self.lock:
            if camera_id not in self.cameras:
                return None
            
            # Update statistics
            self.stats['total_frames'] += 1
            self.stats['camera_stats'][camera_id]['frames_processed'] += 1
            
            # Check resource utilization
            if self.optimizer.should_skip_frame(camera_id):
                return None
            
            # Process detections
            highest_risk = None
            
            for detection in detections:
                # Score risk
                if self.risk_engine:
                    risk_assessment = self.risk_engine.predict_risk(
                        detection=detection,
                        location_id=camera_id,
                        worker_id=detection.get('worker_id')
                    )
                else:
                    risk_assessment = {
                        'risk_score': detection.get('confidence', 0) * 100,
                        'severity': 'HIGH' if detection.get('confidence', 0) > 0.8 else 'MEDIUM',
                        'action_required': detection.get('confidence', 0) > 0.8,
                    }
                
                # Track detections
                self.stats['total_detections'] += 1
                self.stats['camera_stats'][camera_id]['detections'] += 1
                
                # Store highest risk
                if highest_risk is None or risk_assessment.get('risk_score', 0) > highest_risk.get('risk_score', 0):
                    highest_risk = risk_assessment
                    highest_risk['camera_id'] = camera_id
                    highest_risk['timestamp'] = datetime.utcnow()
            
            # Trigger alert if needed
            if highest_risk and highest_risk.get('action_required'):
                self._queue_alert(camera_id, highest_risk)
                self.stats['camera_stats'][camera_id]['alerts'] += 1
            
            return highest_risk
    
    def _queue_alert(self, camera_id: int, risk_data: Dict):
        """Queue alert for processing"""
        
        try:
            # Add to alert queue (non-blocking)
            self.alert_queue.put_nowait({
                'camera_id': camera_id,
                'risk_data': risk_data,
                'queued_at': datetime.utcnow(),
            })
            
            self.stats['total_alerts'][risk_data.get('severity', 'MEDIUM')] += 1
            
        except queue.Full:
            logger.warning("Alert queue full, some alerts may be missed")
    
    def _alert_processor_loop(self):
        """Process queued alerts"""
        
        while self.running:
            try:
                alert = self.alert_queue.get(timeout=1)
                self._process_alert(alert)
            
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in alert processor: {e}")
    
    def _process_alert(self, alert: Dict):
        """Process individual alert"""
        
        try:
            camera_id = alert['camera_id']
            risk_data = alert['risk_data']
            
            # Add to camera alerts
            self.camera_alerts[camera_id].append({
                'timestamp': datetime.utcnow(),
                'risk_data': risk_data,
                'notified': False,
            })
            
            # Send notifications if enabled
            if self.notification_service:
                self._send_notifications_for_alert(risk_data)
            
            logger.info(f"Alert processed: Camera {camera_id}, Severity: {risk_data.get('severity')}")
        
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
    
    def _send_notifications_for_alert(self, risk_data: Dict):
        """Send notifications for critical alerts"""
        
        severity = risk_data.get('severity', 'MEDIUM')
        
        # Only send notifications for MEDIUM and above
        if severity not in ['MEDIUM', 'HIGH', 'CRITICAL']:
            return
        
        # This integration point would connect to the notification service
        logger.info(f"Sending notifications for {severity} alert")
    
    def _monitor_camera(self, camera_id: int):
        """Monitor a single camera (runs in thread)"""
        
        try:
            logger.info(f"Started monitoring camera {camera_id}")
            
            while self.running and camera_id in self.cameras:
                try:
                    # Get current optimal settings
                    fps = self.optimizer.calculate_optimal_fps()
                    resolution = self.optimizer.calculate_optimal_resolution()
                    
                    # Update camera status
                    self.camera_status[camera_id]['fps'] = fps
                    self.camera_status[camera_id]['resolution'] = resolution
                    self.camera_status[camera_id]['last_update'] = datetime.utcnow()
                    
                    # Sleep to control FPS
                    time.sleep(1 / fps)
                
                except Exception as e:
                    logger.error(f"Error monitoring camera {camera_id}: {e}")
                    self.cameras[camera_id]['errors'] += 1
                    time.sleep(5)
        
        finally:
            logger.info(f"Stopped monitoring camera {camera_id}")
    
    def _resource_monitor_loop(self):
        """Monitor system resources"""
        
        check_interval = 5  # seconds
        
        while self.running:
            try:
                resources = self.optimizer.get_system_resources()
                
                # Log warnings if resources exceeded
                if resources['cpu_percent'] > self.optimizer.resource_limits['max_cpu_percent']:
                    logger.warning(f"High CPU usage: {resources['cpu_percent']:.1f}%")
                
                if resources['memory_percent'] > 80:
                    logger.warning(f"High memory usage: {resources['memory_percent']:.1f}%")
                
                # Adjust monitoring intensity
                if resources['cpu_percent'] > 85:
                    logger.warning("System overload detected - reducing frame rate")
                    check_interval = 2
                elif resources['cpu_percent'] < 60:
                    check_interval = 5
                
                time.sleep(check_interval)
            
            except Exception as e:
                logger.error(f"Error in resource monitor: {e}")
                time.sleep(5)
    
    def get_coordinator_status(self) -> Dict:
        """Get overall coordinator status"""
        
        uptime = (datetime.utcnow() - self.stats['start_time']).total_seconds()
        
        return {
            'running': self.running,
            'active_cameras': len(self.cameras),
            'max_cameras': self.max_cameras,
            'uptime_seconds': uptime,
            'total_frames': self.stats['total_frames'],
            'total_detections': self.stats['total_detections'],
            'alerts': dict(self.stats['total_alerts']),
            'resources': self.optimizer.get_system_resources(),
            'camera_count': len(self.cameras),
            'active_threads': threading.active_count(),
        }
    
    def get_camera_status(self, camera_id: int) -> Optional[Dict]:
        """Get status of specific camera"""
        
        if camera_id not in self.cameras:
            return None
        
        with self.lock:
            camera = self.cameras[camera_id]
            status = self.camera_status.get(camera_id, {})
            stats = self.stats['camera_stats'].get(camera_id, {})
            
            return {
                'camera_id': camera_id,
                'config': camera.get('config'),
                'status': camera.get('status'),
                'connection': status,
                'statistics': stats,
                'alert_count': len(self.camera_alerts.get(camera_id, [])),
                'recent_alerts': self.camera_alerts.get(camera_id, [])[-5:],  # Last 5
            }
    
    def get_all_cameras_status(self) -> Dict:
        """Get status of all cameras"""
        
        cameras_status = {}
        
        for camera_id in list(self.cameras.keys()):
            cameras_status[camera_id] = self.get_camera_status(camera_id)
        
        return cameras_status


# Global instance
multi_camera_coordinator = None


def initialize_multi_camera_coordinator(max_cameras: int = 40, risk_engine=None, notification_service=None) -> MultiCameraCoordinator:
    """Initialize global coordinator instance"""
    
    global multi_camera_coordinator
    multi_camera_coordinator = MultiCameraCoordinator(
        max_cameras=max_cameras,
        risk_engine=risk_engine,
        notification_service=notification_service
    )
    return multi_camera_coordinator
