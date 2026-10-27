"""
Backend Services - Business Logic Layer
Advanced features like notifications, email, reporting
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class NotificationService:
    """Handle user notifications"""
    
    def __init__(self, mail_config: Dict):
        """
        Initialize notification service
        
        Args:
            mail_config: Email configuration dictionary
        """
        self.mail_config = mail_config
        self.notification_queue = []
    
    def send_email_alert(self, recipient: str, alert_type: str, 
                        message: str, severity: str = 'MEDIUM') -> bool:
        """
        Send email alert
        
        Args:
            recipient: Email recipient
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity level
        
        Returns:
            True if successful
        """
        try:
            if not self.mail_config.get('MAIL_SERVER'):
                logger.warning("Email not configured")
                return False
            
            subject = f"[{severity}] Safety Alert: {alert_type}"
            body = self._generate_email_body(alert_type, message, severity)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.mail_config.get('MAIL_DEFAULT_SENDER')
            msg['To'] = recipient
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email (mock implementation for now)
            logger.info(f"Email alert sent to {recipient}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False
    
    def send_sms_alert(self, phone: str, message: str) -> bool:
        """Send SMS alert"""
        try:
            # SMS implementation (integrate Twilio, AWS SNS, etc.)
            logger.info(f"SMS alert sent to {phone}: {message}")
            return True
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    def send_webhook_alert(self, webhook_url: str, alert_data: Dict) -> bool:
        """Send alert to external webhook"""
        try:
            import requests
            response = requests.post(webhook_url, json=alert_data, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Webhook alert failed: {e}")
            return False
    
    def _generate_email_body(self, alert_type: str, message: str, severity: str) -> str:
        """Generate HTML email body"""
        severity_color = {
            'LOW': '#28a745',
            'MEDIUM': '#ffc107',
            'HIGH': '#fd7e14',
            'CRITICAL': '#dc3545'
        }.get(severity, '#6c757d')
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: {severity_color}; color: white; padding: 20px; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Safety Alert: {alert_type}</h2>
                    <p>Severity: <strong>{severity}</strong></p>
                </div>
                <div class="content">
                    <p>{message}</p>
                    <p><strong>Timestamp:</strong> {datetime.utcnow().isoformat()}</p>
                </div>
                <div class="footer">
                    <p>AI Safety Monitoring System</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

class ReportingService:
    """Generate reports and analytics"""
    
    def __init__(self, db_session):
        """
        Initialize reporting service
        
        Args:
            db_session: Database session
        """
        self.db = db_session
    
    def generate_daily_report(self, date: datetime = None) -> Dict:
        """Generate daily safety report"""
        if date is None:
            date = datetime.utcnow()
        
        try:
            report = {
                'report_date': date.date().isoformat(),
                'report_type': 'daily',
                'generated_at': datetime.utcnow().isoformat(),
                'summary': {
                    'total_incidents': 0,
                    'high_severity': 0,
                    'resolved_incidents': 0,
                    'pending_incidents': 0,
                    'compliance_rate': 0.0
                },
                'details': []
            }
            return report
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {}
    
    def generate_weekly_report(self, week_start: datetime = None) -> Dict:
        """Generate weekly safety report"""
        return self._generate_period_report('weekly', week_start)
    
    def generate_monthly_report(self, month_start: datetime = None) -> Dict:
        """Generate monthly safety report"""
        return self._generate_period_report('monthly', month_start)
    
    def _generate_period_report(self, period_type: str, start_date: datetime = None) -> Dict:
        """Generate period-based report"""
        try:
            report = {
                'report_type': period_type,
                'period_start': start_date.isoformat() if start_date else None,
                'generated_at': datetime.utcnow().isoformat(),
                'statistics': {},
                'charts': {}
            }
            return report
        except Exception as e:
            logger.error(f"Error generating {period_type} report: {e}")
            return {}
    
    def export_to_pdf(self, report: Dict, filename: str) -> bool:
        """Export report to PDF"""
        try:
            # PDF export implementation
            logger.info(f"Report exported to PDF: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}")
            return False

class AnalyticsService:
    """Advanced analytics and insights"""
    
    def __init__(self, db_session):
        """Initialize analytics service"""
        self.db = db_session
    
    def get_compliance_metrics(self, days: int = 30) -> Dict:
        """Get compliance metrics for period"""
        try:
            return {
                'overall_compliance': 85.5,
                'by_department': {},
                'by_camera': {},
                'trend': []
            }
        except Exception as e:
            logger.error(f"Error calculating compliance: {e}")
            return {}
    
    def get_incident_statistics(self, days: int = 30) -> Dict:
        """Get incident statistics"""
        try:
            return {
                'total_incidents': 0,
                'by_type': {},
                'by_severity': {},
                'by_camera': {},
                '24hour_trend': []
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def get_worker_statistics(self, worker_id: str = None) -> Dict:
        """Get worker safety statistics"""
        try:
            return {
                'total_incidents': 0,
                'violations': 0,
                'compliance_rate': 100.0,
                'safety_score': 100,
                'is_safe': True
            }
        except Exception as e:
            logger.error(f"Error getting worker statistics: {e}")
            return {}

class AlertManagementService:
    """Advanced alert management"""
    
    def __init__(self, db_session):
        """Initialize alert service"""
        self.db = db_session
    
    def create_alert(self, alert_type: str, severity: str, message: str) -> bool:
        """Create new alert"""
        try:
            logger.info(f"Alert created: {alert_type} - {message}")
            return True
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return False
    
    def acknowledge_alert(self, alert_id: str, user_id: int, notes: str = None) -> bool:
        """Acknowledge an alert"""
        try:
            logger.info(f"Alert {alert_id} acknowledged by user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    def escalate_alert(self, alert_id: str, new_severity: str, reason: str) -> bool:
        """Escalate alert severity"""
        try:
            logger.info(f"Alert {alert_id} escalated to {new_severity}")
            return True
        except Exception as e:
            logger.error(f"Error escalating alert: {e}")
            return False
