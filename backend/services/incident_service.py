"""
Incident Management Service
Incident creation, tracking, resolution, and escalation
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class IncidentStatus(Enum):
    """Incident status enumeration"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"

class IncidentSeverity(Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentType(Enum):
    """Types of incidents"""
    MISSING_HELMET = "missing_helmet"
    OVERCROWDING = "overcrowding"
    UNSAFE_ENTRY = "unsafe_entry"
    RESTRICTED_AREA_ACCESS = "restricted_area_access"
    EQUIPMENT_VIOLATION = "equipment_violation"
    UNKNOWN = "unknown"

class IncidentManagementService:
    """Advanced incident management"""
    
    def __init__(self, db_session):
        """Initialize incident management"""
        self.db = db_session
        self.incident_cache = {}
    
    def create_incident(self, incident_type: str, severity: str, camera_id: int,
                       location: str, worker_id: int = None, 
                       message: str = None, image_url: str = None) -> Optional[str]:
        """
        Create new incident
        
        Args:
            incident_type: Type of incident
            severity: Severity level
            camera_id: Camera where detected
            location: Location name
            worker_id: Associated worker ID
            message: Incident details
            image_url: Evidence image URL
        
        Returns:
            Incident ID if created successfully
        """
        try:
            incident_id = str(uuid.uuid4())
            incident = {
                'incident_id': incident_id,
                'type': incident_type,
                'severity': severity,
                'camera_id': camera_id,
                'location': location,
                'worker_id': worker_id,
                'message': message,
                'image_url': image_url,
                'status': IncidentStatus.OPEN.value,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'acknowledged_at': None,
                'acknowledged_by': None,
                'resolved_at': None,
                'resolved_by': None,
                'resolution_notes': None,
                'impact_level': self._calculate_impact_level(severity, camera_id)
            }
            
            self.incident_cache[incident_id] = incident
            logger.info(f"Incident created: {incident_id} ({incident_type} - {severity})")
            return incident_id
            
        except Exception as e:
            logger.error(f"Error creating incident: {e}")
            return None
    
    def acknowledge_incident(self, incident_id: str, user_id: int, notes: str = None) -> bool:
        """
        Acknowledge incident (supervisor action)
        
        Args:
            incident_id: Incident ID
            user_id: User acknowledging
            notes: Optional notes
        
        Returns:
            True if successful
        """
        try:
            if incident_id not in self.incident_cache:
                logger.error(f"Incident not found: {incident_id}")
                return False
            
            incident = self.incident_cache[incident_id]
            incident['status'] = IncidentStatus.ACKNOWLEDGED.value
            incident['acknowledged_at'] = datetime.utcnow()
            incident['acknowledged_by'] = user_id
            incident['updated_at'] = datetime.utcnow()
            
            logger.info(f"Incident acknowledged: {incident_id} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging incident: {e}")
            return False
    
    def resolve_incident(self, incident_id: str, user_id: int, 
                        resolution_type: str, notes: str = None) -> bool:
        """
        Resolve incident
        
        Args:
            incident_id: Incident ID
            user_id: User resolving
            resolution_type: Type of resolution (corrected, false_positive, other)
            notes: Resolution notes
        
        Returns:
            True if successful
        """
        try:
            if incident_id not in self.incident_cache:
                logger.error(f"Incident not found: {incident_id}")
                return False
            
            incident = self.incident_cache[incident_id]
            
            if resolution_type == 'false_positive':
                incident['status'] = IncidentStatus.FALSE_POSITIVE.value
            else:
                incident['status'] = IncidentStatus.RESOLVED.value
            
            incident['resolved_at'] = datetime.utcnow()
            incident['resolved_by'] = user_id
            incident['resolution_notes'] = notes
            incident['updated_at'] = datetime.utcnow()
            
            logger.info(f"Incident resolved: {incident_id} ({resolution_type})")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving incident: {e}")
            return False
    
    def escalate_incident(self, incident_id: str, new_severity: str, reason: str) -> bool:
        """
        Escalate incident severity
        
        Args:
            incident_id: Incident ID
            new_severity: New severity level
            reason: Escalation reason
        
        Returns:
            True if successful
        """
        try:
            if incident_id not in self.incident_cache:
                logger.error(f"Incident not found: {incident_id}")
                return False
            
            incident = self.incident_cache[incident_id]
            incident['severity'] = new_severity
            incident['updated_at'] = datetime.utcnow()
            
            logger.warning(f"Incident escalated: {incident_id} to {new_severity} - {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error escalating incident: {e}")
            return False
    
    def get_incident(self, incident_id: str) -> Optional[Dict]:
        """Get incident details"""
        try:
            return self.incident_cache.get(incident_id)
        except Exception as e:
            logger.error(f"Error retrieving incident: {e}")
            return None
    
    def get_open_incidents(self, camera_id: int = None, limit: int = 100) -> List[Dict]:
        """Get all open incidents"""
        try:
            open_incidents = [
                inc for inc in self.incident_cache.values()
                if inc['status'] in [IncidentStatus.OPEN.value, IncidentStatus.ACKNOWLEDGED.value]
            ]
            
            if camera_id:
                open_incidents = [inc for inc in open_incidents if inc['camera_id'] == camera_id]
            
            return open_incidents[:limit]
            
        except Exception as e:
            logger.error(f"Error retrieving open incidents: {e}")
            return []
    
    def get_incidents_by_camera(self, camera_id: int, status: str = None, 
                               hours: int = 24) -> List[Dict]:
        """Get incidents for specific camera"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            incidents = [
                inc for inc in self.incident_cache.values()
                if inc['camera_id'] == camera_id and inc['created_at'] > cutoff_time
            ]
            
            if status:
                incidents = [inc for inc in incidents if inc['status'] == status]
            
            return incidents
            
        except Exception as e:
            logger.error(f"Error retrieving camera incidents: {e}")
            return []
    
    def get_incidents_by_worker(self, worker_id: int, 
                               hours: int = 24) -> List[Dict]:
        """Get incidents for specific worker"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            incidents = [
                inc for inc in self.incident_cache.values()
                if inc['worker_id'] == worker_id and inc['created_at'] > cutoff_time
            ]
            return incidents
            
        except Exception as e:
            logger.error(f"Error retrieving worker incidents: {e}")
            return []
    
    def get_incident_statistics(self, hours: int = 24) -> Dict:
        """Get incident statistics"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_incidents = [
                inc for inc in self.incident_cache.values()
                if inc['created_at'] > cutoff_time
            ]
            
            stats = {
                'total_incidents': len(recent_incidents),
                'by_severity': {},
                'by_type': {},
                'by_status': {},
                'by_camera': {},
                'open_incidents': 0,
                'resolved_incidents': 0,
                'false_positives': 0,
                'average_resolution_time': 0
            }
            
            for incident in recent_incidents:
                # Count by severity
                severity = incident['severity']
                stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
                
                # Count by type
                inc_type = incident['type']
                stats['by_type'][inc_type] = stats['by_type'].get(inc_type, 0) + 1
                
                # Count by status
                status = incident['status']
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                # Count by camera
                camera_id = incident['camera_id']
                stats['by_camera'][camera_id] = stats['by_camera'].get(camera_id, 0) + 1
                
                # Specific counts
                if status in [IncidentStatus.OPEN.value, IncidentStatus.ACKNOWLEDGED.value]:
                    stats['open_incidents'] += 1
                elif status == IncidentStatus.RESOLVED.value:
                    stats['resolved_incidents'] += 1
                elif status == IncidentStatus.FALSE_POSITIVE.value:
                    stats['false_positives'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def _calculate_impact_level(self, severity: str, camera_id: int) -> str:
        """Calculate impact level based on severity and camera"""
        # Simple impact calculation - can be enhanced
        severity_levels = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 1
        }
        
        # Critical areas might have higher impact
        critical_areas = [1, 2]  # Example camera IDs for critical areas
        
        base_impact = severity_levels.get(severity, 2)
        if camera_id in critical_areas:
            base_impact *= 1.5
        
        return "high" if base_impact >= 4 else ("medium" if base_impact >= 2 else "low")
    
    def mark_as_in_progress(self, incident_id: str, user_id: int) -> bool:
        """Mark incident as in progress"""
        try:
            if incident_id not in self.incident_cache:
                return False
            
            incident = self.incident_cache[incident_id]
            incident['status'] = IncidentStatus.IN_PROGRESS.value
            incident['updated_at'] = datetime.utcnow()
            
            logger.info(f"Incident marked in progress: {incident_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking incident: {e}")
            return False
    
    def bulk_update_incidents(self, incident_ids: List[str], status: str, 
                             notes: str = None) -> int:
        """Bulk update multiple incidents"""
        try:
            updated_count = 0
            for incident_id in incident_ids:
                if incident_id in self.incident_cache:
                    self.incident_cache[incident_id]['status'] = status
                    self.incident_cache[incident_id]['updated_at'] = datetime.utcnow()
                    if notes:
                        self.incident_cache[incident_id]['resolution_notes'] = notes
                    updated_count += 1
            
            logger.info(f"Bulk updated {updated_count} incidents to status {status}")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            return 0
