"""
Multi-Camera Management System
Handle multiple camera feeds simultaneously
"""

import cv2
import numpy as np
import threading
import logging
from typing import Dict, List, Optional
from datetime import datetime



logger = logging.getLogger(__name__)

class MultiCameraManager:
    """Manage multiple camera feeds and coordinated detection"""
    
    def __init__(self, detector=None, max_cameras=30):
        """
        Initialize multi-camera manager
        
        Args:
            detector: Detection engine instance
        """
        self.detector = detector
        self.max_cameras = max_cameras

        self.cameras = {}
        self.active_cameras = set()

        self.lock = threading.Lock()
        
        self.frame_buffers = {}
        self.detection_results = {}
        
 
        
    def add_camera(self, camera_id: int, camera_config: Dict) -> bool:
        """
        Add camera to system

               if len(self.cameras) >= self.max_cameras:
    logger.error("Maximum camera limit reached")
    return False

        
        Args:
            camera_id: Unique camera identifier
            camera_config: Configuration dict with url/id, resolution, fps, etc.
        
        Returns:
            True if successful
        """
        try:
            source = camera_config.get('source', camera_id)
            
            cap = cv2.VideoCapture(source)
            if not cap.isOpened():
                logger.error(f"Cannot open camera {camera_id}")
                return False
            
            # Set properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_config.get('width', 640))
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_config.get('height', 480))
            cap.set(cv2.CAP_PROP_FPS, camera_config.get('fps', 30))
            
            with self.lock:
                self.cameras[camera_id] = {
                    'capture': cap,
                    'config': camera_config,
                    'active': False,
                    'location': camera_config.get('location', f'Camera {camera_id}'),
                    'added_at': datetime.utcnow()
                }
            
            logger.info(f"Camera {camera_id} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding camera {camera_id}: {e}")
            return False
    
    def start_camera_thread(self, camera_id: int) -> bool:
        """Start processing thread for camera"""
        try:
            if camera_id not in self.cameras:
                logger.error(f"Camera {camera_id} not found")
                return False
            
            with self.lock:
                if camera_id in self.active_cameras:
                    logger.warning(f"Camera {camera_id} already active")
                    return False
                
                self.active_cameras.add(camera_id)
                self.frame_buffers[camera_id] = []
                self.detection_results[camera_id] = {}
            
            # Start thread
            thread = threading.Thread(
                target=self._camera_capture_loop,
                args=(camera_id,),
                daemon=True
            )
            thread.start()
            
            logger.info(f"Camera {camera_id} thread started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting camera thread: {e}")
            return False
    
    def stop_camera_thread(self, camera_id: int) -> bool:
        """Stop processing thread for camera"""
        try:
            with self.lock:
                if camera_id in self.active_cameras:
                    self.active_cameras.remove(camera_id)
            
            logger.info(f"Camera {camera_id} thread stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping camera thread: {e}")
            return False
    
    def _camera_capture_loop(self, camera_id: int):
        """Main camera capture and detection loop"""
        try:
            camera = self.cameras[camera_id]
            cap = camera['capture']
            
            frame_count = 0
            while camera_id in self.active_cameras:
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning(f"Camera {camera_id}: Cannot read frame")
                    continue
                
                frame_count += 1
                
                # Perform detection
                if self.detector:
                    results = self.detector.detect(frame, camera_id)
                    
                    with self.lock:
                        self.detection_results[camera_id] = results
                        
                        # Keep buffer of last 5 frames
                        if len(self.frame_buffers[camera_id]) >= 5:
                            self.frame_buffers[camera_id].pop(0)
                        
                        self.frame_buffers[camera_id].append({
                            'frame': frame,
                            'results': results,
                            'timestamp': datetime.utcnow()
                        })
                
                # Throttle if needed
                if frame_count % 3 == 0:
                    cv2.waitKey(1)
        
        except Exception as e:
            logger.error(f"Camera {camera_id} capture loop error: {e}")
        
        finally:
            cap.release()
            logger.info(f"Camera {camera_id} released")
    
    def get_camera_frame(self, camera_id: int) -> Optional[np.ndarray]:
        """Get latest frame from camera"""
        with self.lock:
            if camera_id in self.frame_buffers and self.frame_buffers[camera_id]:
                return self.frame_buffers[camera_id][-1]['frame']
        return None
    
    def get_detection_result(self, camera_id: int) -> Dict:
        """Get latest detection result for camera"""
        with self.lock:
            return self.detection_results.get(camera_id, {})
    
    def get_all_results(self) -> Dict:
        """Get all cameras detection results"""
        with self.lock:
            return dict(self.detection_results)
    
    def remove_camera(self, camera_id: int) -> bool:
        """Remove camera from system"""
        try:
            self.stop_camera_thread(camera_id)
            
            with self.lock:
                if camera_id in self.cameras:
                    self.cameras[camera_id]['capture'].release()
                    del self.cameras[camera_id]
                    
                    if camera_id in self.frame_buffers:
                        del self.frame_buffers[camera_id]
                    
                    if camera_id in self.detection_results:
                        del self.detection_results[camera_id]
            
            logger.info(f"Camera {camera_id} removed")
            return True
            
        except Exception as e:
            logger.error(f"Error removing camera: {e}")
            return False

    def stop_all(self):
        """Stop all active camera threads and release resources."""
        try:
            with self.lock:
                camera_ids = list(self.active_cameras)
            for camera_id in camera_ids:
                self.stop_camera_thread(camera_id)

            with self.lock:
                for camera_id, camera in list(self.cameras.items()):
                    try:
                        camera['capture'].release()
                    except Exception:
                        pass
                self.cameras.clear()
                self.frame_buffers.clear()
                self.detection_results.clear()
                self.active_cameras.clear()

            try:
                self.executor.shutdown(wait=False)
            except Exception:
                pass

            logger.info("All camera streams and resources have been stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping all cameras: {e}")
            return False

    def get_camera_status(self) -> Dict:
        """Get status of all cameras"""
        with self.lock:
            return {
                camera_id: {
                    'active': camera_id in self.active_cameras,
                    'location': self.cameras[camera_id].get('location'),
                    'added_at': self.cameras[camera_id].get('added_at'),
                    'latest_result': self.detection_results.get(camera_id)
                }
                for camera_id in self.cameras
            }
