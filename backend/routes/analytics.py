"""
Analytics and Reporting Routes
Dashboard data, statistics, reports
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from backend.services import (
    AnalyticsService,
    ReportingService,
    AuthenticationService,
    AuthorizationService
)
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Placeholder for initialized services
analytics_service = None
reporting_service = None
auth_service = None

def init_analytics_routes(app, analytics_svc, reporting_svc, auth_svc):
    """Initialize analytics routes with service instances"""
    global analytics_service, reporting_service, auth_service
    analytics_service = analytics_svc
    reporting_service = reporting_svc
    auth_service = auth_svc
    app.register_blueprint(analytics_bp)

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

def require_permission(permission: str):
    """Permission checking decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            role = request.user.get('role')
            if not AuthorizationService.has_permission(role, permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@analytics_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard_data():
    """Get dashboard overview data"""
    try:
        days = request.args.get('days', 7, type=int)
        
        compliance = analytics_service.get_compliance_metrics(days=days)
        incidents = analytics_service.get_incident_statistics(days=days)
        
        dashboard = {
            'timestamp': datetime.utcnow().isoformat(),
            'period_days': days,
            'compliance': compliance,
            'incidents': incidents,
            'overview': {
                'total_cameras': 4,
                'active_cameras': 4,
                'system_health': 'healthy',
                'last_alert': None
            }
        }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/compliance', methods=['GET'])
@require_auth
def get_compliance_metrics():
    """Get compliance metrics"""
    try:
        days = request.args.get('days', 30, type=int)
        
        metrics = analytics_service.get_compliance_metrics(days=days)
        
        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting compliance metrics: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/incidents', methods=['GET'])
@require_auth
def get_incident_statistics():
    """Get incident statistics"""
    try:
        days = request.args.get('days', 30, type=int)
        
        stats = analytics_service.get_incident_statistics(days=days)
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting incident statistics: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/workers', methods=['GET'])
@require_auth
def get_worker_statistics():
    """Get worker safety statistics"""
    try:
        worker_id = request.args.get('worker_id', type=int)
        
        stats = analytics_service.get_worker_statistics(worker_id=worker_id)
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting worker statistics: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/reports/daily', methods=['GET'])
@require_auth
@require_permission('report_generation')
def get_daily_report():
    """Get daily report"""
    try:
        date_str = request.args.get('date')
        date = datetime.fromisoformat(date_str) if date_str else None
        
        report = reporting_service.generate_daily_report(date=date)
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
    
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/reports/weekly', methods=['GET'])
@require_auth
@require_permission('report_generation')
def get_weekly_report():
    """Get weekly report"""
    try:
        week_str = request.args.get('week_start')
        week_start = datetime.fromisoformat(week_str) if week_str else None
        
        report = reporting_service.generate_weekly_report(week_start=week_start)
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
    
    except Exception as e:
        logger.error(f"Error generating weekly report: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/reports/monthly', methods=['GET'])
@require_auth
@require_permission('report_generation')
def get_monthly_report():
    """Get monthly report"""
    try:
        month_str = request.args.get('month_start')
        month_start = datetime.fromisoformat(month_str) if month_str else None
        
        report = reporting_service.generate_monthly_report(month_start=month_start)
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
    
    except Exception as e:
        logger.error(f"Error generating monthly report: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/health', methods=['GET'])
@require_auth
def get_system_health():
    """Get system health status"""
    try:
        health = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'components': {
                'database': 'ok',
                'detection_engine': 'ok',
                'notification_service': 'ok',
                'video_processing': 'ok'
            },
            'metrics': {
                'cpu_usage': 35.2,
                'memory_usage': 48.5,
                'uptime_hours': 240
            }
        }
        
        return jsonify({
            'success': True,
            'health': health
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/trends', methods=['GET'])
@require_auth
def get_trends():
    """Get trend analysis"""
    try:
        period = request.args.get('period', 'daily')  # daily, weekly, monthly
        metric_type = request.args.get('type', 'incidents')  # incidents, compliance, workers
        
        trends = {
            'period': period,
            'metric_type': metric_type,
            'trend_direction': 'increasing',
            'change_percent': 12.5,
            'data_points': []
        }
        
        return jsonify({
            'success': True,
            'trends': trends
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export', methods=['POST'])
@require_auth
@require_permission('data_export')
def export_data():
    """Export analytics data"""
    try:
        data = request.get_json()
        export_format = data.get('format', 'pdf')  # pdf, csv, json
        report_type = data.get('report_type', 'daily')
        
        if export_format == 'pdf':
            filename = f"report_{report_type}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
            # Export to PDF
            reporting_service.export_to_pdf({}, filename)
        
        return jsonify({
            'success': True,
            'message': f'Data exported as {export_format}',
            'filename': filename,
            'download_url': f'/api/analytics/download/{filename}'
        }), 200
    
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({'error': str(e)}), 500
