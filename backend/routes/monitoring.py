"""
Monitoring Routes
Real-time camera monitoring, MJPEG streaming, and live updates
"""

from flask import Blueprint, Response, request, jsonify, stream_with_context, current_app
from functools import wraps
import logging
import time
import json
from datetime import datetime
from backend.services import AuthenticationService

logger = logging.getLogger(__name__)

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')

# Placeholder for initialized services
monitoring_service = None
auth_service = None

def init_monitoring_routes(app, monitoring_svc, auth_svc):
    """Initialize monitoring routes with service instances"""
    global monitoring_service, auth_service
    monitoring_service = monitoring_svc
    auth_service = auth_svc
    app.register_blueprint(monitoring_bp)

def require_auth(f):
    """Authentication decorator (optional in development)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip auth in development mode
        if not current_app.config.get('REQUIRE_AUTH', True):
            request.user = {'username': 'development'}
            return f(*args, **kwargs)
        
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        token = token or request.args.get('token', '')
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        payload = auth_service.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function

def generate_mjpeg(camera_id: int):
    """Generate MJPEG stream for camera"""
    try:
        while True:
            # Get frame from camera
            frame_jpeg = monitoring_service.get_camera_frame_jpeg(camera_id)
            
            if frame_jpeg is None:
                # Send placeholder if no frame available
                yield b'--frame\r\n'
                yield b'Content-Type: image/jpeg\r\n'
                yield b'Content-Length: 0\r\n\r\n'
            else:
                # Send frame
                yield b'--frame\r\n'
                yield b'Content-Type: image/jpeg\r\n'
                yield b'Content-Length: ' + str(len(frame_jpeg)).encode() + b'\r\n\r\n'
                yield frame_jpeg
                yield b'\r\n'
            
            # Wait 1 second before next frame (as user requested)
            time.sleep(1)
    
    except GeneratorExit:
        logger.debug(f"Stream ended for camera {camera_id}")

@monitoring_bp.route('/status', methods=['GET'])
@require_auth
def get_monitoring_status():
    """Get overall monitoring status"""
    try:
        status = monitoring_service.get_monitoring_status()
        
        return jsonify({
            'success': True,
            'monitoring_status': status
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/cameras', methods=['GET'])
@require_auth
def get_all_cameras_status():
    """Get status of all cameras"""
    try:
        cameras = monitoring_service.get_all_cameras_status()
        
        return jsonify({
            'success': True,
            'count': len(cameras),
            'cameras': cameras
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting cameras status: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/cameras/<int:camera_id>', methods=['GET'])
@require_auth
def get_camera_status(camera_id: int):
    """Get status of specific camera"""
    try:
        status = monitoring_service.get_camera_status(camera_id)
        
        if status is None:
            return jsonify({'error': 'Camera not found'}), 404
        
        return jsonify({
            'success': True,
            'camera': status
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting camera status: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/cameras/<int:camera_id>/add', methods=['POST'])
@require_auth
def add_camera(camera_id: int):
    """Add camera for monitoring"""
    try:
        data = request.get_json()
        source = data.get('source')
        location = data.get('location', f'Camera {camera_id}')
        auto_start = data.get('auto_start', True)
        
        if not source:
            return jsonify({'error': 'Source URL required'}), 400
        
        success = monitoring_service.add_camera(
            camera_id=camera_id,
            source=source,
            location=location,
            auto_start=auto_start
        )
        
        if not success:
            return jsonify({'error': 'Failed to add camera'}), 500
        
        return jsonify({
            'success': True,
            'message': f'Camera {camera_id} added successfully',
            'camera_id': camera_id
        }), 201
    
    except Exception as e:
        logger.error(f"Error adding camera: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/cameras/<int:camera_id>/remove', methods=['POST'])
@require_auth
def remove_camera(camera_id: int):
    """Remove camera from monitoring"""
    try:
        success = monitoring_service.remove_camera(camera_id)
        
        if not success:
            return jsonify({'error': 'Camera not found'}), 404
        
        return jsonify({
            'success': True,
            'message': f'Camera {camera_id} removed successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Error removing camera: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/start', methods=['POST'])
@require_auth
def start_monitoring():
    """Start all cameras monitoring"""
    try:
        monitoring_service.start_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Monitoring started for all cameras'
        }), 200
    
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/stop', methods=['POST'])
@require_auth
def stop_monitoring():
    """Stop all cameras monitoring"""
    try:
        monitoring_service.stop_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Monitoring stopped for all cameras'
        }), 200
    
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/stream/<int:camera_id>', methods=['GET'])
@require_auth
def stream_camera(camera_id: int):
    """
    Stream camera as MJPEG
    Access at: /api/monitoring/stream/<camera_id>
    interval: 1 second (as requested)
    """
    try:
        status = monitoring_service.get_camera_status(camera_id)
        
        if status is None:
            return jsonify({'error': 'Camera not found'}), 404
        
        if not status['is_connected']:
            return jsonify({'error': 'Camera not connected'}), 503
        
        # Stream MJPEG with 1-second interval
        return Response(
            generate_mjpeg(camera_id),
            mimetype='multipart/x-mixed-replace; boundary=frame',
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
    
    except Exception as e:
        logger.error(f"Error streaming camera: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/events', methods=['GET'])
@require_auth
def monitoring_events():
    """Server-sent events endpoint for real-time monitoring updates"""
    def event_stream():
        while True:
            try:
                status = monitoring_service.get_monitoring_status()
                cameras = monitoring_service.get_all_cameras_status()
                detections = monitoring_service.get_all_detection_results()

                alerts = []
                for result in detections:
                    for violation in result.get('violations', []):
                        alerts.append({
                            'camera_id': result.get('camera_id'),
                            'violation': violation,
                            'severity': 'critical' if 'MISSING' in violation or 'NO_PPE' in violation else 'warning',
                            'timestamp': result.get('timestamp') or datetime.utcnow().isoformat()
                        })

                payload = {
                    'monitoring': status,
                    'cameras': cameras,
                    'active_alerts': len(alerts),
                    'alerts': alerts[:5],
                    'timestamp': datetime.utcnow().isoformat()
                }

                yield f"data: {json.dumps(payload)}\n\n"
                time.sleep(1)
            except GeneratorExit:
                logger.debug("Monitoring event stream closed")
                break
            except Exception as e:
                logger.error(f"Monitoring event stream error: {e}")
                time.sleep(1)

    return Response(
        stream_with_context(event_stream()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
    )

@monitoring_bp.route('/frame/<int:camera_id>', methods=['GET'])
@require_auth
def get_camera_frame(camera_id: int):
    """Get current frame from camera"""
    try:
        frame_jpeg = monitoring_service.get_camera_frame_jpeg(camera_id)
        
        if frame_jpeg is None:
            return jsonify({'error': 'No frame available'}), 503
        
        return Response(
            frame_jpeg,
            mimetype='image/jpeg',
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate'
            }
        )
    
    except Exception as e:
        logger.error(f"Error getting frame: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/detections', methods=['GET'])
@require_auth
def get_all_detections():
    """Get latest detections from all cameras"""
    try:
        detections = monitoring_service.get_all_detection_results()
        
        return jsonify({
            'success': True,
            'count': len(detections),
            'detections': detections
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting detections: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/detections/<int:camera_id>', methods=['GET'])
@require_auth
def get_camera_detections(camera_id: int):
    """Get latest detection from specific camera"""
    try:
        status = monitoring_service.get_camera_status(camera_id)
        
        if status is None:
            return jsonify({'error': 'Camera not found'}), 404
        
        # Get detection results from camera
        # Note: actual detection integration would happen here
        
        return jsonify({
            'success': True,
            'camera_id': camera_id,
            'detection_timestamp': status['last_detection_time'],
            'total_detections': status['total_detections']
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting detections: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/live-feed', methods=['GET'])
def live_feed_page():
    """Serve live monitoring dashboard"""
    try:
        from flask import render_template
        return render_template('live_monitoring.html')
    except Exception as e:
        logger.error(f"Error serving live feed page: {e}")
        return jsonify({'error': 'Page not found'}), 404
