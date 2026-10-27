"""
Incident Management Routes
Endpoints for managing incidents and incidents
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from backend.services import IncidentManagementService, AuthenticationService
import logging

logger = logging.getLogger(__name__)

incidents_bp = Blueprint('incidents', __name__, url_prefix='/api/incidents')

# Placeholder for initialized services - will be injected
incident_service = None
auth_service = None

def init_incident_routes(app, incident_svc, auth_svc):
    """Initialize incident routes with service instances"""
    global incident_service, auth_service
    incident_service = incident_svc
    auth_service = auth_svc
    app.register_blueprint(incidents_bp)

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        payload = auth_service.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function

@incidents_bp.route('', methods=['GET'])
@require_auth
def get_incidents():
    """Get all open incidents"""
    try:
        camera_id = request.args.get('camera_id', type=int)
        limit = request.args.get('limit', 100, type=int)
        
        incidents = incident_service.get_open_incidents(camera_id=camera_id, limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(incidents),
            'incidents': incidents
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving incidents: {e}")
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/<incident_id>', methods=['GET'])
@require_auth
def get_incident(incident_id: str):
    """Get specific incident details"""
    try:
        incident = incident_service.get_incident(incident_id)
        
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        return jsonify({
            'success': True,
            'incident': incident
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving incident: {e}")
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('', methods=['POST'])
@require_auth
def create_incident():
    """Create new incident"""
    try:
        data = request.get_json()
        
        incident_id = incident_service.create_incident(
            incident_type=data.get('type'),
            severity=data.get('severity'),
            camera_id=data.get('camera_id'),
            location=data.get('location'),
            worker_id=data.get('worker_id'),
            message=data.get('message'),
            image_url=data.get('image_url')
        )
        
        if not incident_id:
            return jsonify({'error': 'Failed to create incident'}), 500
        
        return jsonify({
            'success': True,
            'incident_id': incident_id,
            'message': 'Incident created successfully'
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating incident: {e}")
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/<incident_id>/acknowledge', methods=['PUT'])
@require_auth
def acknowledge_incident(incident_id: str):
    """Acknowledge an incident"""
    try:
        data = request.get_json() or {}
        user_id = request.user['user_id']
        notes = data.get('notes')
        
        success = incident_service.acknowledge_incident(incident_id, user_id, notes)
        
        if not success:
            return jsonify({'error': 'Failed to acknowledge incident'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Incident acknowledged'
        }), 200
    
    except Exception as e:
        logger.error(f"Error acknowledging incident: {e}")
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/<incident_id>/resolve', methods=['PUT'])
@require_auth
def resolve_incident(incident_id: str):
    """Resolve an incident"""
    try:
        data = request.get_json()
        user_id = request.user['user_id']
        
        success = incident_service.resolve_incident(
            incident_id,
            user_id,
            resolution_type=data.get('resolution_type', 'corrected'),
            notes=data.get('notes')
        )
        
        if not success:
            return jsonify({'error': 'Failed to resolve incident'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Incident resolved'
        }), 200
    
    except Exception as e:
        logger.error(f"Error resolving incident: {e}")
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/<incident_id>/escalate', methods=['PUT'])
@require_auth
def escalate_incident(incident_id: str):
    """Escalate incident severity"""
    try:
        data = request.get_json()
        
        success = incident_service.escalate_incident(
            incident_id,
            new_severity=data.get('new_severity'),
            reason=data.get('reason')
        )
        
        if not success:
            return jsonify({'error': 'Failed to escalate incident'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Incident escalated'
        }), 200
    
    except Exception as e:
        logger.error(f"Error escalating incident: {e}")
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/camera/<int:camera_id>', methods=['GET'])
@require_auth
def get_camera_incidents(camera_id: int):
    """Get incidents for specific camera"""
    try:
        hours = request.args.get('hours', 24, type=int)
        status = request.args.get('status')
        
        incidents = incident_service.get_incidents_by_camera(
            camera_id=camera_id,
            status=status,
            hours=hours
        )
        
        return jsonify({
            'success': True,
            'count': len(incidents),
            'incidents': incidents
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving camera incidents: {e}")
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/worker/<int:worker_id>', methods=['GET'])
@require_auth
def get_worker_incidents(worker_id: int):
    """Get incidents for specific worker"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        incidents = incident_service.get_incidents_by_worker(
            worker_id=worker_id,
            hours=hours
        )
        
        return jsonify({
            'success': True,
            'count': len(incidents),
            'incidents': incidents
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving worker incidents: {e}")
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/statistics', methods=['GET'])
@require_auth
def get_statistics():
    """Get incident statistics"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        stats = incident_service.get_incident_statistics(hours=hours)
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/bulk-update', methods=['PUT'])
@require_auth
def bulk_update_incidents():
    """Bulk update multiple incidents"""
    try:
        data = request.get_json()
        incident_ids = data.get('incident_ids', [])
        status = data.get('status')
        notes = data.get('notes')
        
        updated_count = incident_service.bulk_update_incidents(
            incident_ids=incident_ids,
            status=status,
            notes=notes
        )
        
        return jsonify({
            'success': True,
            'updated_count': updated_count,
            'message': f'{updated_count} incidents updated'
        }), 200
    
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        return jsonify({'error': str(e)}), 500
