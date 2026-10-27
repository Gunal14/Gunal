"""
Multi-Channel Notification Service (Enhanced)
Email, SMS, and WhatsApp notifications for emergency alerts
Designed for 30-40 simultaneous cameras with advanced alert routing
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
import json

logger = logging.getLogger(__name__)


@dataclass
class NotificationMessage:
    """Unified notification message"""
    recipient: str
    subject: str
    title: str
    body: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    action_url: Optional[str] = None
    image_url: Optional[str] = None
    alert_id: Optional[str] = None
    timestamp: Optional[datetime] = None


class NotificationChannel(ABC):
    """Abstract base for notification channels"""
    
    @abstractmethod
    def send(self, message: NotificationMessage) -> Tuple[bool, str]:
        """Send notification via this channel"""
        pass
    
    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """Validate recipient format"""
        pass


class EmailNotificationChannel(NotificationChannel):
    """Send notifications via Email"""
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        """Initialize email channel"""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender_email = username
        self.channel_name = "EMAIL"
    
    def send(self, message: NotificationMessage) -> Tuple[bool, str]:
        """Send email notification"""
        
        try:
            if not self.validate_recipient(message.recipient):
                return False, "Invalid email format"
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = self.sender_email
            msg['To'] = message.recipient
            msg['X-Priority'] = self._get_priority(message.severity)
            
            html_body = self._create_html_email(message)
            
            msg.attach(MIMEText(message.body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {message.recipient}")
            return True, "Email sent successfully"
        
        except Exception as e:
            error_msg = f"Email send failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate email format"""
        return '@' in recipient and '.' in recipient
    
    def _get_priority(self, severity: str) -> str:
        """Get email priority level"""
        priority_map = {
            'LOW': '5',
            'MEDIUM': '3',
            'HIGH': '2',
            'CRITICAL': '1',
        }
        return priority_map.get(severity, '3')
    
    def _create_html_email(self, message: NotificationMessage) -> str:
        """Create HTML email content"""
        
        severity_color = {
            'LOW': '#4CAF50',
            'MEDIUM': '#FF9800',
            'HIGH': '#F44336',
            'CRITICAL': '#8B0000',
        }
        
        color = severity_color.get(message.severity, '#2196F3')
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .header {{ background-color: {color}; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f5f5f5; }}
                    .alert {{ background-color: white; padding: 20px; margin: 10px 0; border-left: 4px solid {color}; }}
                    .severity {{ font-weight: bold; color: {color}; font-size: 18px; }}
                    .button {{ 
                        background-color: {color}; 
                        color: white; 
                        padding: 12px 30px; 
                        text-decoration: none;
                        border-radius: 4px;
                        display: inline-block;
                        margin-top: 15px;
                    }}
                    .footer {{ background-color: #333; color: white; padding: 10px; text-align: center; font-size: 12px; }}
                    .timestamp {{ color: #666; font-size: 12px; margin-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚨 Safety Alert Notification</h1>
                    </div>
                    <div class="content">
                        <div class="alert">
                            <p class="severity">Severity: {message.severity}</p>
                            <h2>{message.title}</h2>
                            <p>{message.body}</p>
                            <p class="timestamp">Alert ID: {message.alert_id}</p>
                            <p class="timestamp">Time: {message.timestamp or datetime.utcnow().isoformat()}</p>
                            
                            {f'<img src="{message.image_url}" style="max-width: 100%; margin: 10px 0;" />' if message.image_url else ''}
                            
                            {f'<a href="{message.action_url}" class="button">View Details & Take Action</a>' if message.action_url else ''}
                        </div>
                    </div>
                    <div class="footer">
                        <p>AI Safety Monitoring System - Automatic Alert</p>
                        <p>Please do not reply to this email</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html


class SMSNotificationChannel(NotificationChannel):
    """Send notifications via SMS using Twilio"""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        """Initialize SMS channel using Twilio"""
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.channel_name = "SMS"
        
        try:
            from twilio.rest import Client
            self.client = Client(account_sid, auth_token)
        except ImportError:
            logger.warning("Twilio not installed. SMS notifications will be disabled.")
            self.client = None
    
    def send(self, message: NotificationMessage) -> Tuple[bool, str]:
        """Send SMS notification"""
        
        if not self.client:
            return False, "Twilio client not initialized"
        
        try:
            if not self.validate_recipient(message.recipient):
                return False, "Invalid phone number format"
            
            sms_body = self._create_sms_body(message)
            
            sms = self.client.messages.create(
                body=sms_body,
                from_=self.from_number,
                to=message.recipient
            )
            
            logger.info(f"SMS sent to {message.recipient} (SID: {sms.sid})")
            return True, f"SMS sent (SID: {sms.sid})"
        
        except Exception as e:
            error_msg = f"SMS send failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate phone number format"""
        clean = recipient.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        return len(clean) >= 10 and clean.isdigit()
    
    def _create_sms_body(self, message: NotificationMessage) -> str:
        """Create SMS message body"""
        
        severity_emoji = {
            'LOW': '⚠️',
            'MEDIUM': '⚠️⚠️',
            'HIGH': '🔴',
            'CRITICAL': '🚨',
        }
        
        emoji = severity_emoji.get(message.severity, '⚠️')
        body = f"{emoji} [{message.severity}] {message.title}: {message.body}"
        if message.alert_id:
            body += f" ID:{message.alert_id[-6:]}"
        
        return body[:160]


class WhatsAppNotificationChannel(NotificationChannel):
    """Send notifications via WhatsApp using Twilio"""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        """Initialize WhatsApp channel using Twilio"""
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.channel_name = "WHATSAPP"
        
        try:
            from twilio.rest import Client
            self.client = Client(account_sid, auth_token)
        except ImportError:
            logger.warning("Twilio not installed. WhatsApp notifications will be disabled.")
            self.client = None
    
    def send(self, message: NotificationMessage) -> Tuple[bool, str]:
        """Send WhatsApp notification"""
        
        if not self.client:
            return False, "Twilio client not initialized"
        
        try:
            if not self.validate_recipient(message.recipient):
                return False, "Invalid phone number format"
            
            wa_body = self._create_whatsapp_body(message)
            
            to_number = f"whatsapp:{message.recipient}" if not message.recipient.startswith('whatsapp:') else message.recipient
            from_number = f"whatsapp:{self.from_number}" if not self.from_number.startswith('whatsapp:') else self.from_number
            
            msg = self.client.messages.create(
                body=wa_body,
                from_=from_number,
                to=to_number
            )
            
            logger.info(f"WhatsApp sent to {message.recipient} (SID: {msg.sid})")
            return True, f"WhatsApp sent (SID: {msg.sid})"
        
        except Exception as e:
            error_msg = f"WhatsApp send failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate WhatsApp number"""
        clean = recipient.replace('whatsapp:', '').replace('+', '').replace('-', '').replace(' ', '')
        return len(clean) >= 10 and clean.replace('+', '').isdigit()
    
    def _create_whatsapp_body(self, message: NotificationMessage) -> str:
        """Create WhatsApp message with rich formatting"""
        
        severity_emoji = {
            'LOW': '⚠️ Warning',
            'MEDIUM': '⚠️ Moderate Alert',
            'HIGH': '🔴 High Alert',
            'CRITICAL': '🚨 CRITICAL ALERT',
        }
        
        header = severity_emoji.get(message.severity, '⚠️ Alert')
        
        body = f"""
{header}

*{message.title}*

{message.body}

_Alert ID: {message.alert_id}_
_Time: {(message.timestamp or datetime.utcnow()).isoformat()}_

{f'[View Details]({message.action_url})' if message.action_url else ''}
"""
        
        return body.strip()


class NotificationRouter:
    """Route notifications through appropriate channels based on severity"""
    
    def __init__(self):
        """Initialize notification router"""
        self.channels: Dict[str, NotificationChannel] = {}
        self.routing_rules = {
            'LOW': ['EMAIL'],
            'MEDIUM': ['EMAIL', 'SMS'],
            'HIGH': ['EMAIL', 'SMS', 'WHATSAPP'],
            'CRITICAL': ['EMAIL', 'SMS', 'WHATSAPP'],
        }
    
    def register_channel(self, name: str, channel: NotificationChannel):
        """Register a notification channel"""
        self.channels[name] = channel
        logger.info(f"Registered notification channel: {name}")
    
    def send_notification(self, message: NotificationMessage,
                         override_channels: Optional[List[str]] = None) -> Dict:
        """Send notification through appropriate channels"""
        
        if override_channels:
            channels_to_use = override_channels
        else:
            channels_to_use = self.routing_rules.get(message.severity, ['EMAIL'])
        
        results = {}
        
        for channel_name in channels_to_use:
            if channel_name not in self.channels:
                results[channel_name] = {
                    'success': False,
                    'message': f"Channel {channel_name} not configured"
                }
                continue
            
            channel = self.channels[channel_name]
            success, response = channel.send(message)
            results[channel_name] = {
                'success': success,
                'message': response
            }
        
        return results
    
    def configure_email(self, smtp_host: str, smtp_port: int,
                       username: str, password: str):
        """Configure email channel"""
        channel = EmailNotificationChannel(smtp_host, smtp_port, username, password)
        self.register_channel('EMAIL', channel)
    
    def configure_sms(self, account_sid: str, auth_token: str, from_number: str):
        """Configure SMS channel"""
        channel = SMSNotificationChannel(account_sid, auth_token, from_number)
        self.register_channel('SMS', channel)
    
    def configure_whatsapp(self, account_sid: str, auth_token: str, from_number: str):
        """Configure WhatsApp channel"""
        channel = WhatsAppNotificationChannel(account_sid, auth_token, from_number)
        self.register_channel('WHATSAPP', channel)


class AdvancedNotificationService:
    """
    High-level notification service for multi-camera monitoring
    - Multi-channel routing (email, SMS, WhatsApp)
    - Contact management (up to 10 emergency contacts per admin)
    - Notification logging and tracking
    - Delivery confirmation
    """
    
    def __init__(self):
        """Initialize notification service"""
        self.router = NotificationRouter()
        self.notification_queue = []
        self.sent_notifications = []
    
    def initialize_channels(self, config: Dict):
        """Initialize notification channels from config"""
        
        if config.get('email_enabled'):
            self.router.configure_email(
                smtp_host=config.get('smtp_host', 'smtp.gmail.com'),
                smtp_port=config.get('smtp_port', 587),
                username=config.get('email_username'),
                password=config.get('email_password'),
            )
        
        if config.get('sms_enabled'):
            self.router.configure_sms(
                account_sid=config.get('twilio_account_sid'),
                auth_token=config.get('twilio_auth_token'),
                from_number=config.get('twilio_sms_number'),
            )
        
        if config.get('whatsapp_enabled'):
            self.router.configure_whatsapp(
                account_sid=config.get('twilio_account_sid'),
                auth_token=config.get('twilio_auth_token'),
                from_number=config.get('twilio_whatsapp_number'),
            )
    
    def send_emergency_alert(self, alert_data: Dict,
                            emergency_contacts: List[Dict]) -> Dict:
        """Send emergency alert to multiple contacts"""
        
        results = {
            'total_contacts': len(emergency_contacts),
            'successful': 0,
            'failed': 0,
            'notifications': {}
        }
        
        for contact in emergency_contacts:
            severity = alert_data.get('severity', 'MEDIUM')
            if not self._contact_accepts_severity(contact, severity):
                continue
            
            message = NotificationMessage(
                recipient=contact.get('phone_number'),
                subject=alert_data.get('subject', 'Safety Alert'),
                title=alert_data.get('title', 'Safety Incident'),
                body=alert_data.get('body', ''),
                severity=severity,
                action_url=alert_data.get('action_url'),
                image_url=alert_data.get('image_url'),
                alert_id=alert_data.get('alert_id'),
                timestamp=datetime.utcnow(),
            )
            
            channels = self._get_contact_channels(contact)
            send_results = self.router.send_notification(message, channels)
            
            contact_name = contact.get('contact_name', 'Unknown')
            results['notifications'][contact_name] = send_results
            
            if any(r['success'] for r in send_results.values()):
                results['successful'] += 1
            else:
                results['failed'] += 1
        
        logger.info(f"Emergency alert sent: {results['successful']}/{results['total_contacts']} successful")
        return results
    
    def _contact_accepts_severity(self, contact: Dict, severity: str) -> bool:
        """Check if contact wants this severity level"""
        severity_map = {
            'LOW': 'alert_low',
            'MEDIUM': 'alert_medium',
            'HIGH': 'alert_high',
            'CRITICAL': 'alert_critical',
        }
        field = severity_map.get(severity, 'alert_medium')
        return contact.get(field, False)
    
    def _get_contact_channels(self, contact: Dict) -> List[str]:
        """Get enabled channels for contact"""
        channels = []
        if contact.get('email_enabled'):
            channels.append('EMAIL')
        if contact.get('sms_enabled'):
            channels.append('SMS')
        if contact.get('whatsapp_enabled'):
            channels.append('WHATSAPP')
        return channels if channels else ['EMAIL']


# Global instance
advanced_notification_service = AdvancedNotificationService()
