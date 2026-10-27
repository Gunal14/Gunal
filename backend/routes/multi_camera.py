"""
Multi-Camera Monitoring Routes
REST API endpoints for managing and monitoring multiple simultaneous camera feeds
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

multi_camera_bp = Blueprint('multi_camera', __name__, url_prefix='/api/v1')

# Global coordinator instance
multi_camera_coordinator = None


def initialize_coordinator(risk_engine, notification_service):
    """Initialize the global multi-camera coordinator"""
    global multi_camera_coordinator
    from backend.services.multi_camera_coordinator import MultiCameraCoordinator
    
    multi_camera_coordinator = MultiCameraCoordinator(
        max_cameras=40,
        risk_engine=risk_engine,
        notification_service=notification_service
    )
    logger.info("Multi-Camera Coordinator initialized for 40+ cameras")
    return multi_camera_coordinator


# ============================================================================
# CAMERA REGISTRATION & MANAGEMENT
# ============================================================================

@multi_camera_bp.route('/cameras', methods=['GET'])
@cross_origin()
def get_all_cameras():
    """
    Get all registered cameras with real-time status
    ---
    Query params:
        - status: connected|disconnected|all (default: all)
    """
    try:
        from backend.database.models import CameraConfiguration, CameraHealthStatus, db
        
        status_filter = request.args.get('status', 'all')
        
        # Get all cameras
        cameras = CameraConfiguration.query.filter_by(is_active=True).all()
        
        if not cameras:
            return jsonify({
                'success': True,
                'count': 0,
                'cameras': []
            })
        
        # Get health status for each camera
        camera_list = []
        for camera in cameras:
            health = CameraHealthStatus.query.filter_by(
                camera_id=camera.id
            ).order_by(CameraHealthStatus.last_update.desc()).first()
            
            is_connected = health.is_connected if health else False
            
            # Apply status filter
            if status_filter == 'connected' and not is_connected:
                continue
            if status_filter == 'disconnected' and is_connected:
                continue
            
            health_data = {
                'status': 'connected' if is_connected else 'disconnected',
                'fps': health.current_fps if health else 0,
                'cpu_usage': health.cpu_usage if health else 0,
                'memory_usage': health.memory_usage if health else 0,
                'uptime_percentage': health.uptime_percentage if health else 0,
            } if health else {
                'status': 'no_data',
                'fps': 0,
                'cpu_usage': 0,
                'memory_usage': 0,
                'uptime_percentage': 0,
            }
            
            camera_list.append({
                'camera_id': camera.id,
                'camera_name': camera.camera_name,
                'location': camera.location,
                'stream_url': camera.stream_url,
                'hazard_level': camera.hazard_level,
                'created_at': camera.created_at.isoformat(),
                'health': health_data,
            })
        
        return jsonify({
            'success': True,
            'count': len(camera_list),
            'cameras': camera_list
        })
    
    except Exception as e:
        logger.error(f"Error fetching cameras: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_camera_bp.route('/cameras', methods=['POST'])
@cross_origin()
def register_camera():
    """
    Register a new camera for monitoring (Max 40 active)
    ---
    Request body:
        {
            "camera_name": "Camera 1 - Assembly Floor",
            "location": "Assembly Line A",
            "stream_url": "rtsp://...",
            "hazard_level": "HIGH",
            "detection_enabled": true
        }
    """
    try:
        from backend.database.models import CameraConfiguration, db
        
        data = request.get_json()
        
        if not data.get('camera_name') or not data.get('stream_url'):
            return jsonify({
                'success': False,
                'error': 'camera_name and stream_url are required'
            }), 400
        
        # Check limit (max 40 active cameras)
        active_count = CameraConfiguration.query.filter_by(is_active=True).count()
        
        if active_count >= 40:
            return jsonify({
                'success': False,
                'error': 'Maximum 40 active cameras reached',
                'current_count': active_count
            }), 400
        
        # Create camera
        camera = CameraConfiguration(
            camera_name=data.get('camera_name'),
            location=data.get('location', ''),
            stream_url=data.get('stream_url'),
            hazard_level=data.get('hazard_level', 'MEDIUM'),
            detection_enabled=data.get('detection_enabled', True),
            is_active=True,
        )
        
        db.session.add(camera)
        db.session.commit()
        
        # Register with coordinator if available
        if multi_camera_coordinator:
            multi_camera_coordinator.add_camera(
                camera_id=camera.id,
                config={
                    'camera_name': camera.camera_name,
                    'stream_url': camera.stream_url,
                    'hazard_level': camera.hazard_level,
                }
            )
        
        logger.info(f"Camera registered: {camera.camera_name} (ID: {camera.id})")
        
        return jsonify({
            'success': True,
            'message': 'Camera registered successfully',
            'camera_id': camera.id,
            'camera_name': camera.camera_name,
        }), 201
    
    except Exception as e:
        logger.error(f"Error registering camera: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_camera_bp.route('/cameras/<int:camera_id>', methods=['GET'])
@cross_origin()
def get_camera_details(camera_id):
    """Get detailed information about a specific camera"""
    try:
        from backend.database.models import CameraConfiguration, CameraHealthStatus
        
        camera = CameraConfiguration.query.filter_by(id=camera_id).first()
        
        if not camera:
            return jsonify({'success': False, 'error': 'Camera not found'}), 404
        
        # Get latest health status
        health = CameraHealthStatus.query.filter_by(
            camera_id=camera_id
        ).order_by(CameraHealthStatus.last_update.desc()).first()
        
        health_data = {
            'is_connected': health.is_connected,
            'current_fps': health.current_fps,
            'frame_loss_rate': health.frame_loss_rate,
            'cpu_usage': health.cpu_usage,
            'memory_usage': health.memory_usage,
            'bandwidth_usage': health.bandwidth_usage,
            'latency_ms': health.latency_ms,
            'packet_loss': health.packet_loss,
            'uptime_percentage': health.uptime_percentage,
            'uptime_seconds': health.uptime_seconds,
            'last_update': health.last_update.isoformat(),
            'last_error': health.last_error,
        } if health else {}
        
        return jsonify({
            'success': True,
            'camera': {
                'camera_id': camera.id,
                'camera_name': camera.camera_name,
                'location': camera.location,
                'stream_url': camera.stream_url,
                'hazard_level': camera.hazard_level,
                'detection_enabled': camera.detection_enabled,
                'is_active': camera.is_active,
                'created_at': camera.created_at.isoformat(),
                'health': health_data,
            }
        })
    
    except Exception as e:
        logger.error(f"Error fetching camera details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_camera_bp.route('/cameras/<int:camera_id>', methods=['PUT'])
@cross_origin()
def update_camera(camera_id):
    """Update camera configuration"""
    try:
        from backend.database.models import CameraConfiguration, db
        
        data = request.get_json()
        camera = CameraConfiguration.query.filter_by(id=camera_id).first()
        
        if not camera:
            return jsonify({'success': False, 'error': 'Camera not found'}), 404
        
        # Update fields
        camera.camera_name = data.get('camera_name', camera.camera_name)
        camera.location = data.get('location', camera.location)
        camera.stream_url = data.get('stream_url', camera.stream_url)
        camera.hazard_level = data.get('hazard_level', camera.hazard_level)
        camera.detection_enabled = data.get('detection_enabled', camera.detection_enabled)
        
        db.session.commit()
        
        logger.info(f"Camera updated: {camera.camera_name}")
        
        return jsonify({'success': True, 'message': 'Camera updated successfully'})
    
    except Exception as e:
        logger.error(f"Error updating camera: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_camera_bp.route('/cameras/<int:camera_id>/deactivate', methods=['POST'])
@cross_origin()
def deactivate_camera(camera_id):
    """Stop monitoring a camera"""
    try:
        from backend.database.models import CameraConfiguration, db
        
        camera = CameraConfiguration.query.filter_by(id=camera_id).first()
        
        if not camera:
            return jsonify({'success': False, 'error': 'Camera not found'}), 404
        
        camera.is_active = False
        db.session.commit()
        
        # Remove from coordinator
        if multi_camera_coordinator:
            multi_camera_coordinator.remove_camera(camera_id)
        
        logger.info(f"Camera deactivated: {camera.camera_name}")
        
        return jsonify({'success': True, 'message': 'Camera deactivated'})
    
    except Exception as e:
        logger.error(f"Error deactivating camera: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# MULTI-CAMERA COORDINATOR STATUS
# ============================================================================

@multi_camera_bp.route('/coordinator/status', methods=['GET'])
@cross_origin()
def get_coordinator_status():
    """
    Get overall multi-camera coordinator status and system health
    Shows resource utilization across all 40 cameras
    """
    try:
        if not multi_camera_coordinator:
            return jsonify({
                'success': False,
                'error': 'Multi-camera coordinator not initialized'
            }), 503
        
        status = multi_camera_coordinator.get_coordinator_status()
        
        return jsonify({
            'success': True,
            'coordinator_status': status
        })
    
    except Exception as e:
        logger.error(f"Error getting coordinator status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_camera_bp.route('/coordinator/statistics', methods=['GET'])
@cross_origin()
def get_coordinator_statistics():
    """Get aggregated statistics across all monitored cameras"""
    try:
        from backend.database.models import RiskAlert, db
        
        hours = request.args.get('hours', 24, type=int)
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get coordinator stats
        if not multi_camera_coordinator:
            return jsonify({
                'success': False,
                'error': 'Multi-camera coordinator not initialized'
            }), 503
        
        coordinator_stats = multi_camera_coordinator.stats
        
        # Get recent alerts
        alerts = RiskAlert.query.filter(
            RiskAlert.created_at >= cutoff_time
        ).all()
        
        alert_summary = {
            'total': len(alerts),
            'by_severity': {
                'LOW': len([a for a in alerts if a.severity == 'LOW']),
                'MEDIUM': len([a for a in alerts if a.severity == 'MEDIUM']),
                'HIGH': len([a for a in alerts if a.severity == 'HIGH']),
                'CRITICAL': len([a for a in alerts if a.severity == 'CRITICAL']),
            }
        }
        
        return jsonify({
            'success': True,
            'time_window_hours': hours,
            'coordinator_statistics': {
                'total_cameras': coordinator_stats.get('total_cameras', 0),
                'active_cameras': len(multi_camera_coordinator.cameras),
                'total_frames': coordinator_stats.get('total_frames', 0),
                'total_detections': coordinator_stats.get('total_detections', 0),
                'total_alerts': coordinator_stats.get('total_alerts', 0),
                'alerts_by_severity': coordinator_stats.get('total_alerts_by_severity', {}),
                'camera_stats': coordinator_stats.get('camera_stats', {}),
            },
            'recent_alerts': alert_summary,
        })
    
    except Exception as e:
        logger.error(f"Error getting coordinator statistics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# INDIVIDUAL CAMERA STATUS
# ============================================================================

@multi_camera_bp.route('/cameras/<int:camera_id>/health', methods=['GET'])
@cross_origin()
def get_camera_health(camera_id):
    """Get detailed health metrics for a specific camera"""
    try:
        from backend.database.models import CameraConfiguration, CameraHealthStatus
        
        camera = CameraConfiguration.query.filter_by(id=camera_id).first()
        
        if not camera:
            return jsonify({'success': False, 'error': 'Camera not found'}), 404
        
        # Get last 10 health records for trend analysis
        health_records = CameraHealthStatus.query.filter_by(
            camera_id=camera_id
        ).order_by(CameraHealthStatus.last_update.desc()).limit(10).all()
        
        if not health_records:
            return jsonify({
                'success': True,
                'camera_id': camera_id,
                'health_history': []
            })
        
        latest = health_records[0]
        
        return jsonify({
            'success': True,
            'camera_id': camera_id,
            'camera_name': camera.camera_name,
            'latest_health': {
                'timestamp': latest.last_update.isoformat(),
                'is_connected': latest.is_connected,
                'current_fps': latest.current_fps,
                'frame_loss_rate': latest.frame_loss_rate,
                'cpu_usage': latest.cpu_usage,
                'memory_usage': latest.memory_usage,
                'bandwidth_usage': latest.bandwidth_usage,
                'latency_ms': latest.latency_ms,
                'packet_loss': latest.packet_loss,
                'signal_strength': latest.signal_strength,
                'uptime_percentage': latest.uptime_percentage,
                'last_error': latest.last_error,
            },
            'health_history': [
                {
                    'timestamp': h.last_update.isoformat(),
                    'fps': h.current_fps,
                    'cpu_usage': h.cpu_usage,
                    'memory_usage': h.memory_usage,
                }
                for h in health_records
            ]
        })
    
    except Exception as e:
        logger.error(f"Error getting camera health: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# MULTI-CAMERA MONITORING CONTROL
# ============================================================================

@multi_camera_bp.route('/monitoring/start', methods=['POST'])
@cross_origin()
def start_monitoring_session():
    """Start monitoring all active cameras"""
    try:
        from backend.database.models import MultiCameraSession, CameraConfiguration, db
        from flask_jwt_extended import get_jwt_identity
        
        user_id = get_jwt_identity()
        
        # Get all active cameras
        active_cameras = CameraConfiguration.query.filter_by(is_active=True).all()
        
        if not active_cameras:
            return jsonify({
                'success': False,
                'error': 'No active cameras to monitor'
            }), 400
        
        # Create monitoring session
        session = MultiCameraSession(
            started_by_id=user_id,
            total_cameras=len(active_cameras),
            is_active=True,
        )
        
        session.camera_ids = [c.id for c in active_cameras]
        
        db.session.add(session)
        db.session.commit()
        
        # Start coordinator
        if multi_camera_coordinator:
            multi_camera_coordinator.start_monitoring()
        
        logger.info(f"Monitoring session started: {session.session_id}")
        
        return jsonify({
            'success': True,
            'message': 'Monitoring started',
            'session_id': session.session_id,
            'cameras_monitoring': len(active_cameras),
        }), 201
    
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_camera_bp.route('/monitoring/stop', methods=['POST'])
@cross_origin()
def stop_monitoring_session():
    """Stop monitoring all cameras"""
    try:
        from backend.database.models import MultiCameraSession, db
        
        # Get active session
        active_session = MultiCameraSession.query.filter_by(
            is_active=True
        ).order_by(MultiCameraSession.start_time.desc()).first()
        
        if not active_session:
            return jsonify({
                'success': False,
                'error': 'No active monitoring session'
            }), 404
        
        # Stop session
        active_session.is_active = False
        active_session.end_time = datetime.utcnow()
        db.session.commit()
        
        # Stop coordinator
        if multi_camera_coordinator:
            multi_camera_coordinator.stop_monitoring()
        
        logger.info(f"Monitoring session ended: {active_session.session_id}")
        
        return jsonify({
            'success': True,
            'message': 'Monitoring stopped',
            'session_id': active_session.session_id,
            'duration_seconds': (active_session.end_time - active_session.start_time).total_seconds(),
        })
    
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_camera_bp.route('/monitoring/session/<session_id>', methods=['GET'])
@cross_origin()
def get_monitoring_session(session_id):
    """Get details about a monitoring session"""
    try:
        from backend.database.models import MultiCameraSession
        
        session = MultiCameraSession.query.filter_by(session_id=session_id).first()
        
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        duration = None
        if session.end_time:
            duration = (session.end_time - session.start_time).total_seconds()
        
        return jsonify({
            'success': True,
            'session': {
                'session_id': session.session_id,
                'started_by_id': session.started_by_id,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'duration_seconds': duration,
                'is_active': session.is_active,
                'total_cameras': session.total_cameras,
                'active_alerts': session.active_alerts,
                'total_detections': session.total_detections,
                'high_risk_events': session.high_risk_events,
                'avg_response_time_ms': session.avg_response_time_ms,
                'system_health_score': session.system_health_score,
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# CAMERA FRAME PROCESSING (For real-time monitoring)
# ============================================================================

@multi_camera_bp.route('/cameras/<int:camera_id>/process-frame', methods=['POST'])
@cross_origin()
def process_camera_frame(camera_id):
    """
    Process a frame from a camera (used by edge devices or streaming servers)
    ---
    Request body:
        {
            "frame_data": "base64_encoded_image",
            "detections": [
                {
                    "class": "person",
                    "confidence": 0.95,
                    "bbox": [100, 200, 300, 400]
                }
            ]
        }
    """
    try:
        import base64
        import numpy as np
        import cv2
        
        data = request.get_json()
        frame_data = data.get('frame_data')
        detections = data.get('detections', [])
        
        if not frame_data:
            return jsonify({'success': False, 'error': 'frame_data is required'}), 400
        
        # Decode frame
        try:
            frame_bytes = base64.b64decode(frame_data)
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
        except Exception as e:
            logger.error(f"Error decoding frame: {e}")
            return jsonify({'success': False, 'error': 'Invalid frame data'}), 400
        
        # Process frame with coordinator
        if multi_camera_coordinator:
            result = multi_camera_coordinator.process_frame(
                camera_id=camera_id,
                frame=frame,
                detections=detections
            )
            
            return jsonify({
                'success': True,
                'message': 'Frame processed',
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Coordinator not initialized'
            }), 503
    
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
