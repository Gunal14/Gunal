"""
Backend Routes Module
Exports all route blueprints
"""

from .auth import auth_bp, init_auth_routes
from .incidents import incidents_bp, init_incident_routes
from .analytics import analytics_bp, init_analytics_routes
from .monitoring import monitoring_bp, init_monitoring_routes
from .emergency_contacts_api import init_emergency_routes

__all__ = [
    'auth_bp',
    'incidents_bp', 
    'analytics_bp',
    'monitoring_bp',
    'init_auth_routes',
    'init_incident_routes',
    'init_analytics_routes',
    'init_monitoring_routes',
    'init_emergency_routes'
]
