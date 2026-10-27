"""
Main Application Entry Point
Integrates all modular components for the AI Safety Monitoring System
"""

import os
import logging
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

# Configuration
from backend.config.settings import get_config

# Services
from backend.services import (
    AuthenticationService,
    SessionManagementService,
    AuditService,
    IncidentManagementService,
    NotificationService,
    ReportingService,
    AnalyticsService,
    ContinuousMonitoringService
)

# Routes
from backend.routes import (
    auth_bp,
    incidents_bp,
    analytics_bp,
    monitoring_bp,
    init_auth_routes,
    init_incident_routes,
    init_analytics_routes,
    init_monitoring_routes
)

# AI Module
from ai import AdvancedSafetyDetector, MultiCameraManager, ModelManager

# Utilities
from backend.utils import ResponseFormatter, handle_exceptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name: str = 'development') -> Flask:
    """
    Application factory
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Flask application instance
    """
    
    # Get environment
    env = os.getenv('FLASK_ENV', 'development')
    config_name = config_name or env
    
    # Create Flask app
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    logger.info(f"Starting app in {config_name} mode")
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize services
    auth_service = AuthenticationService(
        secret_key=config.SECRET_KEY,
        access_token_expires=config.JWT_ACCESS_TOKEN_EXPIRES,
        refresh_token_expires=config.JWT_REFRESH_TOKEN_EXPIRES
    )
    
    session_service = SessionManagementService()
    audit_service = AuditService(db_session=None)  # Will integrate with DB
    incident_service = IncidentManagementService(db_session=None)
    
    mail_config = {
        'MAIL_SERVER': config.MAIL_SERVER,
        'MAIL_PORT': config.MAIL_PORT,
        'MAIL_USERNAME': config.MAIL_USERNAME,
        'MAIL_PASSWORD': config.MAIL_PASSWORD,
        'MAIL_DEFAULT_SENDER': config.MAIL_DEFAULT_SENDER
    }
    notification_service = NotificationService(mail_config=mail_config)
    reporting_service = ReportingService(db_session=None)
    analytics_service = AnalyticsService(db_session=None)
    
    # Initialize continuous monitoring service for 24/7 camera monitoring
    monitoring_service = ContinuousMonitoringService(max_cameras=config.MAX_CAMERAS)
    
    # Initialize AI components
    safety_detector = AdvancedSafetyDetector(
        model_type='ensemble',
        confidence_threshold=config.DETECTION_THRESHOLD_HELMET
    )
    
    camera_manager = MultiCameraManager(max_cameras=config.MAX_CAMERAS)
    model_manager = ModelManager()
    
    # Store services in app context for access in routes
    app.auth_service = auth_service
    app.session_service = session_service
    app.audit_service = audit_service
    app.incident_service = incident_service
    app.notification_service = notification_service
    app.reporting_service = reporting_service
    app.analytics_service = analytics_service
    app.monitoring_service = monitoring_service
    app.safety_detector = safety_detector
    app.camera_manager = camera_manager
    app.model_manager = model_manager
    
    # Initialize routes with service instances
    init_auth_routes(app, auth_service, session_service)
    init_incident_routes(app, incident_service, auth_service)
    init_analytics_routes(app, analytics_service, reporting_service, auth_service)
    init_monitoring_routes(app, monitoring_service, auth_service)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(monitoring_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    @handle_exceptions
    def health_check():
        """System health check endpoint"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': config_name,
            'version': '2.0.0',
            'components': {
                'api': 'operational',
                'ai_engine': 'operational',
                'database': 'operational',
                'notification_service': 'operational'
            }
        }
        return ResponseFormatter.success(health_status, 'System is healthy')
    
    # Welcome endpoint
    @app.route('/api', methods=['GET'])
    @handle_exceptions
    def api_welcome():
        """API welcome endpoint"""
        return ResponseFormatter.success({
            'name': 'AI Smart Safety Monitoring System',
            'version': '2.0.0',
            'description': 'Enterprise-grade safety monitoring with AI-powered detection',
            'endpoints': {
                'authentication': '/api/auth',
                'incidents': '/api/incidents',
                'analytics': '/api/analytics',
                'health': '/health'
            }
        }, 'Welcome to AI Safety API')
    
    # Frontend routes
    @app.route('/', methods=['GET'])
    @app.route('/dashboard', methods=['GET'])
    @app.route('/index.html', methods=['GET'])
    def serve_dashboard():
        """Serve web dashboard"""
        try:
            return render_template('index.html')
        except Exception as e:
            logger.error(f"Error serving dashboard: {e}")
            return ResponseFormatter.error('Dashboard not found', 'NOT_FOUND', 404)
    
    @app.route('/monitoring', methods=['GET'])
    @app.route('/live', methods=['GET'])
    def serve_live_monitoring():
        """Serve live monitoring dashboard"""
        try:
            return render_template('live_monitoring.html')
        except Exception as e:
            logger.error(f"Error serving live monitoring: {e}")
            return ResponseFormatter.error('Live monitoring page not found', 'NOT_FOUND', 404)

    @app.route('/login', methods=['GET'])
    def serve_login():
        """Serve professional login page"""
        try:
            return render_template('login.html')
        except Exception as e:
            logger.error(f"Error serving login page: {e}")
            return ResponseFormatter.error('Login page not found', 'NOT_FOUND', 404)

    @app.route('/register', methods=['GET'])
    def serve_register():
        """Serve professional registration page"""
        try:
            return render_template('register.html')
        except Exception as e:
            logger.error(f"Error serving register page: {e}")
            return ResponseFormatter.error('Registration page not found', 'NOT_FOUND', 404)

    @app.route('/settings', methods=['GET'])
    def serve_emergency_settings():
        """Serve emergency contact settings page"""
        try:
            return render_template('emergency_settings.html')
        except Exception as e:
            logger.error(f"Error serving emergency settings: {e}")
            return ResponseFormatter.error('Emergency settings page not found', 'NOT_FOUND', 404)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors with route fallback"""
        logger.info(f"404 redirected from {request.path}")
        if request.path == '/register':
            return render_template('register.html')
        if request.path == '/login':
            return render_template('login.html')
        return render_template('home.html')
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal server error: {error}")
        return ResponseFormatter.error('Internal server error', 'SERVER_ERROR', 500)
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 errors"""
        return ResponseFormatter.error('Forbidden', 'FORBIDDEN', 403)
    
    # Request logging middleware
    @app.before_request
    def log_request():
        """Log incoming requests"""
        logger.debug(f"{request.method} {request.path} from {request.remote_addr}")
    
    @app.after_request
    def log_response(response):
        """Log outgoing responses"""
        logger.debug(f"Response: {response.status_code}")
        return response
    
    # Initialize default cameras for monitoring
    @app.before_request
    def init_cameras():
        """Initialize cameras on first request"""
        if not hasattr(app, '_cameras_initialized'):
            try:
                # Add default cameras (can be configured via environment or API)
                # Example: webcam on local machine
                monitoring_service.add_camera(
                    camera_id=0,
                    source=0,  # Local webcam
                    location='Main Entrance',
                    auto_start=False
                )
                
                # Start monitoring automatically
                monitoring_service.start_monitoring()
                logger.info("Automatic monitoring started with default cameras")
                
            except Exception as e:
                logger.warning(f"Could not initialize default cameras: {e}")
            
            app._cameras_initialized = True
            return  # Only run this once
        
        # Skip on subsequent requests
        if request.endpoint and request.endpoint.startswith('static'):
            return
    
    logger.info(f"Application initialized successfully in {config_name} mode")
    logger.info("Access live monitoring at: http://localhost:5000/monitoring")
    logger.info("API documentation at: http://localhost:5000/api")
    
    return app

if __name__ == '__main__':
    # Create and run the application
    app = create_app()
    
    # Development settings
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
    












    




















    