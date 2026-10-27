"""
AI Smart Safety Monitoring System - Flask Application
Main application entry point with video streaming and detection
"""

from flask import Flask, render_template, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import cv2
import threading
import numpy as np
from safety_detection import SafetyDetector
from models import db, IncidentLog, AlertHistory
import json

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safety_monitoring.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize database
db.init_app(app)

# Global variables
detector = SafetyDetector()
current_frame = None
frame_lock = threading.Lock()
camera = None
monitoring_active = False
alert_threshold = 5  # seconds without safety gear

def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()

def generate_frames():
    """Generate video frames with detection"""
    global current_frame, detector, camera
    
    if camera is None:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while monitoring_active:
        ret, frame = camera.read()
        if not ret:
            break
        
        # Run detection
        results = detector.detect(frame)
        
        # Annotate frame
        annotated_frame = detector.annotate_frame(frame, results)
        
        # Store current frame
        with frame_lock:
            current_frame = annotated_frame.copy()
        
        # Check safety alerts
        check_safety_alerts(results)
        
        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def check_safety_alerts(results):
    """Check detection results and generate alerts"""
    violations = results.get('violations', [])
    
    if violations:
        # Log incident
        incident = IncidentLog(
            incident_type=', '.join(violations),
            severity='HIGH' if len(violations) > 1 else 'MEDIUM',
            timestamp=datetime.utcnow(),
            details=json.dumps(results)
        )
        db.session.add(incident)
        
        # Create alert
        alert = AlertHistory(
            alert_type=violations[0],
            message=f"Safety violation detected: {', '.join(violations)}",
            timestamp=datetime.utcnow(),
            is_active=True
        )
        db.session.add(alert)
        
        try:
            db.session.commit()
        except:
            db.session.rollback()

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming endpoint"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/start_monitoring', methods=['POST'])
def start_monitoring():
    """Start safety monitoring"""
    global monitoring_active
    monitoring_active = True
    return jsonify({'status': 'success', 'message': 'Monitoring started'})

@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """Stop safety monitoring"""
    global monitoring_active, camera
    monitoring_active = False
    if camera:
        camera.release()
        camera = None
    return jsonify({'status': 'success', 'message': 'Monitoring stopped'})

@app.route('/api/incidents')
def get_incidents():
    """Get incident history"""
    limit = request.args.get('limit', 50, type=int)
    incidents = IncidentLog.query.order_by(IncidentLog.timestamp.desc()).limit(limit).all()
    
    return jsonify({
        'incidents': [
            {
                'id': i.id,
                'type': i.incident_type,
                'severity': i.severity,
                'timestamp': i.timestamp.isoformat(),
                'details': json.loads(i.details) if i.details else {}
            }
            for i in incidents
        ]
    })

@app.route('/api/alerts')
def get_alerts():
    """Get active alerts"""
    alerts = AlertHistory.query.filter_by(is_active=True).order_by(
        AlertHistory.timestamp.desc()).all()
    
    return jsonify({
        'alerts': [
            {
                'id': a.id,
                'type': a.alert_type,
                'message': a.message,
                'timestamp': a.timestamp.isoformat(),
                'is_active': a.is_active
            }
            for a in alerts
        ]
    })

@app.route('/api/statistics')
def get_statistics():
    """Get monitoring statistics"""
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    
    total_incidents = IncidentLog.query.count()
    today_incidents = IncidentLog.query.filter(
        IncidentLog.timestamp >= one_day_ago).count()
    high_severity = IncidentLog.query.filter_by(severity='HIGH').count()
    active_alerts = AlertHistory.query.filter_by(is_active=True).count()

    detector_stats = detector.get_statistics()
    latest = detector.get_latest_statistics()
    
    # Realtime gauge fields
    workers = int(latest.get('workers_detected', 0))
    helmets = int(latest.get('helmets_detected', 0))
    compliance_rate = int((helmets / workers) * 100) if workers > 0 else 0

    # Calculate safety score using high_severity
    safety_score = max(0, 100 - (high_severity * 10))
    
    return jsonify({
        'total_incidents': total_incidents,
        'today_incidents': today_incidents,
        'high_severity': high_severity,
        'active_alerts': active_alerts,
        'safety_score': safety_score,
        'monitoring_status': 'Active' if monitoring_active else 'Inactive',
        'realtime': {
            'workers_detected': workers,
            'helmets_detected': helmets,
            'compliance_rate': compliance_rate,
            'last_violations': latest.get('violations', []),
            'confidence': round(latest.get('confidence', 0.0) * 100, 2)
        },
        'detector_history': detector_stats
    })

@app.route('/api/alert_config', methods=['GET', 'POST'])
def alert_config():
    """Get/Set alert configuration"""
    global alert_threshold
    
    if request.method == 'POST':
        data = request.get_json()
        alert_threshold = data.get('threshold', alert_threshold)
        return jsonify({'status': 'success', 'threshold': alert_threshold})
    
    return jsonify({'threshold': alert_threshold})

@app.route('/api/clear_alerts', methods=['POST'])
def clear_alerts():
    """Clear active alerts"""
    AlertHistory.query.update({'is_active': False})
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Alerts cleared'})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'monitoring': monitoring_active
    })

if __name__ == '__main__':
    init_db()
    print("=" * 60)
    print("AI Smart Safety Monitoring System")
    print("=" * 60)
    print("Starting application on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
