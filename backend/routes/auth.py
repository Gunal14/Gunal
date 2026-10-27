"""
Authentication Routes
Registration, login, token refresh, logout endpoints with database/in-memory integration
"""

from flask import Blueprint, request, jsonify
# from flask_limiter import Limiter  # Temporarily disabled
from functools import wraps
from backend.utils import ResponseFormatter, ValidationHelper
import logging
import re
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

# Delayed database imports - avoid import-time failures
_db = None
_user = None
USE_DATABASE = False

def _init_db():
    """Initialize database imports on first use"""
    global _db, _user, USE_DATABASE, db, User, USE_DATABASE
    if not USE_DATABASE:
        try:
            from backend.database.models import db as db_inst, User as user_cls
            _db = db_inst
            _user = user_cls
            db = _db
            User = _user
            USE_DATABASE = True
            logger.info("Database models loaded successfully")
        except Exception as e:
            logger.warning(f"Database unavailable: {e}")
            USE_DATABASE = False

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# In-memory user storage (fallback if database unavailable)
class InMemoryUserStore:
    """Simple in-memory user storage"""
    def __init__(self):
        self.users = {}
        self.next_user_id = 1
        self.load_from_file()
    
    def load_from_file(self):
        """Load users from JSON file if exists"""
        try:
            user_file = "users.json"
            if os.path.exists(user_file):
                with open(user_file, 'r') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
                    self.next_user_id = data.get('next_user_id', len(self.users) + 1)
        except Exception as e:
            logger.warning(f"Could not load users from file: {e}")
    
    def save_to_file(self):
        """Save users to JSON file"""
        try:
            with open("users.json", 'w') as f:
                json.dump({
                    'users': self.users,
                    'next_user_id': self.next_user_id
                }, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Could not save users to file: {e}")
    
    def create_user(self, username, email, password_hash, first_name, last_name):
        """Create new user"""
        user_id = str(self.next_user_id)
        self.next_user_id += 1
        
        self.users[username] = {
            'id': int(user_id),
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'first_name': first_name,
            'last_name': last_name,
            'role': 'operator',
            'department': None,
            'is_active': True,
            'created_at': datetime.utcnow().isoformat(),
            'last_login': None
        }
        self.save_to_file()
        return self.users[username]
    
    def get_user_by_username(self, username):
        """Get user by username"""
        return self.users.get(username)
    
    def get_user_by_email(self, email):
        """Get user by email"""
        for user in self.users.values():
            if user['email'] == email:
                return user
        return None
    
    def update_user(self, username, **kwargs):
        """Update user"""
        if username in self.users:
            self.users[username].update(kwargs)
            self.save_to_file()
            return True
        return False
    
    def user_exists(self, username):
        """Check if user exists"""
        return username in self.users
    
    def email_exists(self, email):
        """Check if email exists"""
        for user in self.users.values():
            if user['email'] == email:
                return True
        return False

# Initialize user store
user_store = InMemoryUserStore()

# Placeholder for initialized services
auth_service = None
session_service = None

def init_auth_routes(app, auth_svc, session_svc, limiter=None):
    """Initialize auth routes with service instances"""
    global auth_service, session_service, rate_limiter
    auth_service = auth_svc
    session_service = session_svc
    rate_limiter = limiter
    # _init_db()  # Try to load database on init - temporarily disabled
    app.register_blueprint(auth_bp)

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

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_mobile_number(phone_number: str) -> tuple:
    """
    Validate mobile phone number format
    Accepts formats like:
    - +1-234-567-8900
    - +44 20 7946 0958
    - 1234567890
    - +1234567890
    Returns: (is_valid, formatted_number, country_code)
    """
    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone_number)
    
    # Extract country code if present
    country_code = '+1'  # Default to US
    number = cleaned
    
    if cleaned.startswith('+'):
        # Extract country code (1-3 digits after +)
        match = re.match(r'^\+(\d{1,3})(\d{6,14})$', cleaned)
        if match:
            country_code = f'+{match.group(1)}'
            number = match.group(2)
        else:
            return False, None, None
    else:
        # Number without country code - must be 7-15 digits
        if not re.match(r'^\d{7,15}$', cleaned):
            return False, None, None
        number = cleaned
    
    # Format as E.164 standard: +[country code][number]
    formatted = f'{country_code}{number}'
    
    return True, formatted, country_code

def validate_password(password: str) -> tuple:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
# @rate_limiter.limit("5 per hour")  # Temporarily disabled
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        error = ValidationHelper.validate_required_fields(
            data, ['username', 'email', 'password', 'confirm_password', 'mobile_number']
        )
        if error:
            return error
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        mobile_number = data.get('mobile_number', '').strip()
        
        # Additional validation
        if len(username) < 3:
            return ResponseFormatter.error(
                'Username must be at least 3 characters long',
                'VALIDATION_ERROR',
                400
            )
        
        if not ValidationHelper.validate_email(email):
            return ResponseFormatter.error(
                'Invalid email format',
                'VALIDATION_ERROR',
                400
            )
        
        if not ValidationHelper.validate_phone(mobile_number):
            return ResponseFormatter.error(
                'Invalid mobile number format',
                'VALIDATION_ERROR',
                400
            )
        
        if password != confirm_password:
            return ResponseFormatter.error(
                'Passwords do not match',
                'VALIDATION_ERROR',
                400
            )
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return ResponseFormatter.error(
                message,
                'VALIDATION_ERROR',
                400
            )
        
        # Check if username already exists
        if USE_DATABASE:
            existing_user = User.query.filter_by(username=username).first()
            existing_email = User.query.filter_by(email=email).first()
        else:
            existing_user = user_store.get_user_by_username(username)
            existing_email = user_store.get_user_by_email(email)
        
        if existing_user:
            return ResponseFormatter.error(
                'Username already exists',
                'VALIDATION_ERROR',
                409
            )
        
        if existing_email:
            return ResponseFormatter.error(
                'Email already registered',
                'VALIDATION_ERROR',
                409
            )
        # Create new user
        try:
            password_hash = auth_service.hash_password(password)
            
            if USE_DATABASE:
                new_user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    first_name=first_name or username,
                    last_name=last_name or '',
                    mobile_number=formatted_phone,
                    country_code=country_code,
                    phone_verified=False,
                    role='operator',
                    is_active=True
                )
                db.session.add(new_user)
                db.session.commit()
                
                user_data = {
                    'user_id': new_user.id,
                    'username': new_user.username,
                    'email': new_user.email,
                    'first_name': new_user.first_name,
                    'last_name': new_user.last_name,
                    'mobile_number': new_user.mobile_number,
                    'role': new_user.role
                }
            else:
                user_data = user_store.create_user(username, email, password_hash, 
                                                   first_name or username, last_name or '')
                # Add mobile number to user store
                user_data['mobile_number'] = formatted_phone
                user_data['country_code'] = country_code
                user_data['phone_verified'] = False
                user_store.save_to_file()
                
                # Remove sensitive data from response
                user_response = {
                    'user_id': user_data['id'],
                    'username': user_data['username'],
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'mobile_number': user_data['mobile_number'],
                    'role': user_data['role']
                }
                user_data = user_response
            
            logger.info(f"New user registered: {username} ({email}) with mobile {formatted_phone}")
            
            return ResponseFormatter.success(
                {'user': user_data},
                'Registration successful! Please login with your credentials.',
                201
            )
        
        except Exception as e:
            if USE_DATABASE:
                db.session.rollback()
            logger.error(f"Error creating user: {e}")
            return ResponseFormatter.error(
                'Failed to create user account',
                'INTERNAL_ERROR',
                500
            )
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'error': 'Registration failed'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint with database/in-memory verification"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password required'
            }), 400
        
        # Query user from database or in-memory store
        if USE_DATABASE:
            user = User.query.filter_by(username=username).first()
        else:
            user = user_store.get_user_by_username(username)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
        
        # Check if user is active
        is_active = user.is_active if USE_DATABASE else user.get('is_active', True)
        if not is_active:
            return jsonify({
                'success': False,
                'error': 'User account is inactive'
            }), 403
        
        # Get password hash
        password_hash = user.password_hash if USE_DATABASE else user.get('password_hash')
        
        # Verify password
        if not auth_service.verify_password(password, password_hash):
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
        
        # Get user info
        if USE_DATABASE:
            user_id = user.id
            user_role = user.role
            user_email = user.email
            user_first_name = user.first_name
            user_last_name = user.last_name
        else:
            user_id = user.get('id')
            user_role = user.get('role', 'operator')
            user_email = user.get('email')
            user_first_name = user.get('first_name')
            user_last_name = user.get('last_name')
        
        # Create tokens
        access_token = auth_service.create_access_token(
            user_id=user_id,
            username=username,
            role=user_role
        )
        
        refresh_token = auth_service.create_refresh_token(
            user_id=user_id,
            username=username
        )
        
        if not access_token or not refresh_token:
            return jsonify({
                'success': False,
                'error': 'Failed to create tokens'
            }), 500
        
        # Update last login time
        if USE_DATABASE:
            user.last_login = datetime.utcnow()
            db.session.commit()
        else:
            user_store.update_user(username, last_login=datetime.utcnow().isoformat())
        
        # Create session
        ip_address = request.remote_addr
        session_id = session_service.create_session(user_id, access_token, ip_address)
        
        logger.info(f"User {username} logged in successfully")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'user_id': user_id,
                'username': username,
                'email': user_email,
                'first_name': user_first_name,
                'last_name': user_last_name,
                'role': user_role
            },
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': 3600  # 1 hour in seconds
            },
            'session_id': session_id
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Login failed'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """User logout endpoint"""
    try:
        user_id = request.user['user_id']
        username = request.user['username']
        
        logger.info(f"User {username} (ID: {user_id}) logged out")
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
    
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({
            'success': False,
            'error': 'Logout failed'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token"""
    try:
        data = request.get_json()
        refresh_token_str = data.get('refresh_token')
        
        if not refresh_token_str:
            return jsonify({
                'success': False,
                'error': 'Refresh token required'
            }), 400
        
        new_access_token = auth_service.refresh_access_token(refresh_token_str)
        
        if not new_access_token:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired refresh token'
            }), 401
        
        return jsonify({
            'success': True,
            'message': 'Token refreshed successfully',
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }), 200
    
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({
            'success': False,
            'error': 'Token refresh failed'
        }), 500

@auth_bp.route('/validate', methods=['GET'])
@require_auth
def validate_token():
    """Validate current token"""
    try:
        return jsonify({
            'success': True,
            'message': 'Token is valid',
            'valid': True,
            'user': {
                'user_id': request.user['user_id'],
                'username': request.user['username'],
                'role': request.user['role']
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Validation failed'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user information"""
    try:
        user_id = request.user['user_id']
        username = request.user['username']
        
        if USE_DATABASE:
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            return jsonify({
                'success': True,
                'user': {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'department': user.department,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
            }), 200
        else:
            user = user_store.get_user_by_username(username)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            return jsonify({
                'success': True,
                'user': {
                    'user_id': user.get('id'),
                    'username': user.get('username'),
                    'email': user.get('email'),
                    'first_name': user.get('first_name'),
                    'last_name': user.get('last_name'),
                    'role': user.get('role'),
                    'department': user.get('department'),
                    'is_active': user.get('is_active'),
                    'created_at': user.get('created_at'),
                    'last_login': user.get('last_login')
                }
            }), 200
    
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get user info'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            return jsonify({
                'success': False,
                'error': 'Current password, new password, and confirmation required'
            }), 400
        
        username = request.user['username']
        
        if USE_DATABASE:
            user_id = request.user['user_id']
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            password_hash = user.password_hash
        else:
            user = user_store.get_user_by_username(username)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            password_hash = user.get('password_hash')
        
        # Verify current password
        if not auth_service.verify_password(current_password, password_hash):
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 401
        
        # Validate new password
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'error': 'New passwords do not match'
            }), 400
        
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Update password
        new_password_hash = auth_service.hash_password(new_password)
        
        if USE_DATABASE:
            user.password_hash = new_password_hash
            db.session.commit()
        else:
            user_store.update_user(username, password_hash=new_password_hash)
        
        logger.info(f"Password changed for user {username}")
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
    
    except Exception as e:
        if USE_DATABASE:
            db.session.rollback()
        logger.error(f"Error changing password: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to change password'
        }), 500

@auth_bp.route('/sessions', methods=['GET'])
@require_auth
def get_sessions():
    """Get all active sessions for current user"""
    try:
        user_id = request.user['user_id']
        sessions = session_service.get_user_sessions(user_id)
        
        return jsonify({
            'success': True,
            'session_count': len(sessions),
            'sessions': sessions
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get sessions'
        }), 500

