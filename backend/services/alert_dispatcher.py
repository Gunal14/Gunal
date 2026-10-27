"""
Emergency Alert Dispatcher Service
Triggers real-time alerts to all emergency contacts (primary + additional)
Supports multiple notification channels: WhatsApp, SMS, Email
"""

import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
import threading
from queue import Queue
import time

logger = logging.getLogger(__name__)


@dataclass
class AlertTrigger:
    """Alert trigger event"""
    camera_id: int
    risk_type: str  # not_wearing_helmet, improper_stance, unsafe_behavior
    risk_category: str  # PPE, POSTURE, BEHAVIOR, HAZMAT
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence_score: float  # 0-1
    risk_score: int  # 0-100
    location: str
    worker_id: Optional[str] = None
    environmental_conditions: Optional[Dict] = None
    image_url: Optional[str] = None
    dashboard_link: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate alert trigger"""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class AlertDispatcher:
    """Dispatch emergency alerts to all emergency contacts"""
    
    def __init__(self, db=None, whatsapp_service=None, email_service=None):
        """
        Initialize Alert Dispatcher
        
        Args:
            db: SQLAlchemy database instance
            whatsapp_service: WhatsApp service instance
            email_service: Email service instance
        """
        self.db = db
        self.whatsapp_service = whatsapp_service
        self.email_service = email_service
        
        # Event queue for async processing
        self.alert_queue = Queue()
        self.is_running = False
        self.worker_thread = None
        
        logger.info("AlertDispatcher initialized")
    
    def start_background_worker(self):
        """Start background worker for async alert processing"""
        if self.is_running:
            logger.warning("Background worker already running")
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(
            target=self._background_worker,
            daemon=True
        )
        self.worker_thread.start()
        logger.info("Background alert worker started")
    
    def stop_background_worker(self):
        """Stop background worker"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("Background alert worker stopped")
    
    def _background_worker(self):
        """Process alerts from queue in background"""
        while self.is_running:
            try:
                # Get alert from queue with timeout
                try:
                    alert_data = self.alert_queue.get(timeout=1)
                except:
                    continue
                
                # Process alert
                self._process_alert(alert_data)
                
            except Exception as e:
                logger.error(f"Error in background worker: {e}")
                time.sleep(1)
    
    def trigger_emergency_alert(
        self,
        alert_trigger: AlertTrigger,
        user_id: int,
        async_mode: bool = True
    ) -> Dict[str, any]:
        """
        Trigger emergency alert to all emergency contacts
        
        Args:
            alert_trigger: AlertTrigger event
            user_id: User ID (admin/supervisor)
            async_mode: Process alerts asynchronously
            
        Returns:
            Dictionary with alert results
        """
        try:
            # Only trigger for MEDIUM+ severity
            severity_levels = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            if severity_levels.get(alert_trigger.severity, 0) < 2:
                logger.debug(f"Skipping alert: severity too low ({alert_trigger.severity})")
                return {'success': False, 'reason': 'Severity too low'}
            
            if async_mode:
                # Queue for background processing
                self.alert_queue.put({
                    'alert_trigger': alert_trigger,
                    'user_id': user_id
                })
                
                return {
                    'success': True,
                    'message': 'Alert queued for dispatch',
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                # Process synchronously
                return self._process_alert({
                    'alert_trigger': alert_trigger,
                    'user_id': user_id
                })
        
        except Exception as e:
            logger.error(f"Error triggering emergency alert: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_alert(self, alert_data: Dict) -> Dict:
        """Process a single alert"""
        try:
            alert_trigger = alert_data['alert_trigger']
            user_id = alert_data['user_id']
            
            # Fetch user and emergency contacts
            if not self.db:
                logger.error("Database not available")
                return {'success': False, 'error': 'Database unavailable'}
            
            from backend.database.models import User, EmergencyContact
            
            user = User.query.filter_by(id=user_id).first()
            if not user:
                logger.error(f"User {user_id} not found")
                return {'success': False, 'error': 'User not found'}
            
            # Build alert message
            dashboard_link = alert_trigger.dashboard_link or f"https://dashboard.com/alerts/{user_id}"
            
            alert_message = {
                'title': f"{alert_trigger.severity} ALERT",
                'risk_type': alert_trigger.risk_type,
                'location': alert_trigger.location,
                'timestamp': alert_trigger.timestamp,
                'confidence': f"{alert_trigger.confidence_score * 100:.1f}%",
                'risk_score': alert_trigger.risk_score,
                'camera_id': alert_trigger.camera_id,
                'worker_id': alert_trigger.worker_id,
                'dashboard_link': dashboard_link
            }
            
            # Get all recipients
            recipients = self._get_alert_recipients(user, alert_trigger.severity)
            
            if not recipients:
                logger.warning(f"No recipients configured for user {user_id}")
                return {'success': False, 'reason': 'No recipients'}
            
            # Send alerts to all recipients
            results = self._send_to_recipients(
                recipients,
                alert_trigger,
                alert_message
            )
            
            # Log alert in database
            self._log_alert(user_id, alert_trigger, results)
            
            logger.info(f"Alert dispatched to {len(recipients)} recipients")
            
            return {
                'success': True,
                'recipients_contacted': len(recipients),
                'delivery_status': results,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_alert_recipients(self, user: 'User', severity: str) -> List[Dict]:
        """
        Get all recipients for alert based on severity and preferences
        
        Returns list of dicts with:
        - phone_number
        - email
        - whatsapp_enabled
        - sms_enabled
        - email_enabled
        - contact_type: 'primary' or 'additional'
        """
        from backend.database.models import EmergencyContact
        
        recipients = []
        severity_level = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(severity, 0)
        
        # Add primary number
        primary_recipient = {
            'phone_number': user.mobile_number,
            'email': user.email,
            'whatsapp_enabled': True,  # Primary always gets WhatsApp
            'sms_enabled': True,
            'email_enabled': True,
            'contact_type': 'primary',
            'contact_name': f"{user.first_name} {user.last_name}"
        }
        recipients.append(primary_recipient)
        
        # Add additional emergency contacts (filtered by severity)
        additional_contacts = EmergencyContact.query.filter_by(
            user_id=user.id,
            is_active=True
        ).all()
        
        for contact in additional_contacts:
            # Check severity threshold for this contact
            severity_map = {
                'CRITICAL': contact.alert_critical,
                'HIGH': contact.alert_high,
                'MEDIUM': contact.alert_medium,
                'LOW': contact.alert_low
            }
            
            if severity_map.get(severity, False):
                additional_recipient = {
                    'phone_number': contact.phone_number,
                    'email': contact.email,
                    'whatsapp_enabled': contact.whatsapp_enabled,
                    'sms_enabled': contact.sms_enabled,
                    'email_enabled': contact.email_enabled,
                    'contact_type': 'additional',
                    'contact_name': contact.contact_name,
                    'verified': contact.verified
                }
                recipients.append(additional_recipient)
        
        return recipients
    
    def _send_to_recipients(
        self,
        recipients: List[Dict],
        alert_trigger: AlertTrigger,
        alert_message: Dict
    ) -> Dict[str, Dict]:
        """
        Send alert to all recipients using their preferred channels
        
        Returns: Dict mapping phone_numbers to delivery status
        """
        from backend.services.whatsapp_service import WhatsAppMessage, get_whatsapp_service
        
        results = {}
        
        for recipient in recipients:
            phone = recipient['phone_number']
            recipient_results = {
                'contact_name': recipient['contact_name'],
                'contact_type': recipient['contact_type'],
                'channels': {}
            }
            
            try:
                # WhatsApp
                if recipient['whatsapp_enabled']:
                    ws = get_whatsapp_service()
                    if ws and ws.is_configured():
                        msg = WhatsAppMessage(
                            recipient=phone,
                            title=alert_message['title'],
                            risk_type=alert_message['risk_type'],
                            location=alert_message['location'],
                            timestamp=alert_message['timestamp'],
                            dashboard_link=alert_message['dashboard_link'],
                            message_type='emergency',
                            image_url=alert_trigger.image_url
                        )
                        
                        success, msg_id = ws.send_alert(msg)
                        recipient_results['channels']['whatsapp'] = {
                            'sent': success,
                            'message_id': msg_id if success else None,
                            'error': msg_id if not success else None
                        }
                        logger.info(f"WhatsApp alert sent to {phone}: {msg_id}")
                    else:
                        recipient_results['channels']['whatsapp'] = {
                            'sent': False,
                            'error': 'WhatsApp service not configured'
                        }
                
                # SMS (placeholder - integrate with Twilio SMS)
                if recipient['sms_enabled']:
                    recipient_results['channels']['sms'] = {
                        'sent': False,
                        'error': 'SMS provider not configured'
                    }
                
                # Email
                if recipient['email_enabled'] and recipient['email']:
                    # Placeholder - integrate with email service
                    recipient_results['channels']['email'] = {
                        'sent': False,
                        'error': 'Email service not configured'
                    }
                
            except Exception as e:
                logger.error(f"Error sending alert to {phone}: {e}")
                recipient_results['error'] = str(e)
            
            results[phone] = recipient_results
        
        return results
    
    def _log_alert(self, user_id: int, alert_trigger: AlertTrigger, results: Dict):
        """Log alert dispatch in database"""
        try:
            from backend.database.models import RiskAlert
            
            alert = RiskAlert(
                camera_id=alert_trigger.camera_id,
                risk_type=alert_trigger.risk_type,
                risk_category=alert_trigger.risk_category,
                severity=alert_trigger.severity,
                confidence_score=alert_trigger.confidence_score,
                risk_score=alert_trigger.risk_score,
                worker_id=alert_trigger.worker_id,
                environmental_conditions=alert_trigger.environmental_conditions,
                image_url=alert_trigger.image_url,
                status='notified',
                notified=True,
                notified_at=datetime.utcnow(),
                first_detection_time=alert_trigger.timestamp,
                last_detection_time=alert_trigger.timestamp
            )
            
            self.db.session.add(alert)
            self.db.session.commit()
            
            logger.info(f"Alert logged in database for user {user_id}")
        
        except Exception as e:
            logger.error(f"Error logging alert: {e}")
            if self.db:
                self.db.session.rollback()


# Global dispatcher instance
_alert_dispatcher = None


def initialize_alert_dispatcher(app=None, db=None, whatsapp_service=None, email_service=None) -> AlertDispatcher:
    """Initialize global alert dispatcher"""
    global _alert_dispatcher
    
    _alert_dispatcher = AlertDispatcher(
        db=db,
        whatsapp_service=whatsapp_service,
        email_service=email_service
    )
    
    # Start background worker
    _alert_dispatcher.start_background_worker()
    
    logger.info("AlertDispatcher initialized and background worker started")
    
    return _alert_dispatcher


def get_alert_dispatcher() -> Optional[AlertDispatcher]:
    """Get dispatcher instance"""
    global _alert_dispatcher
    return _alert_dispatcher
