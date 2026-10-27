"""
Advanced Backend Configuration
Production-ready settings with environment support
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Core
    DEBUG = False
    TESTING = False
    ENV = 'production'
    REQUIRE_AUTH = True  # Require authentication for API
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///safety_monitoring.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour in seconds
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days in seconds
    
    # Camera
    CAMERA_DEFAULT_ID = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    MAX_CAMERAS = 16
    
    # Detection
    HELMET_THRESHOLD = 0.5
    WORKER_THRESHOLD = 0.5
    ALERT_COOLDOWN = 5
    MIN_DETECTION_FRAMES = 3
    
    # Alert Settings
    ALERT_ENABLED = True
    EMAIL_ALERTS_ENABLED = True
    SMS_ALERTS_ENABLED = False
    SOUND_ALERTS_ENABLED = True
    WEBHOOK_ALERTS_ENABLED = True
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@safety-monitor.local'
    
    # Data Retention
    LOG_RETENTION_DAYS = 90
    INCIDENT_RETENTION_DAYS = 180
    VIDEO_RETENTION_DAYS = 30
    
    # API
    API_VERSION = 'v2.0'
    API_TITLE = 'AI Safety Monitoring System API'
    RateLimiter_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'
    LOG_MAX_BYTES = 10485760  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Performance
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Pagination
    PAGINATION_DEFAULT_LIMIT = 50
    PAGINATION_MAX_LIMIT = 500

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    ENV = 'development'
    REQUIRE_AUTH = False  # Disable auth in development
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = True
    SECRET_KEY = "dev-secret-key"
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    # AI detection thresholds
    DETECTION_THRESHOLD_HELMET = 0.5
    DETECTION_THRESHOLD_HELMET = 0.5
    DETECTION_THRESHOLD_VEST = 0.5
    DETECTION_THRESHOLD_PERSON = 0.5
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    ENV = 'production'
    SESSION_COOKIE_SECURE = True
    CORS_ORIGINS = [
        "https://yourdomain.com"
    ]

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

def get_config(config_name=None):
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
