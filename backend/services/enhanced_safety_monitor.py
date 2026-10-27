"""
Enhanced Safety Monitoring Service with Employee Recognition
Integrates facial recognition, compliance tracking, and automated notifications
"""

import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedSafetyMonitor:
    """Enhanced safety monitoring with employee recognition and notifications"""

    def __init__(self, db_session, employee_service, notification_service,
                 whatsapp_service=None, alert_cooldown=300):
        """
        Initialize enhanced safety monitor

        Args:
            db_session: Database session
            employee_service: Employee service instance
            notification_service: Notification service instance
            whatsapp_service: WhatsApp service instance (optional)
            alert_cooldown: Cooldown between alerts (seconds)
        """
        self.db = db_session
        self.employee_service = employee_service
        self.notification_service = notification_service
        self.whatsapp_service = whatsapp_service
        self.alert_cooldown = alert_cooldown

        # Alert tracking
        self.recent_alerts = {}  # employee_id -> last_alert_time

        # Create snapshots directory
        self.snapshots_dir = Path('static/snapshots')
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def process_frame(self, frame, camera_id=None, location=None) -> Dict:
        """
        Process frame with employee recognition and compliance checking

        Args:
            frame: Video frame
            camera_id: Camera identifier
            location: Location description

        Returns:
            Processing results
        """
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'camera_id': camera_id,
            'location': location,
            'recognized_employees': [],
            'violations': [],
            'alerts_sent': []
        }

        try:
            # Recognize employees in frame
            recognized_employees = self.employee_service.recognize_employee(frame)

            results['recognized_employees'] = recognized_employees

            # Process each recognized employee
            for employee_data in recognized_employees:
                violations = self._process_employee_compliance(
                    employee_data, frame, camera_id, location
                )

                if violations:
                    results['violations'].extend(violations)

                    # Send alerts for violations
                    alerts = self._send_employee_alerts(
                        employee_data, violations, frame, camera_id, location
                    )
                    results['alerts_sent'].extend(alerts)

            # Log recognition events
            self._log_recognition_events(recognized_employees, camera_id, location)

        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            results['error'] = str(e)

        return results

    def _process_employee_compliance(self, employee_data: Dict, frame,
                                   camera_id: int, location: str) -> List[Dict]:
        """
        Process compliance for recognized employee

        Args:
            employee_data: Employee recognition data
            frame: Video frame
            camera_id: Camera ID
            location: Location

        Returns:
            List of violations
        """
        violations = []

        try:
            employee_id = employee_data['employee_id']
            compliance = employee_data.get('compliance', {})

            if compliance.get('status') == 'non_compliant':
                violation_data = {
                    'employee_id': employee_id,
                    'employee_name': employee_data['name'],
                    'violations': compliance.get('violations', []),
                    'camera_id': camera_id,
                    'location': location,
                    'timestamp': datetime.utcnow(),
                    'severity': self._calculate_violation_severity(compliance['violations'])
                }

                violations.append(violation_data)

                # Update employee violation count
                self._update_employee_violations(employee_id)

        except Exception as e:
            logger.error(f"Error processing employee compliance: {e}")

        return violations

    def _calculate_violation_severity(self, violations: List[str]) -> str:
        """Calculate violation severity"""
        if 'missing_helmet' in violations:
            return 'HIGH'  # Helmet violations are critical
        elif len(violations) > 1:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _update_employee_violations(self, employee_id: str):
        """Update employee violation statistics"""
        try:
            from backend.database.models import Employee

            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if employee:
                employee.total_violations += 1
                employee.compliance_score = self._calculate_compliance_score(employee)
                self.db.session.commit()

        except Exception as e:
            logger.error(f"Error updating employee violations: {e}")

    def _calculate_compliance_score(self, employee) -> float:
        """Calculate employee compliance score"""
        try:
            from backend.database.models import EmployeeRecognition

            # Get recent recognitions (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recognitions = EmployeeRecognition.query.filter(
                EmployeeRecognition.employee_id == employee.employee_id,
                EmployeeRecognition.timestamp >= thirty_days_ago
            ).all()

            if not recognitions:
                return 0.0

            compliant_count = sum(1 for r in recognitions if r.compliance_status == 'compliant')
            return (compliant_count / len(recognitions)) * 100

        except Exception as e:
            logger.error(f"Error calculating compliance score: {e}")
            return 0.0

    def _send_employee_alerts(self, employee_data: Dict, violations: List[Dict],
                            frame, camera_id: int, location: str) -> List[Dict]:
        """
        Send alerts to employee and emergency contacts

        Args:
            employee_data: Employee data
            violations: Violation details
            frame: Video frame for snapshot
            camera_id: Camera ID
            location: Location

        Returns:
            List of sent alerts
        """
        sent_alerts = []

        try:
            employee_id = employee_data['employee_id']

            # Check alert cooldown
            last_alert = self.recent_alerts.get(employee_id)
            if last_alert and (datetime.utcnow() - last_alert).total_seconds() < self.alert_cooldown:
                return sent_alerts

            # Get employee details
            employee = self.employee_service._get_employee_by_id(employee_id)
            if not employee:
                return sent_alerts

            # Create snapshot
            snapshot_path = self._save_snapshot(frame, employee_id, violations[0]['violations'])

            # Create incident log
            incident = self._create_incident_log(employee, violations[0], camera_id, location, snapshot_path)

            # Send alerts
            for violation_data in violations:
                alert_data = self._send_alert(employee, violation_data, incident, snapshot_path)
                if alert_data:
                    sent_alerts.append(alert_data)

            # Update alert cooldown
            self.recent_alerts[employee_id] = datetime.utcnow()

        except Exception as e:
            logger.error(f"Error sending employee alerts: {e}")

        return sent_alerts

    def _save_snapshot(self, frame, employee_id: str, violations: List[str]) -> str:
        """Save snapshot of violation"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"violation_{employee_id}_{timestamp}.jpg"
            filepath = self.snapshots_dir / filename

            cv2.imwrite(str(filepath), frame)
            return str(filepath)

        except Exception as e:
            logger.error(f"Error saving snapshot: {e}")
            return None

    def _create_incident_log(self, employee, violation_data: Dict,
                           camera_id: int, location: str, snapshot_path: str):
        """Create incident log entry"""
        try:
            from backend.database.models import IncidentLog

            incident = IncidentLog(
                incident_type='SAFETY_VIOLATION',
                severity=violation_data['severity'],
                camera_id=camera_id,
                location=location,
                worker_id=employee.employee_id,
                details={
                    'violations': violation_data['violations'],
                    'employee_name': employee.name,
                    'department': employee.department,
                    'snapshot_path': snapshot_path
                },
                description=f"Safety violation detected for {employee.name}: {', '.join(violation_data['violations'])}"
            )

            self.db.session.add(incident)
            self.db.session.commit()

            return incident

        except Exception as e:
            logger.error(f"Error creating incident log: {e}")
            return None

    def _send_alert(self, employee, violation_data: Dict, incident, snapshot_path: str) -> Dict:
        """Send alert via available channels"""
        try:
            alert_message = self._generate_alert_message(employee, violation_data)

            alert_data = {
                'employee_id': employee.employee_id,
                'alert_type': 'safety_violation',
                'severity': violation_data['severity'],
                'message': alert_message,
                'channels': []
            }

            # Send email to employee
            if employee.email:
                success = self.notification_service.send_email_alert(
                    employee.email,
                    f"Safety Violation Alert - {employee.name}",
                    alert_message,
                    violation_data['severity']
                )
                if success:
                    alert_data['channels'].append('email')

            # Send SMS to employee
            if employee.phone:
                success = self.notification_service.send_sms_alert(
                    employee.phone,
                    f"SAFETY ALERT: {alert_message[:100]}..."
                )
                if success:
                    alert_data['channels'].append('sms')

            # Send WhatsApp to employee
            if employee.phone and self.whatsapp_service:
                # Format phone number for WhatsApp
                whatsapp_number = employee.phone.replace('+', '').replace('-', '').replace(' ', '')
                if employee.phone.startswith('+'):
                    whatsapp_number = employee.phone[1:]

                success = self.whatsapp_service.send_message({
                    'recipient': whatsapp_number,
                    'message': alert_message,
                    'type': 'safety_alert'
                })
                if success:
                    alert_data['channels'].append('whatsapp')

            # Send to emergency contacts
            emergency_alerts = self._send_emergency_alerts(employee, violation_data, alert_message)
            alert_data['emergency_contacts_alerted'] = len(emergency_alerts)

            # Log safety alert
            self._log_safety_alert(employee, violation_data, alert_data)

            return alert_data

        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return None

    def _generate_alert_message(self, employee, violation_data: Dict) -> str:
        """Generate alert message"""
        violations = violation_data['violations']
        violation_text = ', '.join(violations).replace('_', ' ').title()

        message = f"""
SAFETY VIOLATION ALERT

Employee: {employee.name}
ID: {employee.employee_id}
Department: {employee.department or 'N/A'}

Violation: {violation_text}
Location: {violation_data.get('location', 'Unknown')}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

Please ensure compliance with all safety protocols immediately.

This is an automated safety monitoring alert.
"""

        return message.strip()

    def _send_emergency_alerts(self, employee, violation_data: Dict, message: str) -> List[Dict]:
        """Send alerts to emergency contacts"""
        alerts_sent = []

        try:
            from backend.database.models import EmergencyContact

            # Get emergency contacts for this employee
            # Note: This assumes emergency contacts are linked to users, not directly to employees
            # You may need to adjust this based on your user-employee relationship

            contacts = EmergencyContact.query.filter_by(
                user_id=employee.id if hasattr(employee, 'id') else None,
                is_active=True
            ).all()

            for contact in contacts:
                # Check if contact should receive this severity level
                severity = violation_data['severity'].lower()
                should_receive = getattr(contact, f'alert_{severity}', False)

                if should_receive:
                    alert_info = self._send_emergency_contact_alert(contact, message)
                    if alert_info:
                        alerts_sent.append(alert_info)

        except Exception as e:
            logger.error(f"Error sending emergency alerts: {e}")

        return alerts_sent

    def _send_emergency_contact_alert(self, contact, message: str) -> Dict:
        """Send alert to emergency contact"""
        try:
            alert_info = {
                'contact_name': contact.contact_name,
                'channels': []
            }

            # Send email
            if contact.email_enabled and contact.email:
                success = self.notification_service.send_email_alert(
                    contact.email,
                    "Emergency Safety Alert",
                    message,
                    "HIGH"
                )
                if success:
                    alert_info['channels'].append('email')

            # Send SMS
            if contact.sms_enabled and contact.phone_number:
                success = self.notification_service.send_sms_alert(
                    contact.phone_number,
                    f"EMERGENCY ALERT: {message[:100]}..."
                )
                if success:
                    alert_info['channels'].append('sms')

            # Send WhatsApp
            if contact.whatsapp_enabled and contact.phone_number and self.whatsapp_service:
                whatsapp_number = contact.phone_number.replace('+', '').replace('-', '').replace(' ', '')
                if contact.phone_number.startswith('+'):
                    whatsapp_number = contact.phone_number[1:]

                success = self.whatsapp_service.send_message({
                    'recipient': whatsapp_number,
                    'message': message,
                    'type': 'emergency_alert'
                })
                if success:
                    alert_info['channels'].append('whatsapp')

            return alert_info if alert_info['channels'] else None

        except Exception as e:
            logger.error(f"Error sending emergency contact alert: {e}")
            return None

    def _log_safety_alert(self, employee, violation_data: Dict, alert_data: Dict):
        """Log safety alert"""
        try:
            from backend.database.models import SafetyAlert

            alert = SafetyAlert(
                employee_id=employee.employee_id,
                alert_type='safety_violation',
                severity=violation_data['severity'],
                message=alert_data['message'],
                location=violation_data.get('location'),
                sent_to_employee='email' in alert_data.get('channels', []),
                sent_to_emergency_contacts=alert_data.get('emergency_contacts_alerted', 0) > 0,
                email_sent='email' in alert_data.get('channels', []),
                sms_sent='sms' in alert_data.get('channels', []),
                whatsapp_sent='whatsapp' in alert_data.get('channels', []),
                sent_at=datetime.utcnow()
            )

            self.db.session.add(alert)
            self.db.session.commit()

        except Exception as e:
            logger.error(f"Error logging safety alert: {e}")

    def _log_recognition_events(self, recognized_employees: List[Dict],
                              camera_id: int, location: str):
        """Log employee recognition events"""
        try:
            from backend.database.models import EmployeeRecognition

            for employee_data in recognized_employees:
                recognition = EmployeeRecognition(
                    employee_id=employee_data['employee_id'],
                    camera_id=camera_id,
                    location=location,
                    confidence_score=employee_data['confidence'],
                    face_location=employee_data['face_location'],
                    helmet_detected=employee_data.get('compliance', {}).get('helmet_compliant', False),
                    compliance_status=employee_data.get('compliance', {}).get('status', 'unknown'),
                    violations=employee_data.get('compliance', {}).get('violations', [])
                )

                self.db.session.add(recognition)

            self.db.session.commit()

        except Exception as e:
            logger.error(f"Error logging recognition events: {e}")