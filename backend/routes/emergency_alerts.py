"""
Emergency Contact & Alert Management Routes
REST API endpoints for registering emergency contacts and managing alerts
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

emergency_alerts_bp = Blueprint('emergency_alerts', __name__, url_prefix='/api/v1')


# ============================================================================
# EMERGENCY CONTACT MANAGEMENT ENDPOINTS
# ============================================================================

@emergency_alerts_bp.route('/emergency-contacts', methods=['GET'])
@cross_origin()
def get_emergency_contacts():
    """
    Get all emergency contacts for authenticated admin
    ---
    Returns:
        List of emergency contacts with up to 10 per admin
    """
    try:
        from backend.database.models import EmergencyContact, db
        from flask_jwt_extended import get_jwt_identity
        
        user_id = get_jwt_identity()
        
        contacts = EmergencyContact.query.filter_by(
            admin_id=user_id,
            is_active=True
        ).all()
        
        return jsonify({
            'success': True,
            'count': len(contacts),
            'contacts': [
                {
                    'id': c.id,
                    'contact_name': c.contact_name,
                    'phone_number': c.phone_number,
                    'email': c.email,
                    'whatsapp_enabled': c.whatsapp_enabled,
                    'sms_enabled': c.sms_enabled,
                    'email_enabled': c.email_enabled,
                    'alert_levels': {
                        'low': c.alert_low,
                        'medium': c.alert_medium,
                        'high': c.alert_high,
                        'critical': c.alert_critical,
                    },
                    'verified': c.verified,
                    'created_at': c.created_at.isoformat(),
                }
                for c in contacts
            ]
        })
    
    except Exception as e:
        logger.error(f"Error fetching emergency contacts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@emergency_alerts_bp.route('/emergency-contacts', methods=['POST'])
@cross_origin()
def register_emergency_contact():
    """
    Register a new emergency contact (Max 10 per admin)
    ---
    Request body:
        {
            "contact_name": "John Manager",
            "phone_number": "+1234567890",
            "email": "john@example.com",
            "whatsapp_enabled": true,
            "sms_enabled": true,
            "email_enabled": true,
            "alert_low": false,
            "alert_medium": true,
            "alert_high": true,
            "alert_critical": true
        }
    """
    try:
        from backend.database.models import EmergencyContact, User, db
        from flask_jwt_extended import get_jwt_identity
        
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate data
        if not data.get('contact_name') or not data.get('phone_number'):
            return jsonify({
                'success': False,
                'error': 'contact_name and phone_number are required'
            }), 400
        
        # Check limit (max 10 contacts per admin)
        current_count = EmergencyContact.query.filter_by(
            admin_id=user_id,
            is_active=True
        ).count()
        
        if current_count >= 10:
            return jsonify({
                'success': False,
                'error': 'Maximum 10 emergency contacts allowed per admin',
                'current_count': current_count
            }), 400
        
        # Validate phone number format
        phone = data.get('phone_number').replace('+', '').replace('-', '').replace(' ', '')
        if len(phone) < 10 or not phone.isdigit():
            return jsonify({
                'success': False,
                'error': 'Invalid phone number format'
            }), 400
        
        # Create contact
        contact = EmergencyContact(
            admin_id=user_id,
            contact_name=data.get('contact_name'),
            phone_number=data.get('phone_number'),
            email=data.get('email'),
            whatsapp_enabled=data.get('whatsapp_enabled', True),
            sms_enabled=data.get('sms_enabled', True),
            email_enabled=data.get('email_enabled', True),
            alert_low=data.get('alert_low', False),
            alert_medium=data.get('alert_medium', True),
            alert_high=data.get('alert_high', True),
            alert_critical=data.get('alert_critical', True),
            is_active=True,
        )
        
        db.session.add(contact)
        db.session.commit()
        
        logger.info(f"Emergency contact registered: {contact.contact_name}")
        
        return jsonify({
            'success': True,
            'message': 'Emergency contact registered successfully',
            'contact_id': contact.id,
            'contact_name': contact.contact_name,
        }), 201
    
    except Exception as e:
        logger.error(f"Error registering emergency contact: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@emergency_alerts_bp.route('/emergency-contacts/<int:contact_id>', methods=['PUT'])
@cross_origin()
def update_emergency_contact(contact_id):
    """Update an emergency contact"""
    try:
        from backend.database.models import EmergencyContact, db
        from flask_jwt_extended import get_jwt_identity
        
        user_id = get_jwt_identity()
        data = request.get_json()
        
        contact = EmergencyContact.query.filter_by(
            id=contact_id,
            admin_id=user_id
        ).first()
        
        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        # Update fields
        contact.contact_name = data.get('contact_name', contact.contact_name)
        contact.phone_number = data.get('phone_number', contact.phone_number)
        contact.email = data.get('email', contact.email)
        contact.whatsapp_enabled = data.get('whatsapp_enabled', contact.whatsapp_enabled)
        contact.sms_enabled = data.get('sms_enabled', contact.sms_enabled)
        contact.email_enabled = data.get('email_enabled', contact.email_enabled)
        contact.alert_low = data.get('alert_low', contact.alert_low)
        contact.alert_medium = data.get('alert_medium', contact.alert_medium)
        contact.alert_high = data.get('alert_high', contact.alert_high)
        contact.alert_critical = data.get('alert_critical', contact.alert_critical)
        
        db.session.commit()
        
        logger.info(f"Emergency contact updated: {contact.contact_name}")
        
        return jsonify({'success': True, 'message': 'Contact updated successfully'})
    
    except Exception as e:
        logger.error(f"Error updating contact: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@emergency_alerts_bp.route('/emergency-contacts/<int:contact_id>', methods=['DELETE'])
@cross_origin()
def delete_emergency_contact(contact_id):
    """Delete (deactivate) an emergency contact"""
    try:
        from backend.database.models import EmergencyContact, db
        from flask_jwt_extended import get_jwt_identity
        
        user_id = get_jwt_identity()
        
        contact = EmergencyContact.query.filter_by(
            id=contact_id,
            admin_id=user_id
        ).first()
        
        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        # Soft delete
        contact.is_active = False
        db.session.commit()
        
        logger.info(f"Emergency contact deleted: {contact.contact_name}")
        
        return jsonify({'success': True, 'message': 'Contact deleted successfully'})
    
    except Exception as e:
        logger.error(f"Error deleting contact: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# RISK ALERT MANAGEMENT ENDPOINTS
# ============================================================================

@emergency_alerts_bp.route('/risk-alerts', methods=['GET'])
@cross_origin()
def get_risk_alerts():
    """
    Get recent risk alerts with filtering options
    ---
    Query params:
        - severity: LOW|MEDIUM|HIGH|CRITICAL
        - camera_id: Filter by camera
        - status: pending|notified|acknowledged|resolved
        - hours: Last N hours (default 24)
        - limit: Max results (default 100)
    """
    try:
        from backend.database.models import RiskAlert, db
        
        severity = request.args.get('severity')
        camera_id = request.args.get('camera_id', type=int)
        status = request.args.get('status')
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        # Build query
        query = RiskAlert.query
        
        # Time filter
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(RiskAlert.created_at >= cutoff_time)
        
        # Apply filters
        if severity:
            query = query.filter_by(severity=severity)
        if camera_id:
            query = query.filter_by(camera_id=camera_id)
        if status:
            query = query.filter_by(status=status)
        
        # Order by most recent
        alerts = query.order_by(RiskAlert.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(alerts),
            'alerts': [
                {
                    'alert_id': a.alert_id,
                    'camera_id': a.camera_id,
                    'risk_type': a.risk_type,
                    'risk_category': a.risk_category,
                    'severity': a.severity,
                    'confidence_score': a.confidence_score,
                    'risk_score': a.risk_score,
                    'status': a.status,
                    'worker_id': a.worker_id,
                    'image_url': a.image_url,
                    'timestamp': a.created_at.isoformat(),
                    'first_detection': a.first_detection_time.isoformat(),
                    'detection_count': a.detection_count,
                }
                for a in alerts
            ]
        })
    
    except Exception as e:
        logger.error(f"Error fetching risk alerts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@emergency_alerts_bp.route('/risk-alerts/<alert_id>', methods=['GET'])
@cross_origin()
def get_risk_alert_details(alert_id):
    """Get detailed information about a specific risk alert"""
    try:
        from backend.database.models import RiskAlert
        
        alert = RiskAlert.query.filter_by(alert_id=alert_id).first()
        
        if not alert:
            return jsonify({'success': False, 'error': 'Alert not found'}), 404
        
        return jsonify({
            'success': True,
            'alert': {
                'alert_id': alert.alert_id,
                'camera_id': alert.camera_id,
                'risk_type': alert.risk_type,
                'risk_category': alert.risk_category,
                'severity': alert.severity,
                'confidence_score': alert.confidence_score,
                'risk_score': alert.risk_score,
                'status': alert.status,
                'worker_id': alert.worker_id,
                'image_url': alert.image_url,
                'thumbnail_url': alert.thumbnail_url,
                'first_detection': alert.first_detection_time.isoformat(),
                'last_detection': alert.last_detection_time.isoformat(),
                'detection_count': alert.detection_count,
                'environmental_conditions': alert.environmental_conditions,
                'nearby_hazards': alert.nearby_hazards,
                'created_at': alert.created_at.isoformat(),
                'updated_at': alert.updated_at.isoformat(),
            }
        })
    
    except Exception as e:
        logger.error(f"Error fetching alert details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@emergency_alerts_bp.route('/risk-alerts/<alert_id>/acknowledge', methods=['POST'])
@cross_origin()
def acknowledge_risk_alert(alert_id):
    """Acknowledge a risk alert"""
    try:
        from backend.database.models import RiskAlert, db
        from flask_jwt_extended import get_jwt_identity
        
        user_id = get_jwt_identity()
        data = request.get_json()
        
        alert = RiskAlert.query.filter_by(alert_id=alert_id).first()
        
        if not alert:
            return jsonify({'success': False, 'error': 'Alert not found'}), 404
        
        alert.status = 'acknowledged'
        alert.acknowledged_by_id = user_id
        alert.acknowledged_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Alert {alert_id} acknowledged by user {user_id}")
        
        return jsonify({'success': True, 'message': 'Alert acknowledged'})
    
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@emergency_alerts_bp.route('/risk-alerts/<alert_id>/resolve', methods=['POST'])
@cross_origin()
def resolve_risk_alert(alert_id):
    """Resolve a risk alert"""
    try:
        from backend.database.models import RiskAlert, db
        from flask_jwt_extended import get_jwt_identity
        
        user_id = get_jwt_identity()
        data = request.get_json()
        
        alert = RiskAlert.query.filter_by(alert_id=alert_id).first()
        
        if not alert:
            return jsonify({'success': False, 'error': 'Alert not found'}), 404
        
        alert.status = 'resolved'
        alert.resolved_at = datetime.utcnow()
        alert.resolution_action = data.get('action', 'Manual resolution')
        
        db.session.commit()
        
        logger.info(f"Alert {alert_id} resolved")
        
        return jsonify({'success': True, 'message': 'Alert resolved'})
    
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ALERT STATISTICS ENDPOINTS
# ============================================================================

@emergency_alerts_bp.route('/alert-statistics', methods=['GET'])
@cross_origin()
def get_alert_statistics():
    """Get alert statistics and trends"""
    try:
        from backend.database.models import RiskAlert, db
        
        hours = request.args.get('hours', 24, type=int)
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get alerts
        alerts = RiskAlert.query.filter(
            RiskAlert.created_at >= cutoff_time
        ).all()
        
        # Calculate statistics
        stats = {
            'total_alerts': len(alerts),
            'by_severity': {
                'LOW': len([a for a in alerts if a.severity == 'LOW']),
                'MEDIUM': len([a for a in alerts if a.severity == 'MEDIUM']),
                'HIGH': len([a for a in alerts if a.severity == 'HIGH']),
                'CRITICAL': len([a for a in alerts if a.severity == 'CRITICAL']),
            },
            'by_status': {
                'pending': len([a for a in alerts if a.status == 'pending']),
                'acknowledged': len([a for a in alerts if a.status == 'acknowledged']),
                'resolved': len([a for a in alerts if a.status == 'resolved']),
            },
            'by_type': {},
            'by_camera': {},
        }
        
        # Count by type and camera
        for alert in alerts:
            stats['by_type'][alert.risk_type] = stats['by_type'].get(alert.risk_type, 0) + 1
            stats['by_camera'][alert.camera_id] = stats['by_camera'].get(alert.camera_id, 0) + 1
        
        # Calculate average response time
        acknowledged_alerts = [a for a in alerts if a.acknowledged_at]
        if acknowledged_alerts:
            response_times = [
                (a.acknowledged_at - a.created_at).total_seconds()
                for a in acknowledged_alerts
            ]
            stats['avg_response_time_seconds'] = sum(response_times) / len(response_times)
        
        return jsonify({
            'success': True,
            'hours_covered': hours,
            'statistics': stats
        })
    
    except Exception as e:
        logger.error(f"Error getting alert statistics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# EMERGENCY ALERT TESTING AND DEMO
# ============================================================================

@emergency_alerts_bp.route('/test-alert', methods=['POST'])
@cross_origin()
def test_emergency_alert():
    """
    Test emergency alert system by sending test notifications
    ---
    Request body:
        {
            "severity": "CRITICAL|HIGH|MEDIUM|LOW",
            "include_all_contacts": true
        }
    """
    try:
        from backend.database.models import EmergencyContact, db
        from backend.services.advanced_notification_service import advanced_notification_service
        from flask_jwt_extended import get_jwt_identity
        
        user_id = get_jwt_identity()
        data = request.get_json()
        severity = data.get('severity', 'HIGH')
        
        # Get emergency contacts
        contacts = EmergencyContact.query.filter_by(
            admin_id=user_id,
            is_active=True
        ).all()
        
        if not contacts:
            return jsonify({
                'success': False,
                'error': 'No emergency contacts registered'
            }), 400
        
        # Create test alert
        alert_data = {
            'severity': severity,
            'subject': '🚨 TEST ALERT - AI Safety Monitoring System',
            'title': f'Test {severity} Safety Alert',
            'body': 'This is a test alert to verify your notification system is working correctly.',
            'alert_id': 'TEST-' + datetime.utcnow().strftime('%Y%m%d-%H%M%S'),
            'action_url': 'https://your-dashboard/alerts',
        }
        
        # Send notifications
        contacts_data = [
            {
                'contact_name': c.contact_name,
                'phone_number': c.phone_number,
                'email': c.email,
                'email_enabled': c.email_enabled,
                'sms_enabled': c.sms_enabled,
                'whatsapp_enabled': c.whatsapp_enabled,
                'alert_low': c.alert_low,
                'alert_medium': c.alert_medium,
                'alert_high': c.alert_high,
                'alert_critical': c.alert_critical,
            }
            for c in contacts
        ]
        
        result = advanced_notification_service.send_emergency_alert(
            alert_data,
            contacts_data
        )
        
        logger.info(f"Test alert sent: {result['successful']}/{result['total_contacts']} successful")
        
        return jsonify({
            'success': True,
            'message': f'Test alert sent to {result["successful"]} contacts',
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Error sending test alert: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
