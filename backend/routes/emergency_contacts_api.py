"""
Emergency Contact Management Routes
CRUD operations for emergency contacts and alert settings
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

emergency_bp = Blueprint('emergency_contacts', __name__, url_prefix='/api/emergency-contacts')

# Database imports (delayed)
_db = None
_EmergencyContact = None
_User = None
USE_DATABASE = False


def _init_db():
    """Initialize database imports on first use"""
    global _db, _EmergencyContact, _User, USE_DATABASE
    if not USE_DATABASE:
        try:
            from backend.database.models import db as db_inst, EmergencyContact, User
            _db = db_inst
            _EmergencyContact = EmergencyContact
            _User = User
            USE_DATABASE = True
            logger.info("Database models loaded for emergency contacts")
        except Exception as e:
            logger.warning(f"Database unavailable: {e}")
            USE_DATABASE = False


def require_auth(f):
    """Authentication decorator"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        # Import auth service here to avoid circular imports
        from backend.services import AuthenticationService
        auth_service = AuthenticationService()
        
        payload = auth_service.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function


def validate_phone_number(phone_number: str) -> tuple:
    """
    Validate phone number format
    Returns: (is_valid, formatted_number, country_code)
    """
    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone_number)
    
    country_code = '+1'  # Default
    number = cleaned
    
    if cleaned.startswith('+'):
        match = re.match(r'^\+(\d{1,3})(\d{6,14})$', cleaned)
        if match:
            country_code = f'+{match.group(1)}'
            number = match.group(2)
        else:
            return False, None, None
    else:
        if not re.match(r'^\d{7,15}$', cleaned):
            return False, None, None
        number = cleaned
    
    formatted = f'{country_code}{number}'
    return True, formatted, country_code


def init_emergency_routes(app, auth_service=None):
    """Initialize emergency contact routes"""
    _init_db()
    app.register_blueprint(emergency_bp)


@emergency_bp.route('', methods=['GET'])
@require_auth
def get_emergency_contacts():
    """Get all emergency contacts for authenticated user"""
    try:
        user_id = request.user.get('user_id')
        
        if not USE_DATABASE:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        contacts = _EmergencyContact.query.filter_by(user_id=user_id, is_active=True).all()
        
        contacts_data = [{
            'id': c.id,
            'contact_name': c.contact_name,
            'phone_number': c.phone_number,
            'country_code': c.country_code,
            'email': c.email,
            'whatsapp_enabled': c.whatsapp_enabled,
            'sms_enabled': c.sms_enabled,
            'email_enabled': c.email_enabled,
            'alert_low': c.alert_low,
            'alert_medium': c.alert_medium,
            'alert_high': c.alert_high,
            'alert_critical': c.alert_critical,
            'verified': c.verified,
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in contacts]
        
        return jsonify({
            'success': True,
            'contacts': contacts_data,
            'total': len(contacts_data)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching emergency contacts: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch emergency contacts'
        }), 500


@emergency_bp.route('', methods=['POST'])
@require_auth
def add_emergency_contact():
    """Add a new emergency contact"""
    try:
        user_id = request.user.get('user_id')
        data = request.get_json()
        
        if not USE_DATABASE:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        # Validate required fields
        contact_name = data.get('contact_name', '').strip()
        phone_number = data.get('phone_number', '').strip()
        email = data.get('email', '').strip()
        
        if not contact_name or not phone_number:
            return jsonify({
                'success': False,
                'error': 'Contact name and phone number are required'
            }), 400
        
        # Validate phone number
        is_valid, formatted_phone, country_code = validate_phone_number(phone_number)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Invalid phone number format (e.g., +1-234-567-8900)'
            }), 400
        
        # Check limit (max 10 per user)
        existing_count = _EmergencyContact.query.filter_by(
            user_id=user_id, is_active=True
        ).count()
        
        if existing_count >= 10:
            return jsonify({
                'success': False,
                'error': 'Maximum 10 emergency contacts allowed'
            }), 400
        
        # Create new emergency contact
        new_contact = _EmergencyContact(
            user_id=user_id,
            contact_name=contact_name,
            phone_number=formatted_phone,
            country_code=country_code,
            email=email or None,
            whatsapp_enabled=data.get('whatsapp_enabled', True),
            sms_enabled=data.get('sms_enabled', True),
            email_enabled=data.get('email_enabled', False),
            alert_low=data.get('alert_low', False),
            alert_medium=data.get('alert_medium', True),
            alert_high=data.get('alert_high', True),
            alert_critical=data.get('alert_critical', True),
            is_active=True,
            verified=False
        )
        
        _db.session.add(new_contact)
        _db.session.commit()
        
        logger.info(f"Emergency contact added for user {user_id}: {contact_name}")
        
        return jsonify({
            'success': True,
            'message': 'Emergency contact added successfully',
            'contact': {
                'id': new_contact.id,
                'contact_name': new_contact.contact_name,
                'phone_number': new_contact.phone_number,
                'country_code': new_contact.country_code,
                'email': new_contact.email,
                'whatsapp_enabled': new_contact.whatsapp_enabled,
                'sms_enabled': new_contact.sms_enabled,
                'email_enabled': new_contact.email_enabled,
                'alert_low': new_contact.alert_low,
                'alert_medium': new_contact.alert_medium,
                'alert_high': new_contact.alert_high,
                'alert_critical': new_contact.alert_critical,
                'verified': new_contact.verified
            }
        }), 201
    
    except Exception as e:
        _db.session.rollback()
        logger.error(f"Error adding emergency contact: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to add emergency contact'
        }), 500


@emergency_bp.route('/<int:contact_id>', methods=['GET'])
@require_auth
def get_emergency_contact(contact_id):
    """Get specific emergency contact"""
    try:
        user_id = request.user.get('user_id')
        
        if not USE_DATABASE:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        contact = _EmergencyContact.query.filter_by(
            id=contact_id, user_id=user_id
        ).first()
        
        if not contact:
            return jsonify({
                'success': False,
                'error': 'Emergency contact not found'
            }), 404
        
        return jsonify({
            'success': True,
            'contact': {
                'id': contact.id,
                'contact_name': contact.contact_name,
                'phone_number': contact.phone_number,
                'country_code': contact.country_code,
                'email': contact.email,
                'whatsapp_enabled': contact.whatsapp_enabled,
                'sms_enabled': contact.sms_enabled,
                'email_enabled': contact.email_enabled,
                'alert_low': contact.alert_low,
                'alert_medium': contact.alert_medium,
                'alert_high': contact.alert_high,
                'alert_critical': contact.alert_critical,
                'verified': contact.verified,
                'created_at': contact.created_at.isoformat() if contact.created_at else None
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching emergency contact: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch emergency contact'
        }), 500


@emergency_bp.route('/<int:contact_id>', methods=['PUT'])
@require_auth
def update_emergency_contact(contact_id):
    """Update emergency contact"""
    try:
        user_id = request.user.get('user_id')
        data = request.get_json()
        
        if not USE_DATABASE:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        contact = _EmergencyContact.query.filter_by(
            id=contact_id, user_id=user_id
        ).first()
        
        if not contact:
            return jsonify({
                'success': False,
                'error': 'Emergency contact not found'
            }), 404
        
        # Update fields
        if 'contact_name' in data:
            contact.contact_name = data['contact_name'].strip()
        
        if 'phone_number' in data:
            is_valid, formatted_phone, country_code = validate_phone_number(data['phone_number'])
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': 'Invalid phone number format'
                }), 400
            contact.phone_number = formatted_phone
            contact.country_code = country_code
            contact.verified = False  # Reset verification
        
        if 'email' in data:
            contact.email = data['email'].strip() or None
        
        if 'whatsapp_enabled' in data:
            contact.whatsapp_enabled = data['whatsapp_enabled']
        if 'sms_enabled' in data:
            contact.sms_enabled = data['sms_enabled']
        if 'email_enabled' in data:
            contact.email_enabled = data['email_enabled']
        
        if 'alert_low' in data:
            contact.alert_low = data['alert_low']
        if 'alert_medium' in data:
            contact.alert_medium = data['alert_medium']
        if 'alert_high' in data:
            contact.alert_high = data['alert_high']
        if 'alert_critical' in data:
            contact.alert_critical = data['alert_critical']
        
        contact.updated_at = datetime.utcnow()
        
        _db.session.commit()
        
        logger.info(f"Emergency contact updated for user {user_id}: {contact.id}")
        
        return jsonify({
            'success': True,
            'message': 'Emergency contact updated successfully',
            'contact': {
                'id': contact.id,
                'contact_name': contact.contact_name,
                'phone_number': contact.phone_number,
                'country_code': contact.country_code,
                'email': contact.email,
                'whatsapp_enabled': contact.whatsapp_enabled,
                'sms_enabled': contact.sms_enabled,
                'email_enabled': contact.email_enabled,
                'alert_low': contact.alert_low,
                'alert_medium': contact.alert_medium,
                'alert_high': contact.alert_high,
                'alert_critical': contact.alert_critical,
                'verified': contact.verified
            }
        }), 200
    
    except Exception as e:
        _db.session.rollback()
        logger.error(f"Error updating emergency contact: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update emergency contact'
        }), 500


@emergency_bp.route('/<int:contact_id>', methods=['DELETE'])
@require_auth
def delete_emergency_contact(contact_id):
    """Delete emergency contact (soft delete)"""
    try:
        user_id = request.user.get('user_id')
        
        if not USE_DATABASE:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        contact = _EmergencyContact.query.filter_by(
            id=contact_id, user_id=user_id
        ).first()
        
        if not contact:
            return jsonify({
                'success': False,
                'error': 'Emergency contact not found'
            }), 404
        
        # Soft delete
        contact.is_active = False
        contact.updated_at = datetime.utcnow()
        
        _db.session.commit()
        
        logger.info(f"Emergency contact deleted for user {user_id}: {contact_id}")
        
        return jsonify({
            'success': True,
            'message': 'Emergency contact deleted successfully'
        }), 200
    
    except Exception as e:
        _db.session.rollback()
        logger.error(f"Error deleting emergency contact: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete emergency contact'
        }), 500


@emergency_bp.route('/<int:contact_id>/verify', methods=['POST'])
@require_auth
def verify_emergency_contact(contact_id):
    """
    Verify emergency contact phone number via OTP
    In production, send OTP via SMS/WhatsApp
    """
    try:
        user_id = request.user.get('user_id')
        data = request.get_json()
        
        if not USE_DATABASE:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        contact = _EmergencyContact.query.filter_by(
            id=contact_id, user_id=user_id
        ).first()
        
        if not contact:
            return jsonify({
                'success': False,
                'error': 'Emergency contact not found'
            }), 404
        
        # For demo: accept any 6-digit code
        # In production: validate against sent OTP
        otp = data.get('otp', '').strip()
        
        if not otp or len(otp) != 6 or not otp.isdigit():
            return jsonify({
                'success': False,
                'error': 'Invalid OTP format (must be 6 digits)'
            }), 400
        
        # Mock validation - in production, check against stored OTP
        contact.verified = True
        contact.verification_code = None
        contact.verified_at = datetime.utcnow()
        
        _db.session.commit()
        
        logger.info(f"Emergency contact verified for user {user_id}: {contact_id}")
        
        return jsonify({
            'success': True,
            'message': 'Emergency contact verified successfully'
        }), 200
    
    except Exception as e:
        _db.session.rollback()
        logger.error(f"Error verifying emergency contact: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to verify emergency contact'
        }), 500


@emergency_bp.route('/primary-number', methods=['GET'])
@require_auth
def get_primary_number():
    """Get user's primary (registered) mobile number"""
    try:
        user_id = request.user.get('user_id')
        
        if not USE_DATABASE:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        user = _User.query.filter_by(id=user_id).first()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'primary_number': user.mobile_number,
            'country_code': user.country_code,
            'phone_verified': user.phone_verified
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching primary number: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch primary number'
        }), 500


@emergency_bp.route('/primary-number', methods=['PUT'])
@require_auth
def update_primary_number():
    """Update user's primary mobile number"""
    try:
        user_id = request.user.get('user_id')
        data = request.get_json()
        
        if not USE_DATABASE:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
        
        user = _User.query.filter_by(id=user_id).first()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        phone_number = data.get('mobile_number', '').strip()
        
        if not phone_number:
            return jsonify({
                'success': False,
                'error': 'Mobile number is required'
            }), 400
        
        # Validate phone number
        is_valid, formatted_phone, country_code = validate_phone_number(phone_number)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Invalid phone number format'
            }), 400
        
        user.mobile_number = formatted_phone
        user.country_code = country_code
        user.phone_verified = False
        
        _db.session.commit()
        
        logger.info(f"Primary number updated for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Primary mobile number updated successfully',
            'mobile_number': user.mobile_number,
            'country_code': user.country_code
        }), 200
    
    except Exception as e:
        _db.session.rollback()
        logger.error(f"Error updating primary number: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update primary number'
        }), 500
