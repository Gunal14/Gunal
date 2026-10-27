"""
Backend Utilities
Common utility functions and helpers
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Format API responses consistently"""
    
    @staticmethod
    def success(data: Any = None, message: str = 'Success', status_code: int = 200):
        """Format successful response"""
        response = {
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response), status_code
    
    @staticmethod
    def error(message: str, error_code: str = None, status_code: int = 400, details: Dict = None):
        """Format error response"""
        response = {
            'success': False,
            'message': message,
            'error_code': error_code or 'UNKNOWN_ERROR'
        }
        if details:
            response['details'] = details
        return jsonify(response), status_code
    
    @staticmethod
    def paginated(items: list, total: int, page: int, per_page: int, message: str = 'Retrieved successfully'):
        """Format paginated response"""
        response = {
            'success': True,
            'message': message,
            'items': items,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        }
        return jsonify(response), 200

class ValidationHelper:
    """Validate request data"""
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: list) -> Optional[tuple]:
        """
        Validate required fields are present
        
        Returns:
            Error tuple if validation fails, None if valid
        """
        missing = [f for f in required_fields if f not in data or not data[f]]
        if missing:
            return ResponseFormatter.error(
                f'Missing required fields: {", ".join(missing)}',
                'VALIDATION_ERROR',
                400
            )
        return None
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number"""
        import re
        # International phone format
        pattern = r'^[+]?[0-9\-\s()]{10,}$'
        return re.match(pattern, phone) is not None

class PaginationHelper:
    """Handle pagination logic"""
    
    @staticmethod
    def get_pagination_params(request_args) -> tuple:
        """
        Extract pagination parameters from request
        
        Returns:
            (page, per_page) tuple
        """
        page = request_args.get('page', 1, type=int)
        per_page = request_args.get('per_page', 20, type=int)
        
        # Validate
        page = max(1, page)
        per_page = min(100, max(1, per_page))  # Max 100 items per page
        
        return page, per_page
    
    @staticmethod
    def paginate_list(items: list, page: int, per_page: int) -> tuple:
        """
        Paginate a list
        
        Returns:
            (paginated_items, total_count)
        """
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        
        return items[start:end], total

class DateTimeHelper:
    """Handle datetime operations"""
    
    @staticmethod
    def parse_datetime(date_str: str) -> Optional[datetime]:
        """Parse ISO format datetime string"""
        try:
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """Format datetime to string"""
        return dt.strftime(format_str)
    
    @staticmethod
    def get_time_difference(dt1: datetime, dt2: datetime) -> str:
        """Get human-readable time difference"""
        diff = abs((dt2 - dt1).total_seconds())
        
        if diff < 60:
            return f"{int(diff)} seconds"
        elif diff < 3600:
            return f"{int(diff / 60)} minutes"
        elif diff < 86400:
            return f"{int(diff / 3600)} hours"
        else:
            return f"{int(diff / 86400)} days"

class LoggingHelper:
    """Enhanced logging utilities"""
    
    @staticmethod
    def log_api_request(user_id: int = None, method: str = None, 
                       endpoint: str = None, status_code: int = None):
        """Log API request"""
        method = method or request.method
        endpoint = endpoint or request.path
        user_id = user_id or 'anonymous'
        
        logger.info(f"API Request: {method} {endpoint} by {user_id}")
    
    @staticmethod
    def log_api_response(endpoint: str, status_code: int, response_time: float):
        """Log API response"""
        level = 'info' if status_code < 400 else 'warning' if status_code < 500 else 'error'
        getattr(logger, level)(
            f"API Response: {endpoint} - Status: {status_code} - Time: {response_time:.2f}ms"
        )

class SecurityHelper:
    """Security-related utilities"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove potentially dangerous characters from filename"""
        import re
        filename = re.sub(r'[^\w\s.-]', '', filename)
        filename = re.sub(r'[\s]+', '_', filename)
        return filename[:255]  # Max 255 chars
    
    @staticmethod
    def is_safe_file_path(filepath: str, base_path: str) -> bool:
        """Check if file path is safe (no directory traversal)"""
        import os
        real_path = os.path.realpath(filepath)
        real_base = os.path.realpath(base_path)
        
        return real_path.startswith(real_base)
    
    @staticmethod
    def rate_limit_key(user_id: int = None, ip_address: str = None) -> str:
        """Generate rate limit key"""
        identifier = user_id or ip_address or 'anonymous'
        endpoint = request.endpoint or 'unknown'
        return f"rate_limit:{identifier}:{endpoint}"

class CacheHelper:
    """Caching utilities"""
    
    _cache = {}
    
    @staticmethod
    def set(key: str, value: Any, ttl_seconds: int = 300):
        """Set cache value"""
        CacheHelper._cache[key] = {
            'value': value,
            'expires_at': datetime.utcnow().timestamp() + ttl_seconds
        }
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get cache value"""
        if key not in CacheHelper._cache:
            return None
        
        item = CacheHelper._cache[key]
        if datetime.utcnow().timestamp() > item['expires_at']:
            del CacheHelper._cache[key]
            return None
        
        return item['value']
    
    @staticmethod
    def clear(pattern: str = None):
        """Clear cache"""
        if pattern:
            import re
            regex = re.compile(pattern)
            CacheHelper._cache = {k: v for k, v in CacheHelper._cache.items() 
                                 if not regex.match(k)}
        else:
            CacheHelper._cache.clear()

def handle_exceptions(f):
    """Decorator to handle common exceptions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return ResponseFormatter.error(str(e), 'VALIDATION_ERROR', 400)
        except KeyError as e:
            logger.error(f"Missing key: {e}")
            return ResponseFormatter.error(f'Missing required field: {e}', 'MISSING_FIELD', 400)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return ResponseFormatter.error('Internal server error', 'SERVER_ERROR', 500)
    
    return decorated_function
