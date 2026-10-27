"""
Configuration and utility functions for Safety Monitoring System
"""

import os
from datetime import datetime, timedelta

# ============ APPLICATION CONFIG ============
class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///safety_monitoring.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required")
    
    # Camera settings
    CAMERA_ID = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Detection settings
    HELMET_THRESHOLD = 0.5
    WORKER_THRESHOLD = 0.5
    ALERT_COOLDOWN = 5  # seconds
    
    # Alert settings
    EMAIL_ALERTS_ENABLED = True
    SOUND_ALERTS_ENABLED = True
    ALERT_COOLDOWN_PERIOD = 60  # seconds between same alerts
    
    # Data retention
    LOG_RETENTION_DAYS = 90
    INCIDENT_RETENTION_DAYS = 180

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# ============ UTILITIES ============
class DateUtils:
    """Date and time utilities"""
    
    @staticmethod
    def get_timestamp():
        """Get current timestamp"""
        return datetime.utcnow()
    
    @staticmethod
    def days_ago(days):
        """Get datetime from days ago"""
        return datetime.utcnow() - timedelta(days=days)
    
    @staticmethod
    def format_time(dt):
        """Format datetime for display"""
        if not dt:
            return "N/A"
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def is_within_minutes(dt, minutes):
        """Check if datetime is within N minutes"""
        if not dt:
            return False
        return (datetime.utcnow() - dt).total_seconds() < (minutes * 60)

class AlertUtils:
    """Alert and notification utilities"""
    
    ALERT_TYPES = {
        'MISSING_HELMET': {
            'name': 'Missing Helmet',
            'severity': 'HIGH',
            'icon': 'fas fa-exclamation-circle'
        },
        'NO_SAFETY_GEAR': {
            'name': 'No Safety Gear',
            'severity': 'HIGH',
            'icon': 'fas fa-exclamation-triangle'
        },
        'AREA_OVERCROWDED': {
            'name': 'Area Overcrowded',
            'severity': 'MEDIUM',
            'icon': 'fas fa-people-group'
        },
        'EQUIPMENT_MALFUNCTION': {
            'name': 'Equipment Malfunction',
            'severity': 'HIGH',
            'icon': 'fas fa-tools'
        },
        'UNAUTHORIZED_ENTRY': {
            'name': 'Unauthorized Entry',
            'severity': 'CRITICAL',
            'icon': 'fas fa-ban'
        }
    }
    
    @staticmethod
    def get_alert_info(alert_type):
        """Get alert information"""
        return AlertUtils.ALERT_TYPES.get(
            alert_type,
            {
                'name': 'Unknown Alert',
                'severity': 'MEDIUM',
                'icon': 'fas fa-info-circle'
            }
        )
    
    @staticmethod
    def format_alert(alert_type, details=None):
        """Format alert for display"""
        info = AlertUtils.get_alert_info(alert_type)
        message = info['name']
        if details:
            message += f": {details}"
        return message

class StatisticsUtils:
    """Statistics and reporting utilities"""
    
    @staticmethod
    def calculate_safety_score(incidents, period_days=30):
        """Calculate safety score (0-100)"""
        # Score based on incident count and severity
        high_count = len([i for i in incidents if i.severity == 'HIGH'])
        medium_count = len([i for i in incidents if i.severity == 'MEDIUM'])
        
        # Scoring: -5 per high, -2 per medium
        score = 100 - (high_count * 5) - (medium_count * 2)
        return max(0, score)
    
    @staticmethod
    def calculate_compliance_rate(total_workers, workers_with_gear):
        """Calculate compliance rate percentage"""
        if total_workers == 0:
            return 100
        return (workers_with_gear / total_workers) * 100
    
    @staticmethod
    def get_incident_summary(incidents):
        """Get summary statistics for incidents"""
        return {
            'total': len(incidents),
            'high_severity': len([i for i in incidents if i.severity == 'HIGH']),
            'medium_severity': len([i for i in incidents if i.severity == 'MEDIUM']),
            'low_severity': len([i for i in incidents if i.severity == 'LOW']),
        }

class ValidationUtils:
    """Input validation utilities"""
    
    @staticmethod
    def validate_camera_id(camera_id):
        """Validate camera ID"""
        try:
            cam_id = int(camera_id)
            return 0 <= cam_id <= 10
        except:
            return False
    
    @staticmethod
    def validate_threshold(threshold):
        """Validate threshold value"""
        try:
            val = float(threshold)
            return 0.0 <= val <= 1.0
        except:
            return False
    
    @staticmethod
    def validate_resolution(resolution):
        """Validate resolution format"""
        try:
            parts = resolution.split('x')
            if len(parts) != 2:
                return False
            width, height = int(parts[0]), int(parts[1])
            return width > 0 and height > 0
        except:
            return False

class LoggingUtils:
    """Logging utilities"""
    
    @staticmethod
    def log_event(event_type, message, details=None):
        """Log application event"""
        timestamp = DateUtils.get_timestamp()
        log_entry = {
            'timestamp': timestamp,
            'type': event_type,
            'message': message,
            'details': details
        }
        print(f"[{timestamp}] {event_type}: {message}")
        return log_entry
    
    @staticmethod
    def log_detection(detection_data):
        """Log detection event"""
        return LoggingUtils.log_event(
            'DETECTION',
            f"Workers: {detection_data.get('workers_detected')}, "
            f"Helmets: {detection_data.get('helmets_detected')}",
            detection_data
        )
    
    @staticmethod
    def log_alert(alert_type, severity):
        """Log alert event"""
        return LoggingUtils.log_event(
            'ALERT',
            f"{alert_type} (Severity: {severity})"
        )

class PerformanceUtils:
    """Performance monitoring utilities"""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, name):
        """Start a performance timer"""
        self.metrics[name] = {'start': datetime.utcnow()}
    
    def end_timer(self, name):
        """End a performance timer and get duration"""
        if name not in self.metrics:
            return None
        
        start = self.metrics[name]['start']
        duration = (datetime.utcnow() - start).total_seconds() * 1000  # ms
        self.metrics[name]['duration'] = duration
        return duration
    
    def get_metric(self, name):
        """Get metric value"""
        return self.metrics.get(name, {}).get('duration', None)

# Global performance tracker
perf_tracker = PerformanceUtils()

# ============ CONSTANTS ============
class Constants:
    """Application constants"""
    
    # Severity levels
    SEVERITY_LOW = 'LOW'
    SEVERITY_MEDIUM = 'MEDIUM'
    SEVERITY_HIGH = 'HIGH'
    SEVERITY_CRITICAL = 'CRITICAL'
    
    # Incident types
    INCIDENT_TYPE_HELMET = 'MISSING_HELMET'
    INCIDENT_TYPE_PPE = 'MISSING_PPE'
    INCIDENT_TYPE_OVERCROWDED = 'AREA_OVERCROWDED'
    INCIDENT_TYPE_UNAUTHORIZED = 'UNAUTHORIZED_ENTRY'
    
    # Status codes
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_INACTIVE = 'INACTIVE'
    STATUS_ERROR = 'ERROR'
    STATUS_MAINTENANCE = 'MAINTENANCE'
    
    # Detection states
    STATE_MONITORING = 'MONITORING'
    STATE_ALERT = 'ALERT'
    STATE_PAUSED = 'PAUSED'
    STATE_ERROR = 'ERROR'

# Get configuration based on environment
def get_config():
    """Get application configuration"""
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
