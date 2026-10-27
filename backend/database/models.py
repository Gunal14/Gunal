"""
Advanced Database Models
Production-ready with comprehensive tracking
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid

db = SQLAlchemy()

class BaseModel(db.Model):
    """Base model with common fields"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class User(BaseModel):
    """User model with role-based access"""
    __tablename__ = 'users'
    
    username = db.Column(db.String(120), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    role = db.Column(db.String(50), default='operator')  # admin, supervisor, operator
    department = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    # Emergency Contact Information
    mobile_number = db.Column(db.String(20), nullable=False)  # Primary phone number (e.g., +1-234-567-8900)
    country_code = db.Column(db.String(5), default='+1')  # Country code for validation
    phone_verified = db.Column(db.Boolean, default=False)
    
    # Relations
    incidents = db.relationship('IncidentLog', backref='reporter', lazy=True)
    alerts = db.relationship('AlertHistory', backref='responder', lazy=True)
    emergency_contacts = db.relationship('EmergencyContact', backref='user', lazy=True, foreign_keys='EmergencyContact.user_id')
    
    def __repr__(self):
        return f'<User {self.username}>'

class IncidentLog(BaseModel):
    """Comprehensive incident logging"""
    __tablename__ = 'incident_logs'
    
    incident_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    incident_type = db.Column(db.String(100), nullable=False, index=True)
    severity = db.Column(db.String(20), default='MEDIUM')  # LOW, MEDIUM, HIGH, CRITICAL
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    camera_id = db.Column(db.Integer)
    location = db.Column(db.String(255))
    worker_id = db.Column(db.String(100))
    details = db.Column(db.JSON)
    description = db.Column(db.Text)
    
    # Status tracking
    status = db.Column(db.String(50), default='open')  # open, acknowledged, resolved, false_positive
    resolved_at = db.Column(db.DateTime)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolution_notes = db.Column(db.Text)
    
    # Evidence
    image_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))
    
    # Analytics
    response_time = db.Column(db.Integer)  # seconds
    impact_level = db.Column(db.String(50))
    
    resolved_by = db.relationship('User', backref='resolved_incidents', foreign_keys=[resolved_by_id])
    
    def __repr__(self):
        return f'<IncidentLog {self.incident_id}>'

class AlertHistory(BaseModel):
    """Alert tracking and management"""
    __tablename__ = 'alert_history'
    
    alert_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    alert_type = db.Column(db.String(100), nullable=False, index=True)
    severity = db.Column(db.String(20), default='MEDIUM')
    message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Response tracking
    acknowledged_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    acknowledged_at = db.Column(db.DateTime)
    acknowledgment_notes = db.Column(db.Text)
    
    # Notifications
    email_sent = db.Column(db.Boolean, default=False)
    sms_sent = db.Column(db.Boolean, default=False)
    
    acknowledged_by = db.relationship('User', backref='acknowledged_alerts', foreign_keys=[acknowledged_by_id])
    
    def __repr__(self):
        return f'<AlertHistory {self.alert_id}>'

class WorkerProfile(BaseModel):
    """Worker management"""
    __tablename__ = 'worker_profiles'
    
    worker_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    department = db.Column(db.String(120), index=True)
    shift = db.Column(db.String(50))
    role = db.Column(db.String(120))
    equipment_required = db.Column(db.JSON)  # ['helmet', 'vest', 'gloves']
    badge_number = db.Column(db.String(50))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    
    # Statistics
    total_incidents = db.Column(db.Integer, default=0)
    safety_violations = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<WorkerProfile {self.worker_id}>'

class CameraConfiguration(BaseModel):
    """Camera management and configuration"""
    __tablename__ = 'camera_configs'
    
    camera_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(255))
    camera_url = db.Column(db.String(500))
    resolution = db.Column(db.String(20), default='640x480')
    fps = db.Column(db.Integer, default=30)
    status = db.Column(db.String(50), default='active')  # active, inactive, offline
    
    # Monitoring
    is_monitoring = db.Column(db.Boolean, default=False)
    last_frame_time = db.Column(db.DateTime)
    
    # Config
    detection_enabled = db.Column(db.Boolean, default=True)
    alerts_enabled = db.Column(db.Boolean, default=True)
    recording_enabled = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<CameraConfiguration {self.camera_id}>'

class ShiftManagement(BaseModel):
    """Track worker shifts and operations"""
    __tablename__ = 'shift_management'
    
    shift_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    shift_name = db.Column(db.String(120))
    shift_type = db.Column(db.String(50))  # morning, afternoon, night
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    
    # Workers in shift
    workers_assigned = db.Column(db.JSON)  # list of worker_ids
    area_monitors = db.Column(db.JSON)  # list of camera_ids
    
    # Statistics
    total_workers = db.Column(db.Integer)
    incidents_count = db.Column(db.Integer, default=0)
    violations_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<ShiftManagement {self.shift_id}>'

class SystemConfig(BaseModel):
    """System configuration storage"""
    __tablename__ = 'system_configs'
    
    config_key = db.Column(db.String(120), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text)
    data_type = db.Column(db.String(50))  # string, integer, boolean, json
    description = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<SystemConfig {self.config_key}>'

class AuditLog(BaseModel):
    """Audit trail for compliance"""
    __tablename__ = 'audit_logs'
    
    action = db.Column(db.String(255), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    table_name = db.Column(db.String(100))
    record_id = db.Column(db.String(100))
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action}>'

class NotificationPreference(BaseModel):
    """User notification preferences"""
    __tablename__ = 'notification_preferences'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    alert_type = db.Column(db.String(100), nullable=False)
    email_enabled = db.Column(db.Boolean, default=True)
    sms_enabled = db.Column(db.Boolean, default=False)
    push_enabled = db.Column(db.Boolean, default=True)
    min_severity = db.Column(db.String(20), default='MEDIUM')
    
    user = db.relationship('User', backref='notification_preferences')
    
    def __repr__(self):
        return f'<NotificationPreference {self.user_id}> - {self.alert_type}>'

class ReportTemplate(BaseModel):
    """Report templates for various needs"""
    __tablename__ = 'report_templates'
    
    template_name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    report_type = db.Column(db.String(50))  # daily,weekly, monthly, custom
    fields = db.Column(db.JSON)
    filters = db.Column(db.JSON)
    charts = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<ReportTemplate {self.template_name}>'


# ============================================================================
# NEW MODELS FOR ENHANCED MULTI-CAMERA & NOTIFICATION SYSTEM (v2.0)
# ============================================================================

class EmergencyContact(BaseModel):
    """Emergency contact numbers for alert notifications (Max 10 per user)"""
    __tablename__ = 'emergency_contacts'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    contact_name = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    country_code = db.Column(db.String(5), default='+1')
    email = db.Column(db.String(255))
    
    # Notification channels
    whatsapp_enabled = db.Column(db.Boolean, default=True)
    sms_enabled = db.Column(db.Boolean, default=True)
    email_enabled = db.Column(db.Boolean, default=True)
    
    # Alert severity levels this contact should receive
    alert_low = db.Column(db.Boolean, default=False)
    alert_medium = db.Column(db.Boolean, default=True)
    alert_high = db.Column(db.Boolean, default=True)
    alert_critical = db.Column(db.Boolean, default=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))  # OTP for verification
    verified_at = db.Column(db.DateTime)
    
    # Relationship
    user = db.relationship('User', backref='emergency_contacts_list', foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<EmergencyContact {self.contact_name}>'


class Employee(BaseModel):
    """Employee database with facial recognition and safety compliance data"""
    __tablename__ = 'employees'
    
    employee_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(120), index=True)
    position = db.Column(db.String(120))
    shift = db.Column(db.String(50))
    
    # Facial recognition data
    face_encoding = db.Column(db.JSON)  # Face encoding vector for recognition
    face_image_path = db.Column(db.String(500))  # Path to reference face image
    
    # Safety equipment requirements
    requires_helmet = db.Column(db.Boolean, default=True)
    requires_vest = db.Column(db.Boolean, default=True)
    requires_gloves = db.Column(db.Boolean, default=False)
    requires_boots = db.Column(db.Boolean, default=False)
    
    # Training data for helmet detection
    helmet_training_images = db.Column(db.JSON)  # List of image paths with helmet
    no_helmet_training_images = db.Column(db.JSON)  # List of image paths without helmet
    
    # Status and compliance
    is_active = db.Column(db.Boolean, default=True)
    compliance_score = db.Column(db.Float, default=0.0)  # Overall compliance percentage
    last_seen = db.Column(db.DateTime)
    total_violations = db.Column(db.Integer, default=0)
    
    # Emergency contacts (separate from user emergency contacts)
    emergency_contact_name = db.Column(db.String(200))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_email = db.Column(db.String(255))
    
    # Relations
    incidents = db.relationship('IncidentLog', backref='employee', lazy=True, foreign_keys='IncidentLog.worker_id')
    
    def __repr__(self):
        return f'<Employee {self.employee_id}: {self.name}>'


class EmployeeRecognition(BaseModel):
    """Employee recognition events and compliance tracking"""
    __tablename__ = 'employee_recognitions'
    
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False, index=True)
    camera_id = db.Column(db.Integer)
    location = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Recognition data
    confidence_score = db.Column(db.Float)  # Face recognition confidence
    face_location = db.Column(db.JSON)  # Bounding box coordinates
    
    # Safety compliance at time of recognition
    helmet_detected = db.Column(db.Boolean)
    vest_detected = db.Column(db.Boolean, default=False)
    gloves_detected = db.Column(db.Boolean, default=False)
    boots_detected = db.Column(db.Boolean, default=False)
    
    # Compliance status
    compliance_status = db.Column(db.String(50))  # 'compliant', 'non_compliant', 'partial'
    violations = db.Column(db.JSON)  # List of specific violations
    
    # Image reference
    snapshot_path = db.Column(db.String(500))
    
    # Relations
    employee = db.relationship('Employee', backref='recognitions')
    
    def __repr__(self):
        return f'<EmployeeRecognition {self.employee_id} at {self.timestamp}>'


class SafetyAlert(BaseModel):
    """Safety alerts sent to employees and emergency contacts"""
    __tablename__ = 'safety_alerts'
    
    alert_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), index=True)
    incident_id = db.Column(db.String(36), db.ForeignKey('incident_logs.incident_id'), index=True)
    
    # Alert details
    alert_type = db.Column(db.String(100), nullable=False)  # 'helmet_violation', 'equipment_missing', etc.
    severity = db.Column(db.String(20), default='MEDIUM')
    message = db.Column(db.String(500))
    location = db.Column(db.String(255))
    
    # Recipients
    sent_to_employee = db.Column(db.Boolean, default=False)
    sent_to_emergency_contacts = db.Column(db.Boolean, default=False)
    
    # Notification status
    email_sent = db.Column(db.Boolean, default=False)
    sms_sent = db.Column(db.Boolean, default=False)
    whatsapp_sent = db.Column(db.Boolean, default=False)
    
    # Timestamps
    sent_at = db.Column(db.DateTime)
    acknowledged_at = db.Column(db.DateTime)
    
    # Relations
    employee = db.relationship('Employee', backref='alerts')
    incident = db.relationship('IncidentLog', backref='alerts')
    
    def __repr__(self):
        return f'<SafetyAlert {self.alert_type} for {self.employee_id}>'


class CameraHealthStatus(BaseModel):
    """Real-time health monitoring for 30-40+ cameras"""
    __tablename__ = 'camera_health_status'
    
    camera_id = db.Column(db.Integer, db.ForeignKey('camera_configs.id'), nullable=False, unique=True, index=True)
    
    # Connection status
    is_connected = db.Column(db.Boolean, default=False)
    last_frame_time = db.Column(db.DateTime)
    connection_attempts = db.Column(db.Integer, default=0)
    last_connection_error = db.Column(db.String(500))
    
    # Performance metrics
    current_fps = db.Column(db.Float, default=0)
    frame_loss_rate = db.Column(db.Float, default=0)  # 0-100%
    cpu_usage = db.Column(db.Float, default=0)
    memory_usage = db.Column(db.Float, default=0)
    bandwidth_usage = db.Column(db.Float, default=0)
    
    # Detection status
    detection_running = db.Column(db.Boolean, default=False)
    last_detection_time = db.Column(db.DateTime)
    detections_per_minute = db.Column(db.Float, default=0)
    
    # Uptime tracking
    uptime_percentage = db.Column(db.Float, default=100)
    uptime_seconds = db.Column(db.Integer, default=0)
    downtime_events = db.Column(db.Integer, default=0)
    
    # Network health
    latency_ms = db.Column(db.Float, default=0)
    packet_loss = db.Column(db.Float, default=0)
    signal_strength = db.Column(db.Float, default=0)  # For wireless cameras
    
    # Last updated
    last_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    camera = db.relationship('CameraConfiguration', backref='health_status')
    
    def __repr__(self):
        return f'<CameraHealthStatus Camera-{self.camera_id}>'


class RiskAlert(BaseModel):
    """Enhanced risk alerts with context and severity scoring"""
    __tablename__ = 'risk_alerts'
    
    alert_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('camera_configs.id'), nullable=False, index=True)
    
    # Risk classification
    risk_type = db.Column(db.String(100), nullable=False, index=True)  # not_wearing_helmet, improper_stance, unsafe_behavior
    risk_category = db.Column(db.String(50), nullable=False)  # PPE, POSTURE, BEHAVIOR, HAZMAT
    
    # Severity & confidence
    severity = db.Column(db.String(20), nullable=False, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    confidence_score = db.Column(db.Float)  # 0-1 detection confidence
    risk_score = db.Column(db.Float)  # 0-100 contextualized risk
    
    # Detection details
    worker_id = db.Column(db.String(100))
    detection_count = db.Column(db.Integer, default=1)  # How many times detected in time window
    first_detection_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_detection_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Context
    environmental_conditions = db.Column(db.JSON)  # lighting, weather, etc.
    area_hazard_level = db.Column(db.String(20))  # LOW, MEDIUM, HIGH
    nearby_hazards = db.Column(db.JSON)  # List of identified hazards
    
    # Image evidence
    image_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    
    # Alert lifecycle
    status = db.Column(db.String(50), default='pending', index=True)  # pending, notified, acknowledged, resolved, dismissed
    notified = db.Column(db.Boolean, default=False)
    notified_at = db.Column(db.DateTime)
    
    # Response tracking
    acknowledged_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    acknowledged_at = db.Column(db.DateTime)
    resolution_action = db.Column(db.String(200))
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    camera = db.relationship('CameraConfiguration', backref='risk_alerts')
    acknowledged_by = db.relationship('User', backref='acknowledged_risk_alerts', foreign_keys=[acknowledged_by_id])
    
    def __repr__(self):
        return f'<RiskAlert {self.alert_id}>'


class NotificationLog(BaseModel):
    """Track all notifications sent (email, SMS, WhatsApp)"""
    __tablename__ = 'notification_logs'
    
    notification_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    alert_id = db.Column(db.String(36), db.ForeignKey('risk_alerts.alert_id'))
    
    # Notification details
    notification_type = db.Column(db.String(50), nullable=False, index=True)  # EMAIL, SMS, WHATSAPP
    recipient = db.Column(db.String(255), nullable=False)  # Email or phone number
    subject = db.Column(db.String(500))
    message = db.Column(db.Text)
    
    # Contact info
    contact_id = db.Column(db.Integer, db.ForeignKey('emergency_contacts.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status
    status = db.Column(db.String(50), default='pending', index=True)  # pending, sent, failed, bounced
    attempts = db.Column(db.Integer, default=0)
    last_attempt = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Delivery tracking
    delivered = db.Column(db.Boolean, default=False)
    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    sent_at = db.Column(db.DateTime)
    
    # Relationships
    contact = db.relationship('EmergencyContact', backref='notifications')
    admin = db.relationship('User', backref='sent_notifications')
    
    def __repr__(self):
        return f'<NotificationLog {self.notification_id}>'


class RiskPredictionModel(BaseModel):
    """Store risk prediction model versions and accuracy metrics"""
    __tablename__ = 'risk_prediction_models'
    
    model_name = db.Column(db.String(200), nullable=False, index=True)
    model_version = db.Column(db.String(50), nullable=False)
    
    # Model info
    model_type = db.Column(db.String(100))  # YOLO, Faster R-CNN, etc.
    risk_types = db.Column(db.JSON)  # Categories detected: ['helmet', 'ppe', 'posture']
    
    # Performance metrics
    accuracy = db.Column(db.Float)  # 0-100 percent
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    
    # Dataset info
    training_dataset_size = db.Column(db.Integer)
    training_date = db.Column(db.DateTime)
    test_accuracy = db.Column(db.Float)
    
    # Deployment
    is_active = db.Column(db.Boolean, default=False, index=True)
    is_fallback = db.Column(db.Boolean, default=False)  # Fallback model if primary fails
    deployed_at = db.Column(db.DateTime)
    
    # Optimization
    inference_time_ms = db.Column(db.Float)  # Average inference time
    memory_required_mb = db.Column(db.Float)
    
    # Location
    model_path = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<RiskPredictionModel {self.model_name}-{self.model_version}>'


class MultiCameraSession(BaseModel):
    """Track multi-camera monitoring sessions"""
    __tablename__ = 'multi_camera_sessions'
    
    session_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    started_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Session scope
    camera_ids = db.Column(db.JSON)  # Which cameras being monitored
    total_cameras = db.Column(db.Integer)
    
    # Live statistics
    active_alerts = db.Column(db.Integer, default=0)
    total_detections = db.Column(db.Integer, default=0)
    high_risk_events = db.Column(db.Integer, default=0)
    
    # Performance
    avg_response_time_ms = db.Column(db.Float, default=0)
    system_health_score = db.Column(db.Float)  # 0-100
    
    # Session lifecycle
    start_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    end_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Relationships
    started_by = db.relationship('User', backref='monitoring_sessions')
    
    def __repr__(self):
        return f'<MultiCameraSession {self.session_id}>'
