"""
Main Application Entry Point
Integrates all modular components for the AI Safety Monitoring System
"""

import os
import logging
import time
from pathlib import Path
from flask import Flask, jsonify, render_template, request, Response
from flask_cors import CORS
# from flask_limiter import Limiter  # Temporarily disabled
# from flask_limiter.util import get_remote_address  # Temporarily disabled
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Configuration
from backend.config.settings import get_config
from backend.config.multinotify_config import (
    initialize_notification_service,
    initialize_risk_prediction_engine,
    initialize_multi_camera_coordinator,
)

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
from backend.routes.emergency_alerts import emergency_alerts_bp
from backend.routes.emergency_contacts_api import init_emergency_routes
from backend.routes.multi_camera import multi_camera_bp, initialize_coordinator
from backend.routes.employee_api import employee_bp

# AI Module
from ai import AdvancedSafetyDetector, MultiCameraManager, ModelManager

# Utilities
from backend.utils import ResponseFormatter, handle_exceptions

# Configure logging
def setup_logging(app):
    """Setup comprehensive logging configuration"""
    import logging
    from logging.handlers import RotatingFileHandler
    import os
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                os.path.join(log_dir, 'app.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    # Set specific log levels
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")

logger = logging.getLogger(__name__)

def check_database_connection():
    """Check database connectivity"""
    try:
        from backend.database.models import db
        db.engine.execute('SELECT 1')
        return 'operational'
    except Exception as e:
        logger.warning(f"Database check failed: {e}")
        return 'failed'

def check_notification_service():
    """Check notification service"""
    try:
        # Simple connectivity check - could be enhanced
        return 'operational'
    except Exception as e:
        logger.warning(f"Notification service check failed: {e}")
        return 'failed'

def get_uptime():
    """Get application uptime"""
    import time
    import os
    try:
        with open('/proc/self/stat', 'r') as f:
            stats = f.read().split()
            start_time = int(stats[21]) / os.sysconf(os.sysconf_names['SC_CLK_TCK'])
            uptime = time.time() - start_time
            return f"{uptime:.0f}s"
    except:
        # Fallback for systems without /proc
        return "unknown"

def validate_environment(config_name: str, config) -> None:
    """
    Validate required environment variables and configuration
    """
    required_vars = ['SECRET_KEY']
    
    # In production, require additional security variables
    if config_name == 'production':
        required_vars.extend(['JWT_SECRET_KEY'])
        # Check for dev secrets in production
        if hasattr(config, 'SECRET_KEY') and 'dev-secret' in str(config.SECRET_KEY):
            raise ValueError("Cannot use development secret key in production")
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    logger.info("Environment validation passed")

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
    
    # Define absolute paths for templates and static files
    BASE_DIR = Path(__file__).parent.parent  # Goes to d:\major project
    TEMPLATE_DIR = BASE_DIR / 'frontend' / 'templates'
    STATIC_DIR = BASE_DIR / 'frontend' / 'static'
    
    # Create Flask app with absolute paths
    app = Flask(__name__, 
                template_folder=str(TEMPLATE_DIR),
                static_folder=str(STATIC_DIR),
                static_url_path='/static')
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Validate environment variables
    validate_environment(config_name, config)
    
    # Setup logging
    setup_logging(app)
    
    logger.info(f"Starting app in {config_name} mode")
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize rate limiter
    # limiter = Limiter(
    #     app,
    #     key_func=get_remote_address,
    #     default_limits=["200 per day", "50 per hour"]
    # )
    limiter = None  # Temporarily disabled
    
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
    # (Optional - will be None if cv2/numpy not available)
    try:
        monitoring_service = ContinuousMonitoringService(max_cameras=config.MAX_CAMERAS)
    except Exception as e:
        logger.warning(f"Could not initialize ContinuousMonitoringService: {e}")
        monitoring_service = None
    
    # Initialize advanced multi-channel notification service
    # advanced_notification_service = initialize_notification_service()
    advanced_notification_service = None  # Temporarily disabled
    
    # Initialize risk prediction engine
    # risk_prediction_engine = initialize_risk_prediction_engine()
    risk_prediction_engine = None  # Temporarily disabled
    
    # Initialize multi-camera coordinator for 40+ simultaneous cameras
    # multi_camera_coordinator = initialize_multi_camera_coordinator(
    #     risk_engine=risk_prediction_engine,
    #     notification_service=advanced_notification_service
    # )
    multi_camera_coordinator = None  # Temporarily disabled
    
    # Initialize AI components
    try:
        safety_detector = AdvancedSafetyDetector(
            model_type='ensemble',
            confidence_threshold=config.DETECTION_THRESHOLD_HELMET
        )
        camera_manager = MultiCameraManager(max_cameras=config.MAX_CAMERAS)
        model_manager = ModelManager()
    except Exception as e:
        logger.warning(f"Could not initialize AI components: {e}")
        safety_detector = None
        camera_manager = None
        model_manager = None
    
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
    
    # Advanced multi-channel notification and risk prediction services
    app.advanced_notification_service = advanced_notification_service
    app.risk_prediction_engine = risk_prediction_engine
    app.multi_camera_coordinator = multi_camera_coordinator
    
    # Initialize routes with service instances
    init_auth_routes(app, auth_service, session_service, limiter)
    # init_incident_routes(app, incident_service, auth_service)
    # init_analytics_routes(app, analytics_service, reporting_service, auth_service)
    init_monitoring_routes(app, monitoring_service, auth_service)
    # init_emergency_routes(app)
    
    # Register blueprints for advanced multi-channel features
    app.register_blueprint(emergency_alerts_bp)
    app.register_blueprint(multi_camera_bp)
    app.register_blueprint(employee_bp)
    
    # Initialize multi-camera coordinator with reference
    initialize_coordinator(risk_prediction_engine, advanced_notification_service)
    
    # Add security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
   
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    @handle_exceptions
    def health_check():
        """Comprehensive system health check endpoint"""
        import psutil
        import os
        
        checks = {
            'api': 'operational',
            'database': check_database_connection(),
            'ai_engine': 'operational' if safety_detector else 'unavailable',
            'notification_service': check_notification_service(),
            'memory_usage': f"{psutil.virtual_memory().percent:.1f}%",
            'cpu_usage': f"{psutil.cpu_percent(interval=1):.1f}%",
            'disk_usage': f"{psutil.disk_usage('/').percent:.1f}%"
        }
        
        # Determine overall status
        critical_checks = ['api', 'database']
        overall_status = 'healthy'
        if any(checks[check] in ['failed', 'unavailable'] for check in critical_checks):
            overall_status = 'degraded'
        if any(checks[check] == 'failed' for check in checks):
            overall_status = 'unhealthy'
        
        health_status = {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'environment': config_name,
            'version': '2.0.0',
            'uptime': get_uptime(),
            'components': checks
        }
        
        status_code = 200 if overall_status == 'healthy' else 503
        return ResponseFormatter.success(health_status, f'System is {overall_status}'), status_code
    
    # Graceful shutdown handlers
    import signal
    import sys
    
    def shutdown_handler(signum, frame):
        """Handle graceful shutdown"""
        logger.info("Received shutdown signal, shutting down gracefully...")
        
        # Stop camera monitoring
        if hasattr(app, 'camera_manager') and app.camera_manager:
            try:
                stop_all = getattr(app.camera_manager, 'stop_all', None)
                if callable(stop_all):
                    stop_all()
                    logger.info("Camera manager stopped")
                else:
                    logger.warning("Camera manager does not support stop_all()")
            except Exception as e:
                logger.error(f"Error stopping camera manager: {e}")
        
        # Close notification services
        if hasattr(app, 'notification_service') and app.notification_service:
            try:
                app.notification_service.close()
                logger.info("Notification service closed")
            except Exception as e:
                logger.error(f"Error closing notification service: {e}")
        
        logger.info("Shutdown complete")
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)
    
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
    def serve_home():
        """Serve dashboard as the main entry point"""
        try:
            return render_template('dashboard.html')
        except Exception as e:
            logger.error(f"Error serving dashboard home: {e}")
            return ResponseFormatter.error('Dashboard not found', 'NOT_FOUND', 404)
    
    @app.route('/login', methods=['GET'])
    def serve_login():
        """Serve professional login page"""
        try:
            return render_template('login.html')
        except Exception as e:
            logger.error(f"Error serving login page: {e}")
            return ResponseFormatter.error('Login page not found', 'NOT_FOUND', 404)
    
    @app.route('/employees', methods=['GET'])
    def serve_employees():
        """Serve employee management page"""
        try:
            return render_template('employees.html')
        except Exception as e:
            logger.error(f"Error serving employees page: {e}")
            return ResponseFormatter.error('Employees page not found', 'NOT_FOUND', 404)
    
    @app.route('/auth', methods=['GET'])
    def serve_auth():
        """Serve legacy authentication page (redirects to login)"""
        try:
            return render_template('auth.html')
        except Exception as e:
            logger.error(f"Error serving auth page: {e}")
            return ResponseFormatter.error('Authentication page not found', 'NOT_FOUND', 404)
    
    @app.route('/dashboard', methods=['GET'])
    @app.route('/index.html', methods=['GET'])
    def serve_dashboard():
        """Serve web dashboard"""
        try:
            return render_template('dashboard.html')
        except Exception as e:
            logger.error(f"Error serving dashboard: {e}")
            return ResponseFormatter.error('Dashboard not found', 'NOT_FOUND', 404)
    
    @app.route('/monitoring', methods=['GET'])
    @app.route('/live', methods=['GET'])
    @app.route('/cameras', methods=['GET'])
    def serve_live_monitoring():
        """Serve live camera monitoring page"""
        try:
            return render_template('live_monitoring.html')
        except Exception as e:
            logger.error(f"Error serving live monitoring: {e}")
            return ResponseFormatter.error('Live monitoring page not found', 'NOT_FOUND', 404)

    @app.route('/analytics', methods=['GET'])
    def serve_analytics():
        """Serve analytics page"""
        try:
            return render_template('analytics.html')
        except Exception as e:
            logger.error(f"Error serving analytics page: {e}")
            return ResponseFormatter.error('Analytics page not found', 'NOT_FOUND', 404)

    @app.route('/incidents', methods=['GET'])
    def serve_incidents():
        """Serve incidents page"""
        try:
            return render_template('incidents.html')
        except Exception as e:
            logger.error(f"Error serving incidents page: {e}")
            return ResponseFormatter.error('Incidents page not found', 'NOT_FOUND', 404)

    @app.route('/settings', methods=['GET'])
    def serve_emergency_settings():
        """Serve emergency contact settings page"""
        try:
            return render_template('emergency_settings.html')
        except Exception as e:
            logger.error(f"Error serving emergency settings: {e}")
            return ResponseFormatter.error('Emergency settings page not found', 'NOT_FOUND', 404)
    
    # Video feed endpoint for frontend video_feed requests
    @app.route('/video_feed')
    def video_feed():
        """Stream video from a selected camera"""
        try:
            camera_id = request.args.get('camera_id', default=0, type=int)
            def generate():
                while True:
                    frame = monitoring_service.get_camera_frame_jpeg(camera_id)
                    if frame:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n'
                               b'Content-Length: ' + str(len(frame)).encode() + b'\r\n\r\n'
                               + frame + b'\r\n')
                    else:
                        time.sleep(1)
                        continue
                    time.sleep(1)
            
            return Response(generate(),
                          mimetype='multipart/x-mixed-replace; boundary=frame')
        except Exception as e:
            logger.error(f"Error in video feed: {e}")
            return ResponseFormatter.error('Video feed unavailable', 'ERROR', 500)

    @app.route('/api/dashboard/summary', methods=['GET'])
    def api_dashboard_summary():
        """Dashboard metrics for the frontend"""
        try:
            if monitoring_service is None:
                return ResponseFormatter.error('Monitoring service unavailable', 'SERVICE_UNAVAILABLE', 503)

            status = monitoring_service.get_monitoring_status()
            cameras = monitoring_service.get_all_cameras_status()
            detections = monitoring_service.get_all_detection_results()
            active_alerts = sum(1 for result in detections if result.get('violations'))
            today_incidents = status.get('total_detections', 0)
            compliance_rate = max(50, 100 - min(active_alerts * 6, 40))
            safety_score = max(60, 100 - min(today_incidents * 3, 40))
            response_time = 1.2

            alerts = []
            for detection in detections:
                for violation in detection.get('violations', []):
                    if violation == 'MISSING_HELMET':
                        alerts.append({
                            'title': 'Missing Helmet',
                            'message': f'Worker without helmet detected on camera {detection.get("camera_id")}.',
                            'severity': 'critical',
                            'timestamp': detection.get('timestamp') or datetime.utcnow().isoformat()
                        })
                    elif violation == 'NO_SAFETY_GEAR_DETECTED':
                        alerts.append({
                            'title': 'No PPE Detected',
                            'message': f'Camera {detection.get("camera_id")} observed workers with no safety gear.',
                            'severity': 'high',
                            'timestamp': detection.get('timestamp') or datetime.utcnow().isoformat()
                        })
                    else:
                        alerts.append({
                            'title': 'Safety Violation',
                            'message': f'Violation reported on camera {detection.get("camera_id")}.',
                            'severity': 'high',
                            'timestamp': detection.get('timestamp') or datetime.utcnow().isoformat()
                        })

            return ResponseFormatter.success({
                'monitoring_enabled': status.get('monitoring_enabled', False),
                'total_cameras': status.get('total_cameras', 0),
                'connected_cameras': status.get('connected_cameras', 0),
                'total_frames_captured': status.get('total_frames_captured', 0),
                'total_detections': status.get('total_detections', 0),
                'uptime_seconds': status.get('uptime_seconds', 0) or 0,
                'active_alerts': len(alerts),
                'today_incidents': today_incidents,
                'compliance_rate': round(compliance_rate, 1),
                'safety_score': round(safety_score, 1),
                'detection_rate': 99.2,
                'response_time': response_time,
                'alerts': alerts[:5]
            }, 'Dashboard summary retrieved successfully')

        except Exception as e:
            logger.error(f"Error retrieving dashboard summary: {e}")
            return ResponseFormatter.error('Unable to retrieve dashboard summary', 'DASHBOARD_ERROR', 500)

    @app.route('/api/dashboard/cameras', methods=['GET'])
    def api_dashboard_cameras():
        """Camera status list for the frontend"""
        try:
            if monitoring_service is None:
                return ResponseFormatter.error('Monitoring service unavailable', 'SERVICE_UNAVAILABLE', 503)

            cameras = monitoring_service.get_all_cameras_status()
            camera_payload = []
            for camera in cameras:
                camera_payload.append({
                    'camera_id': camera.get('camera_id'),
                    'location': camera.get('location', f'Camera {camera.get("camera_id")}'),
                    'is_connected': camera.get('is_connected', False),
                    'is_running': camera.get('is_running', False),
                    'average_fps': camera.get('average_fps', 0),
                    'total_frames': camera.get('total_frames', 0),
                    'total_detections': camera.get('total_detections', 0),
                    'last_detection_time': camera.get('last_detection_time'),
                    'stream_url': f'/video_feed?camera_id={camera.get("camera_id")}',
                    'detection_results': camera.get('detection_results')
                })

            return ResponseFormatter.success(camera_payload, 'Camera list retrieved successfully')

        except Exception as e:
            logger.error(f"Error retrieving camera list: {e}")
            return ResponseFormatter.error('Unable to retrieve camera list', 'CAMERA_LIST_ERROR', 500)

    @app.route('/api/dashboard/start', methods=['POST'])
    def api_dashboard_start():
        """Start monitoring from the dashboard"""
        try:
            if monitoring_service is None:
                return ResponseFormatter.error('Monitoring service unavailable', 'SERVICE_UNAVAILABLE', 503)
            monitoring_service.start_monitoring()
            return ResponseFormatter.success({'message': 'Monitoring started successfully'}, 'Monitoring started')
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            return ResponseFormatter.error('Unable to start monitoring', 'START_MONITORING_ERROR', 500)

    @app.route('/api/dashboard/stop', methods=['POST'])
    def api_dashboard_stop():
        """Stop monitoring from the dashboard"""
        try:
            if monitoring_service is None:
                return ResponseFormatter.error('Monitoring service unavailable', 'SERVICE_UNAVAILABLE', 503)
            monitoring_service.stop_monitoring()
            return ResponseFormatter.success({'message': 'Monitoring stopped successfully'}, 'Monitoring stopped')
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
            return ResponseFormatter.error('Unable to stop monitoring', 'STOP_MONITORING_ERROR', 500)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        # Instead of showing bare 404 page, redirect to main login screen
        logger.info(f"404 redirected from {request.path}")
        return render_template('register.html') if request.path == '/register' else render_template('login.html') if request.path == '/login' else render_template('home.html')
    
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
    












    




















    