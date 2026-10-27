"""
Authentication and Authorization Service
JWT token management, password hashing, role-based access control
"""

import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from functools import wraps
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

class AuthenticationService:
    """Handle user authentication and JWT tokens"""
    
    def __init__(self, secret_key: str, access_token_expires: int = 3600, 
                 refresh_token_expires: int = 2592000):
        """
        Initialize authentication service
        
        Args:
            secret_key: Secret key for token signing
            access_token_expires: Access token expiration time in seconds (default 1 hour)
            refresh_token_expires: Refresh token expiration time in seconds (default 30 days)
        """
        self.secret_key = secret_key
        self.access_token_expires = access_token_expires
        self.refresh_token_expires = refresh_token_expires
        self.algorithm = 'HS256'
    
    def hash_password(self, password: str) -> str:
        """Hash password using Werkzeug"""
        return generate_password_hash(password, method='pbkdf2:sha256')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return check_password_hash(password_hash, password)
    
    def create_access_token(self, user_id: int, username: str, role: str) -> str:
        """
        Create JWT access token
        
        Args:
            user_id: User ID
            username: Username
            role: User role
        
        Returns:
            JWT token string
        """
        try:
            payload = {
                'user_id': user_id,
                'username': username,
                'role': role,
                'type': 'access',
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=self.access_token_expires)
            }
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            return None
    
    def create_refresh_token(self, user_id: int, username: str) -> str:
        """
        Create JWT refresh token
        
        Args:
            user_id: User ID
            username: Username
        
        Returns:
            JWT refresh token string
        """
        try:
            payload = {
                'user_id': user_id,
                'username': username,
                'type': 'refresh',
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=self.refresh_token_expires)
            }
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            return None
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token to verify
        
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Generate new access token from refresh token
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            New access token or None if invalid
        """
        try:
            payload = self.verify_token(refresh_token)
            if payload and payload.get('type') == 'refresh':
                return self.create_access_token(
                    payload['user_id'],
                    payload['username'],
                    payload.get('role', 'operator')
                )
            return None
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None

class AuthorizationService:
    """Handle authorization and role-based access control"""
    
    # Define role permissions
    ROLE_PERMISSIONS = {
        'admin': {
            'user_management': True,
            'system_settings': True,
            'report_generation': True,
            'incident_management': True,
            'camera_configuration': True,
            'data_export': True,
            'audit_log_access': True,
            'shift_management': True,
            'alert_configuration': True
        },
        'supervisor': {
            'user_management': False,
            'system_settings': False,
            'report_generation': True,
            'incident_management': True,
            'camera_configuration': False,
            'data_export': True,
            'audit_log_access': True,
            'shift_management': True,
            'alert_configuration': True
        },
        'operator': {
            'user_management': False,
            'system_settings': False,
            'report_generation': False,
            'incident_management': True,
            'camera_configuration': False,
            'data_export': False,
            'audit_log_access': False,
            'shift_management': False,
            'alert_configuration': False
        }
    }
    
    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        """
        Check if role has permission
        
        Args:
            role: User role
            permission: Required permission
        
        Returns:
            True if role has permission
        """
        role_perms = AuthorizationService.ROLE_PERMISSIONS.get(role, {})
        return role_perms.get(permission, False)
    
    @staticmethod
    def has_any_permission(role: str, permissions: list) -> bool:
        """Check if role has any of the given permissions"""
        return any(AuthorizationService.has_permission(role, perm) for perm in permissions)
    
    @staticmethod
    def has_all_permissions(role: str, permissions: list) -> bool:
        """Check if role has all given permissions"""
        return all(AuthorizationService.has_permission(role, perm) for perm in permissions)

class SessionManagementService:
    """Manage user sessions"""
    
    def __init__(self):
        """Initialize session management"""
        self.active_sessions = {}
    
    def create_session(self, user_id: int, token: str, ip_address: str) -> str:
        """
        Create new session
        
        Args:
            user_id: User ID
            token: Authentication token
            ip_address: User IP address
        
        Returns:
            Session ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            'user_id': user_id,
            'token': token,
            'ip_address': ip_address,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow()
        }
        logger.info(f"Session created for user {user_id}: {session_id}")
        return session_id
    
    def validate_session(self, session_id: str, current_ip: str) -> bool:
        """
        Validate whether session is still active
        
        Args:
            session_id: Session ID to validate
            current_ip: Current user IP address
        
        Returns:
            True if session is valid
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        # Check IP address for security
        if session['ip_address'] != current_ip:
            logger.warning(f"IP mismatch for session {session_id}")
            return False
        
        # Check session timeout (30 minutes)
        if datetime.utcnow() - session['last_activity'] > timedelta(minutes=30):
            self.remove_session(session_id)
            return False
        
        return True
    
    def update_session_activity(self, session_id: str):
        """Update session last activity time"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['last_activity'] = datetime.utcnow()
    
    def remove_session(self, session_id: str):
        """Remove session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Session removed: {session_id}")
    
    def get_user_sessions(self, user_id: int) -> list:
        """Get all active sessions for a user"""
        return [
            session_id for session_id, session in self.active_sessions.items()
            if session['user_id'] == user_id
        ]

class AuditService:
    """Audit logging and compliance tracking"""
    
    def __init__(self, db_session):
        """Initialize audit service"""
        self.db = db_session
    
    def log_action(self, user_id: int, action: str, table_name: str, 
                   record_id: int, old_values: Dict = None, new_values: Dict = None,
                   ip_address: str = None) -> bool:
        """
        Log user action for audit trail
        
        Args:
            user_id: User performing action
            action: Action type (create, update, delete)
            table_name: Database table affected
            record_id: Record ID affected
            old_values: Previous values
            new_values: New values
            ip_address: User IP address
        
        Returns:
            True if logged successfully
        """
        try:
            logger.info(
                f"Audit: User {user_id} / Action: {action} / "
                f"Table: {table_name} / Record: {record_id} / IP: {ip_address}"
            )
            return True
        except Exception as e:
            logger.error(f"Error logging action: {e}")
            return False
    
    def log_login(self, user_id: int, ip_address: str, success: bool = True) -> bool:
        """Log login attempt"""
        try:
            status = "SUCCESS" if success else "FAILED"
            logger.info(f"Audit: Login {status} - User {user_id} from {ip_address}")
            return True
        except Exception as e:
            logger.error(f"Error logging login: {e}")
            return False
    
    def log_configuration_change(self, user_id: int, config_key: str, 
                                old_value: str, new_value: str) -> bool:
        """Log system configuration changes"""
        try:
            logger.info(
                f"Audit: Config Change by User {user_id} / "
                f"Key: {config_key} / Old: {old_value} -> New: {new_value}"
            )
            return True
        except Exception as e:
            logger.error(f"Error logging config change: {e}")
            return False
