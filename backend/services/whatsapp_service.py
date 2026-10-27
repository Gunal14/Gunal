"""
WhatsApp Integration Service
Multi-provider support for emergency alert delivery:
- Twilio WhatsApp API
- Meta Cloud WhatsApp API
- Nexmo/Vonage (optional)
"""

import logging
import os
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class WhatsAppMessage:
    """WhatsApp message object"""
    recipient: str  # Phone number with country code (e.g., +1-234-567-8900)
    title: str
    risk_type: str
    location: str
    timestamp: datetime
    dashboard_link: str
    message_type: str = "emergency"  # emergency, warning, info
    image_url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'recipient': self.recipient,
            'title': self.title,
            'risk_type': self.risk_type,
            'location': self.location,
            'timestamp': self.timestamp.isoformat(),
            'dashboard_link': self.dashboard_link,
            'message_type': self.message_type,
            'image_url': self.image_url
        }


class WhatsAppProvider(ABC):
    """Abstract base class for WhatsApp providers"""
    
    @abstractmethod
    def send_message(self, message: WhatsAppMessage) -> Tuple[bool, str]:
        """Send WhatsApp message. Returns (success, message_id or error)"""
        pass
    
    @abstractmethod
    def verify_credentials(self) -> bool:
        """Verify API credentials"""
        pass


class TwilioWhatsAppProvider(WhatsAppProvider):
    """Twilio WhatsApp API provider"""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        """
        Initialize Twilio provider
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            from_number: Twilio WhatsApp number (e.g., +1-234-567-8901)
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}"
    
    def verify_credentials(self) -> bool:
        """Verify Twilio API credentials"""
        try:
            url = f"{self.base_url}.json"
            response = requests.get(url, auth=(self.account_sid, self.auth_token), timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Twilio credential verification failed: {e}")
            return False
    
    def send_message(self, message: WhatsAppMessage) -> Tuple[bool, str]:
        """
        Send WhatsApp message via Twilio
        
        Args:
            message: WhatsAppMessage object
            
        Returns:
            (success, message_id or error_msg)
        """
        try:
            # Format message body
            body = self._format_message_body(message)
            
            # Twilio Messages endpoint
            url = f"{self.base_url}/Messages.json"
            
            # Message data with media if image provided
            data = {
                'From': f'whatsapp:{self.from_number}',
                'To': f'whatsapp:{message.recipient}',
                'Body': body
            }
            
            # Add media URL if image exists
            if message.image_url:
                data['MediaUrl'] = message.image_url
            
            response = requests.post(
                url,
                auth=(self.account_sid, self.auth_token),
                data=data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                message_sid = result.get('sid', 'unknown')
                logger.info(f"WhatsApp message sent via Twilio: {message_sid} to {message.recipient}")
                return True, message_sid
            else:
                error = response.json().get('message', 'Unknown error')
                logger.error(f"Twilio Error ({response.status_code}): {error}")
                return False, f"Twilio Error: {error}"
        
        except Exception as e:
            logger.error(f"Failed to send Twilio WhatsApp message: {e}")
            return False, str(e)
    
    def _format_message_body(self, message: WhatsAppMessage) -> str:
        """Format WhatsApp message body"""
        timestamp_str = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        body = f"""🚨 *EMERGENCY ALERT* 🚨

*{message.title}*

⚠️ *Risk Type:* {message.risk_type}
📍 *Location:* {message.location}
⏰ *Time:* {timestamp_str}

🔗 Dashboard: {message.dashboard_link}

---
*Reply ACKNOWLEDGED to confirm receipt*
"""
        return body


class MetaWhatsAppProvider(WhatsAppProvider):
    """Meta Cloud WhatsApp API provider"""
    
    def __init__(self, business_account_id: str, phone_number_id: str, access_token: str):
        """
        Initialize Meta Cloud WhatsApp provider
        
        Args:
            business_account_id: Meta Business Account ID
            phone_number_id: WhatsApp Business Phone Number ID
            access_token: Meta API access token
        """
        self.business_account_id = business_account_id
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = f"https://graph.instagram.com/v20.0/{phone_number_id}"
    
    def verify_credentials(self) -> bool:
        """Verify Meta API credentials"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(f"{self.base_url}", headers=headers, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Meta credential verification failed: {e}")
            return False
    
    def send_message(self, message: WhatsAppMessage) -> Tuple[bool, str]:
        """
        Send WhatsApp message via Meta Cloud API
        
        Args:
            message: WhatsAppMessage object
            
        Returns:
            (success, message_id or error_msg)
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Format message body
            body = self._format_message_body(message)
            
            # Meta messages endpoint
            url = f"{self.base_url}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": message.recipient.replace('-', '').replace('+', ''),
                "type": "text",
                "text": {"preview_url": True, "body": body}
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code in [200, 201]:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id', 'unknown')
                logger.info(f"WhatsApp message sent via Meta: {message_id} to {message.recipient}")
                return True, message_id
            else:
                error = response.json().get('error', {}).get('message', 'Unknown error')
                logger.error(f"Meta Error ({response.status_code}): {error}")
                return False, f"Meta Error: {error}"
        
        except Exception as e:
            logger.error(f"Failed to send Meta WhatsApp message: {e}")
            return False, str(e)
    
    def _format_message_body(self, message: WhatsAppMessage) -> str:
        """Format WhatsApp message body"""
        timestamp_str = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        body = f"""🚨 EMERGENCY ALERT 🚨

{message.title}

⚠️ Risk Type: {message.risk_type}
📍 Location: {message.location}
⏰ Time: {timestamp_str}

🔗 Dashboard: {message.dashboard_link}

Reply ACKNOWLEDGED to confirm receipt
"""
        return body


class WhatsAppService:
    """Unified WhatsApp service with multi-provider support"""
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize WhatsApp Service
        
        Args:
            provider: 'twilio', 'meta', or None to auto-detect
        """
        self.provider_name = provider or self._detect_provider()
        self.provider = self._initialize_provider()
        self.fallback_providers = []  # For redundancy
        
        if self.provider is None:
            logger.warning("No WhatsApp provider configured")
        else:
            logger.info(f"WhatsApp service initialized with {self.provider_name} provider")
    
    def _detect_provider(self) -> str:
        """Auto-detect configured provider from environment"""
        if os.getenv('TWILIO_ACCOUNT_SID'):
            return 'twilio'
        elif os.getenv('META_BUSINESS_ACCOUNT_ID'):
            return 'meta'
        else:
            return 'twilio'  # Default
    
    def _initialize_provider(self) -> Optional[WhatsAppProvider]:
        """Initialize the configured provider"""
        try:
            if self.provider_name == 'twilio':
                return self._init_twilio()
            elif self.provider_name == 'meta':
                return self._init_meta()
            else:
                logger.error(f"Unknown provider: {self.provider_name}")
                return None
        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp provider: {e}")
            return None
    
    def _init_twilio(self) -> Optional[TwilioWhatsAppProvider]:
        """Initialize Twilio provider"""
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            logger.error("Missing Twilio credentials")
            return None
        
        provider = TwilioWhatsAppProvider(account_sid, auth_token, from_number)
        if provider.verify_credentials():
            return provider
        else:
            logger.error("Twilio credentials verification failed")
            return None
    
    def _init_meta(self) -> Optional[MetaWhatsAppProvider]:
        """Initialize Meta provider"""
        business_account_id = os.getenv('META_BUSINESS_ACCOUNT_ID')
        phone_number_id = os.getenv('META_PHONE_NUMBER_ID')
        access_token = os.getenv('META_ACCESS_TOKEN')
        
        if not all([business_account_id, phone_number_id, access_token]):
            logger.error("Missing Meta credentials")
            return None
        
        provider = MetaWhatsAppProvider(business_account_id, phone_number_id, access_token)
        if provider.verify_credentials():
            return provider
        else:
            logger.error("Meta credentials verification failed")
            return None
    
    def send_alert(self, message: WhatsAppMessage) -> Tuple[bool, str]:
        """
        Send WhatsApp alert
        
        Args:
            message: WhatsAppMessage object
            
        Returns:
            (success, message_id or error_msg)
        """
        if not self.provider:
            return False, "WhatsApp provider not configured"
        
        try:
            success, result = self.provider.send_message(message)
            if success:
                return True, result
            elif self.fallback_providers:
                # Try fallback providers
                logger.warning(f"Primary provider failed, trying fallback...")
                for fallback in self.fallback_providers:
                    success, result = fallback.send_message(message)
                    if success:
                        return True, result
                return False, f"All providers failed. Last error: {result}"
            else:
                return False, result
        except Exception as e:
            logger.error(f"Error sending WhatsApp alert: {e}")
            return False, str(e)
    
    def send_bulk_alerts(self, message_list: List[WhatsAppMessage]) -> Dict[str, bool]:
        """
        Send bulk WhatsApp alerts
        
        Args:
            message_list: List of WhatsAppMessage objects
            
        Returns:
            Dict mapping phone numbers to success status
        """
        results = {}
        for message in message_list:
            success, _ = self.send_alert(message)
            results[message.recipient] = success
            
            # Add slight delay to avoid rate limiting
            import time
            time.sleep(0.5)
        
        return results
    
    def add_fallback_provider(self, provider: WhatsAppProvider) -> None:
        """Add a fallback provider for redundancy"""
        self.fallback_providers.append(provider)
        logger.info(f"Added fallback provider: {provider.__class__.__name__}")
    
    def is_configured(self) -> bool:
        """Check if service is properly configured"""
        return self.provider is not None


# Singleton instance
_whatsapp_service = None


def get_whatsapp_service(provider: Optional[str] = None) -> WhatsAppService:
    """Get or create WhatsApp service instance"""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = WhatsAppService(provider)
    return _whatsapp_service


def initialize_whatsapp_service(app=None) -> WhatsAppService:
    """Initialize WhatsApp service (Flask app context)"""
    global _whatsapp_service
    
    # Check environment configuration
    provider = None
    if os.getenv('TWILIO_ACCOUNT_SID'):
        provider = 'twilio'
    elif os.getenv('META_BUSINESS_ACCOUNT_ID'):
        provider = 'meta'
    
    _whatsapp_service = WhatsAppService(provider)
    logger.info(f"WhatsApp service initialized: {_whatsapp_service.provider_name}")
    
    return _whatsapp_service
