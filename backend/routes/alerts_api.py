"""
Emergency Alert API Endpoints
Trigger and manage emergency alerts
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

alert_api_bp = Blueprint('alerts_api', __name__, url_prefix='/api/alerts')


def require_auth(f):
    """Authentication decorator"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        from backend.services import AuthenticationService
        auth_service = AuthenticationService()
        
        payload = auth_service.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function


def init_alert_api_routes(app, db=None):
    """Initialize alert API routes"""
    app.register_blueprint(alert_api_bp)


@alert_api_bp.route('/trigger', methods=['POST'])
@require_auth
def trigger_emergency_alert():
    """
    Trigger emergency alert to all emergency contacts
    
    Request body:
    {
        "camera_id": 1,
        "risk_type": "not_wearing_helmet",
        "risk_category": "PPE",
        "severity": "CRITICAL",
        "confidence_score": 0.95,
        "risk_score": 85,
        "location": "Factory Floor - Section A",
        "worker_id": "W001",
        "image_url": "https://...",
        "dashboard_link": "https://dashboard.com/alerts/123"
    }
    """
    try:
        from backend.services.alert_dispatcher import get_alert_dispatcher, AlertTrigger
        
        dispatcher = get_alert_dispatcher()
        if not dispatcher:
            return jsonify({
                'success': False,
                'error': 'Alert service not available'
            }), 503
        
        user_id = request.user.get('user_id')
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['camera_id', 'risk_type', 'risk_category', 'severity', 'location']
        missing = [f for f in required_fields if f not in data]
        
        if missing:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        # Validate severity
        valid_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        if data['severity'] not in valid_severities:
            return jsonify({
                'success': False,
                'error': f'Invalid severity. Must be one of: {", ".join(valid_severities)}'
            }), 400
        
        # Create alert trigger
        alert = AlertTrigger(
            camera_id=int(data['camera_id']),
            risk_type=data['risk_type'],
            risk_category=data['risk_category'],
            severity=data['severity'],
            confidence_score=float(data.get('confidence_score', 0.9)),
            risk_score=int(data.get('risk_score', 75)),
            location=data['location'],
            worker_id=data.get('worker_id'),
            image_url=data.get('image_url'),
            dashboard_link=data.get('dashboard_link'),
            timestamp=datetime.utcnow()
        )
        
        # Dispatch alert
        result = dispatcher.trigger_emergency_alert(alert, user_id, async_mode=True)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Emergency alert triggered successfully',
                'recipients_contacted': result.get('recipients_contacted', 0),
                'timestamp': result.get('timestamp')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to trigger alert')
            }), 500
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'error': f'Invalid request data: {str(e)}'
        }), 400
    
    except Exception as e:
        logger.error(f"Error triggering alert: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to trigger emergency alert'
        }), 500


@alert_api_bp.route('/test', methods=['POST'])
@require_auth
def test_alert():
    """
    Send test alert to verify emergency contact configuration
    
    Request body:
    {
        "contact_id": 1  // Optional: specific contact, or sends to admin
    }
    """
    try:
        from backend.services.alert_dispatcher import get_alert_dispatcher, AlertTrigger
        
        dispatcher = get_alert_dispatcher()
        if not dispatcher:
            return jsonify({
                'success': False,
                'error': 'Alert service not available'
            }), 503
        
        user_id = request.user.get('user_id')
        
        # Create test alert
        alert = AlertTrigger(
            camera_id=999,
            risk_type='TEST_ALERT',
            risk_category='TEST',
            severity='HIGH',
            confidence_score=1.0,
            risk_score=100,
            location='TEST - System Configuration Verification',
            dashboard_link='https://dashboard.example.com/test',
            timestamp=datetime.utcnow()
        )
        
        # Dispatch test alert
        result = dispatcher.trigger_emergency_alert(alert, user_id, async_mode=False)
        
        return jsonify({
            'success': result['success'],
            'message': 'Test alert sent to configured emergency contacts',
            'delivery_status': result.get('delivery_status', {}),
            'details': result
        }), 200 if result['success'] else 500
    
    except Exception as e:
        logger.error(f"Error sending test alert: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@alert_api_bp.route('/history', methods=['GET'])
@require_auth
def get_alert_history():
    """Get alert history for authenticated user"""
    try:
        from backend.database.models import RiskAlert
        
        user_id = request.user.get('user_id')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        severity = request.args.get('severity')
        
        query = RiskAlert.query
        
        if severity:
            query = query.filter_by(severity=severity)
        
        alerts = query.order_by(RiskAlert.created_at.desc()).limit(limit).offset(offset).all()
        
        alerts_data = [{
            'id': a.id,
            'alert_id': a.alert_id,
            'camera_id': a.camera_id,
            'risk_type': a.risk_type,
            'risk_category': a.risk_category,
            'severity': a.severity,
            'confidence_score': a.confidence_score,
            'risk_score': a.risk_score,
            'location': a.location,
            'worker_id': a.worker_id,
            'status': a.status,
            'image_url': a.image_url,
            'created_at': a.created_at.isoformat() if a.created_at else None,
            'notified': a.notified,
            'notified_at': a.notified_at.isoformat() if a.notified_at else None
        } for a in alerts]
        
        return jsonify({
            'success': True,
            'alerts': alerts_data,
            'total': len(alerts_data)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching alert history: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch alert history'
        }), 500


@alert_api_bp.route('/<alert_id>/status', methods=['PUT'])
@require_auth
def update_alert_status(alert_id):
    """Update alert status"""
    try:
        from backend.database.models import RiskAlert
        
        data = request.get_json()
        status = data.get('status')
        
        valid_statuses = ['pending', 'notified', 'acknowledged', 'resolved', 'dismissed']
        if status not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        alert = RiskAlert.query.filter_by(alert_id=alert_id).first()
        
        if not alert:
            return jsonify({
                'success': False,
                'error': 'Alert not found'
            }), 404
        
        alert.status = status
        
        if status == 'acknowledged':
            alert.acknowledged_at = datetime.utcnow()
        elif status == 'resolved':
            alert.resolved_at = datetime.utcnow()
        
        from backend.database.models import db
        db.session.commit()
        
        logger.info(f"Alert {alert_id} status updated to {status}")
        
        return jsonify({
            'success': True,
            'message': f'Alert status updated to {status}'
        }), 200
    
    except Exception as e:
        logger.error(f"Error updating alert status: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update alert status'
        }), 500
