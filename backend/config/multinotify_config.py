"""
Multi-Camera Monitoring & Advanced Notification System Configuration File
Configures email, SMS, WhatsApp, risk scoring, and camera settings
"""

import os
from typing import Dict, List
from dataclasses import dataclass

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

EMAIL_CONFIG = {
    # SMTP Server Settings
    'smtp_host': os.environ.get('SMTP_HOST', 'smtp.gmail.com'),
    'smtp_port': int(os.environ.get('SMTP_PORT', '587')),
    'smtp_use_tls': os.environ.get('SMTP_USE_TLS', 'true').lower() == 'true',
    'smtp_username': os.environ.get('SMTP_USERNAME', 'your-email@gmail.com'),
    'smtp_password': os.environ.get('SMTP_PASSWORD', 'your-app-password'),
    
    # Email sender details
    'sender_email': os.environ.get('SENDER_EMAIL', 'safety-alerts@yourcompany.com'),
    'sender_name': os.environ.get('SENDER_NAME', 'AI Safety Monitoring System'),
    
    # Email templates
    'email_templates': {
        'subject_prefix': '[SAFETY ALERT]',
        'html_template_path': 'templates/alert_email.html',
    },
    
    # Email retry settings
    'max_retry_attempts': 3,
    'retry_delay_seconds': 5,
}

# ============================================================================
# TWILIO SMS & WHATSAPP CONFIGURATION
# ============================================================================

TWILIO_CONFIG = {
    # Twilio API credentials
    'account_sid': os.environ.get('TWILIO_ACCOUNT_SID', 'your_account_sid'),
    'auth_token': os.environ.get('TWILIO_AUTH_TOKEN', 'your_auth_token'),
    
    # SMS Settings
    'sms_from_number': os.environ.get('TWILIO_SMS_FROM', '+1234567890'),
    'sms_max_length': 160,  # SMS message can be split if longer
    'sms_enabled': os.environ.get('SMS_ENABLED', 'true').lower() == 'true',
    
    # WhatsApp Settings
    'whatsapp_from_number': os.environ.get('TWILIO_WHATSAPP_FROM', 'whatsapp:+1234567890'),
    'whatsapp_enabled': os.environ.get('WHATSAPP_ENABLED', 'true').lower() == 'true',
    
    # Retry settings
    'max_retry_attempts': 3,
    'retry_delay_seconds': 10,
}

# ============================================================================
# NOTIFICATION ROUTING CONFIGURATION
# ============================================================================

NOTIFICATION_ROUTING = {
    # Severity-based channel selection
    'routing_rules': {
        'LOW': {
            'channels': ['EMAIL'],
            'description': 'Email notifications only',
        },
        'MEDIUM': {
            'channels': ['EMAIL', 'SMS'],
            'description': 'Email and SMS notifications',
        },
        'HIGH': {
            'channels': ['EMAIL', 'SMS', 'WHATSAPP'],
            'description': 'All channels: Email, SMS, and WhatsApp',
        },
        'CRITICAL': {
            'channels': ['EMAIL', 'SMS', 'WHATSAPP'],
            'description': 'All channels with immediate delivery',
            'immediate': True,
        },
    },
    
    # Notification timing
    'quiet_hours': {
        'enabled': False,
        'start_hour': 22,  # 10 PM
        'end_hour': 6,     # 6 AM
        'allow_critical': True,  # Always send CRITICAL during quiet hours
    },
    
    # Rate limiting (prevent alert fatigue)
    'rate_limiting': {
        'enabled': True,
        'max_alerts_per_contact_per_hour': 10,
        'min_time_between_alerts_seconds': 60,
    },
}

# ============================================================================
# RISK SCORING CONFIGURATION
# ============================================================================

RISK_SCORING_CONFIG = {
    # Base risk scores for violation types
    'base_risk_scores': {
        'not_wearing_helmet': 85,
        'improper_helmet_fit': 65,
        'helmet_off_in_hazard_area': 90,
        'no_safety_vest': 75,
        'improper_ppe_fit': 60,
        'no_safety_glasses': 50,
        'no_gloves': 40,
        'hazmat_exposure': 95,
        'no_respiratory_protection': 80,
        'improper_posture': 35,
        'working_at_height_unprotected': 92,
        'electrical_hazard_exposure': 88,
        'blocked_emergency_exit': 85,
        'unsafe_behavior': 55,
    },
    
    # Multiplier weights
    'multipliers': {
        'confidence_weight': 1.0,           # Detection confidence (0-1)
        'hazard_level_weight': 1.2,        # Location hazard level multiplier
        'critical_area_multiplier': 2.0,   # High-hazard zones
        'night_shift_multiplier': 1.3,     # Fatigue factor for night shifts
        'repeated_violation_multiplier': 1.5,  # Pattern escalation
        'worker_fatigue_multiplier': 1.2,  # Detected fatigue signal
    },
    
    # Environmental factors
    'environmental_factors': {
        'lighting_dark_multiplier': 1.2,
        'lighting_bright_multiplier': 1.0,
        'poor_visibility_multiplier': 1.3,
        'high_temperature_multiplier': 1.15,
        'low_temperature_multiplier': 1.1,
        'high_humidity_multiplier': 1.1,
        'weather_rain_multiplier': 1.15,
        'air_quality_poor_multiplier': 1.2,
    },
    
    # Severity thresholds
    'severity_thresholds': {
        'LOW': 25,
        'MEDIUM': 50,
        'HIGH': 75,
        'CRITICAL': 100,  # Any score >= 100 becomes 100
    },
    
    # Pattern detection
    'pattern_detection': {
        'violation_window_hours': 8,       # 8-hour tracking window
        'repeated_violation_count': 3,     # Number of repeats to escalate
        'time_between_violations_minutes': 30,
    },
}

# ============================================================================
# MULTI-CAMERA COORDINATOR CONFIGURATION
# ============================================================================

MULTI_CAMERA_CONFIG = {
    # Camera limits
    'max_cameras': 40,
    'max_workers': 8,  # ThreadPoolExecutor workers
    
    # Frame processing
    'frame_queue_size': 100,
    'detection_queue_size': 50,
    'alert_queue_size': 50,
    
    # FPS and Resolution Optimization
    'fps_settings': {
        'normal_fps': 30,
        'reduced_fps': 20,
        'minimal_fps': 15,
        'cpu_threshold_for_reduction': 60,  # CPU % to trigger FPS reduction
        'memory_threshold_for_reduction': 75,  # Memory % to trigger FPS reduction
    },
    
    'resolution_settings': {
        'normal_resolution': (640, 480),
        'reduced_resolution': (528, 396),
        'minimal_resolution': (416, 312),
        'cpu_threshold_for_reduction': 70,
        'memory_threshold_for_reduction': 75,
    },
    
    # Resource monitoring
    'resource_monitor': {
        'check_interval_seconds': 5,
        'cpu_threshold_critical': 85,
        'memory_threshold_critical': 90,
    },
    
    # Alert processing
    'alert_timeout_seconds': 300,  # 5 minutes
    'alert_aggregation_window_seconds': 30,
}

# ============================================================================
# EMERGENCY CONTACT CONSTRAINTS
# ============================================================================

EMERGENCY_CONTACT_CONFIG = {
    'max_contacts_per_admin': 10,
    
    # Phone number validation
    'phone_validation': {
        'min_length': 10,
        'max_length': 15,
        'allowed_chars': '+0123456789',
    },
    
    # Default notification preferences
    'default_preferences': {
        'email_enabled': True,
        'sms_enabled': True,
        'whatsapp_enabled': True,
        'alert_low': False,
        'alert_medium': True,
        'alert_high': True,
        'alert_critical': True,
    },
}

# ============================================================================
# CAMERA HEALTH MONITORING CONFIGURATION
# ============================================================================

CAMERA_HEALTH_CONFIG = {
    # Connection thresholds
    'connection_timeout_seconds': 30,
    'connection_attempt_max': 5,
    'reconnect_interval_seconds': 10,
    
    # Performance thresholds
    'fps_threshold_warning': 15,
    'fps_threshold_critical': 5,
    'frame_loss_threshold': 20,  # %
    'latency_threshold_warning': 500,  # ms
    'latency_threshold_critical': 1000,  # ms
    
    # Resource thresholds
    'cpu_threshold_warning': 75,
    'cpu_threshold_critical': 90,
    'memory_threshold_warning': 80,
    'memory_threshold_critical': 95,
    'bandwidth_threshold_warning': 80,  # % of available
    
    # Uptime tracking
    'uptime_window_days': 7,  # Calculate uptime over 7 days
    'downtime_alert_threshold': 1,  # Alert if downtime > 1 event
}

# ============================================================================
# HAZARD LEVEL DEFINITIONS
# ============================================================================

HAZARD_LEVELS = {
    'LOW': {
        'description': 'Office, administrative areas',
        'risk_multiplier': 1.0,
    },
    'MEDIUM': {
        'description': 'Manufacturing floor, warehouse',
        'risk_multiplier': 1.5,
    },
    'HIGH': {
        'description': 'Chemical plant, heavy machinery area',
        'risk_multiplier': 2.0,
    },
    'CRITICAL': {
        'description': 'Explosive atmosphere, radiation zone',
        'risk_multiplier': 3.0,
    },
}

# ============================================================================
# SYSTEM INITIALIZATION FUNCTION
# ============================================================================

def initialize_notification_service():
    """
    Initialize the Advanced Notification Service with current config
    Call this during Flask app startup
    """
    from backend.services.advanced_notification_service import AdvancedNotificationService
    
    service = AdvancedNotificationService()
    
    try:
        service.initialize_channels({
            'email': {
                'smtp_host': EMAIL_CONFIG['smtp_host'],
                'smtp_port': EMAIL_CONFIG['smtp_port'],
                'smtp_use_tls': EMAIL_CONFIG['smtp_use_tls'],
                'smtp_username': EMAIL_CONFIG['smtp_username'],
                'smtp_password': EMAIL_CONFIG['smtp_password'],
                'sender_email': EMAIL_CONFIG['sender_email'],
                'enabled': True,
            },
            'sms': {
                'account_sid': TWILIO_CONFIG['account_sid'],
                'auth_token': TWILIO_CONFIG['auth_token'],
                'from_number': TWILIO_CONFIG['sms_from_number'],
                'enabled': TWILIO_CONFIG['sms_enabled'],
            },
            'whatsapp': {
                'account_sid': TWILIO_CONFIG['account_sid'],
                'auth_token': TWILIO_CONFIG['auth_token'],
                'from_number': TWILIO_CONFIG['whatsapp_from_number'],
                'enabled': TWILIO_CONFIG['whatsapp_enabled'],
            },
        })
        
        print("[OK] Advanced Notification Service initialized successfully")
        return service
    except Exception as e:
        print(f"[ERROR] Error initializing notification service: {e}")
        return None


def initialize_risk_prediction_engine():
    """
    Initialize the Risk Prediction Engine with current config
    Call this during Flask app startup
    """
    from backend.services.risk_prediction_service import RiskPredictionEngine
    
    engine = RiskPredictionEngine()
    
    print("[OK] Risk Prediction Engine initialized successfully")
    return engine


def initialize_multi_camera_coordinator(risk_engine=None, notification_service=None):
    """
    Initialize the Multi-Camera Coordinator
    Call this during Flask app startup
    """
    from backend.services.multi_camera_coordinator import MultiCameraCoordinator
    
    coordinator = MultiCameraCoordinator(
        max_cameras=MULTI_CAMERA_CONFIG['max_cameras'],
        risk_engine=risk_engine,
        notification_service=notification_service,
    )
    
    print(f"[OK] Multi-Camera Coordinator initialized for {MULTI_CAMERA_CONFIG['max_cameras']} cameras")
    return coordinator


def get_severity_from_score(score: float) -> str:
    """Convert numeric risk score to severity level"""
    thresholds = RISK_SCORING_CONFIG['severity_thresholds']
    
    if score >= thresholds.get('CRITICAL', 100):
        return 'CRITICAL'
    elif score >= thresholds.get('HIGH', 75):
        return 'HIGH'
    elif score >= thresholds.get('MEDIUM', 50):
        return 'MEDIUM'
    else:
        return 'LOW'


# ============================================================================
# ENVIRONMENT VARIABLES GUIDE
# ============================================================================
"""
Required environment variables to set:

EMAIL:
  - SMTP_HOST: Your SMTP server (default: smtp.gmail.com)
  - SMTP_PORT: SMTP port (default: 587)
  - SMTP_USERNAME: Email account username
  - SMTP_PASSWORD: Email account password or app-specific password
  - SENDER_EMAIL: Email address to send from
  - SENDER_NAME: Display name for sender

TWILIO:
  - TWILIO_ACCOUNT_SID: Your Twilio account SID
  - TWILIO_AUTH_TOKEN: Your Twilio auth token
  - TWILIO_SMS_FROM: SMS sender phone number (e.g., +1234567890)
  - TWILIO_WHATSAPP_FROM: WhatsApp sender number (e.g., whatsapp:+1234567890)
  - SMS_ENABLED: Enable SMS notifications (true/false)
  - WHATSAPP_ENABLED: Enable WhatsApp notifications (true/false)

Example .env file:
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USERNAME=your-email@gmail.com
  SMTP_PASSWORD=app-specific-password
  SENDER_EMAIL=safety-alerts@yourcompany.com
  SENDER_NAME=AI Safety Monitoring
  
  TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  TWILIO_AUTH_TOKEN=your_auth_token_here
  TWILIO_SMS_FROM=+1234567890
  TWILIO_WHATSAPP_FROM=whatsapp:+1234567890
  SMS_ENABLED=true
  WHATSAPP_ENABLED=true
"""
