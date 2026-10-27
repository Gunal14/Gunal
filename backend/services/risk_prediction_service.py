"""
Advanced Risk Prediction Engine
Context-aware risk scoring with environmental factors and behavioral analysis
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class RiskSeverity(Enum):
    """Risk severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskCategory(Enum):
    """Risk categories for classification"""
    PPE = "PPE"  # Personal Protective Equipment
    POSTURE = "POSTURE"  # Body position/ergonomics
    BEHAVIOR = "BEHAVIOR"  # Unsafe actions
    HAZMAT = "HAZMAT"  # Hazardous materials exposure
    FATIGUE = "FATIGUE"  # Worker fatigue detection
    ENVIRONMENT = "ENVIRONMENT"  # Environmental hazards


@dataclass
class RiskContext:
    """Context for risk assessment"""
    time_of_day: str  # morning, afternoon, night
    location_hazard_level: str  # LOW, MEDIUM, HIGH
    shift_type: str  # morning, afternoon, night
    environmental_conditions: Dict = None  # lighting, temperature, etc.
    nearby_hazards: List[str] = None
    worker_fatigue_level: float = 0.5  # 0-1 scale
    previous_violations: int = 0


@dataclass
class DetectionData:
    """Detection result from AI model"""
    object_type: str  # helmet, person, ppe, etc.
    confidence: float  # 0-1
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    attributes: Dict = None  # Additional attributes


class ContextualRiskScorer:
    """
    Context-aware risk scoring using multiple factors:
    - Detection confidence
    - Location hazard level
    - Time of day/shift
    - Worker history
    - Environmental conditions
    - Previous violations
    """
    
    # Base risk weights
    CONFIDENCE_WEIGHT = 1.0
    HAZARD_LEVEL_WEIGHT = 1.2  # Location hazard amplifies risk
    TIME_OF_DAY_WEIGHT = 0.8  # Fatigue higher at certain times
    WORKER_HISTORY_WEIGHT = 0.5  # Previous violations indicate higher risk
    ENVIRONMENTAL_WEIGHT = 1.1
    
    # Risk escalation factors
    REPEATED_VIOLATION_MULTIPLIER = 1.5  # Risk increases if repeated
    CRITICAL_AREA_MULTIPLIER = 2.0  # High hazard areas increase risk
    NIGHT_SHIFT_MULTIPLIER = 1.3  # Higher risk at night
    
    # Base risk scores for different violations (0-100)
    BASE_RISK_SCORES = {
        'not_wearing_helmet': 85,
        'improper_helmet_fit': 65,
        'no_safety_vest': 75,
        'missing_ppe': 70,
        'improper_posture': 40,
        'near_hazard': 60,
        'hazmat_exposure': 95,
        'fatigue_detected': 45,
        'unsafe_behavior': 55,
    }
    
    def __init__(self):
        """Initialize risk scorer"""
        self.violation_history = {}
        self.location_hazard_cache = {}
    
    def score_risk(self,
                   violation_type: str,
                   detection_confidence: float,
                   risk_context: RiskContext,
                   detection_count: int = 1) -> Tuple[float, RiskSeverity]:
        """
        Calculate contextualized risk score
        
        Args:
            violation_type: Type of violation detected
            detection_confidence: AI model confidence (0-1)
            risk_context: Context information for risk assessment
            detection_count: Number of times detected in time window
        
        Returns:
            Tuple of (risk_score: 0-100, severity: RiskSeverity)
        """
        
        # Get base risk score
        base_score = self.BASE_RISK_SCORES.get(violation_type, 50)
        
        # Start with confidence-weighted base score
        risk_score = base_score * detection_confidence
        
        # Apply hazard level multiplier
        if risk_context.location_hazard_level == "HIGH":
            risk_score *= self.CRITICAL_AREA_MULTIPLIER
        elif risk_context.location_hazard_level == "MEDIUM":
            risk_score *= 1.5
        # LOW area: no multiplier
        
        # Apply time-of-day risk (fatigue factor)
        if risk_context.time_of_day == "night":
            risk_score *= self.NIGHT_SHIFT_MULTIPLIER
        elif risk_context.time_of_day == "morning":
            risk_score *= 1.1  # Slight increase for first shift
        
        # Repeated violation escalation
        if detection_count > 3:
            risk_score *= min(self.REPEATED_VIOLATION_MULTIPLIER, 1 + (detection_count * 0.1))
        
        # Worker history amplification
        if risk_context.previous_violations > 0:
            violation_multiplier = 1 + (min(risk_context.previous_violations, 5) * 0.2)
            risk_score *= min(violation_multiplier, 1.8)
        
        # Environmental conditions
        if risk_context.environmental_conditions:
            risk_score = self._apply_environmental_factors(
                risk_score,
                risk_context.environmental_conditions
            )
        
        # Worker fatigue factor
        if risk_context.worker_fatigue_level > 0.7:
            risk_score *= 1.2
        
        # Cap score at 100
        risk_score = min(risk_score, 100)
        
        # Determine severity level
        severity = self._score_to_severity(risk_score)
        
        return risk_score, severity
    
    def _apply_environmental_factors(self, base_score: float,
                                     conditions: Dict) -> float:
        """Apply environmental condition factors to risk score"""
        
        score = base_score
        
        # Poor lighting increases risk
        if conditions.get('lighting', 'good') == 'poor':
            score *= 1.15
        
        # Weather conditions
        weather = conditions.get('weather', 'clear')
        if weather == 'rain':
            score *= 1.1
        elif weather == 'snow':
            score *= 1.2
        
        # Temperature extremes
        temp = conditions.get('temperature', 20)
        if temp < 0 or temp > 40:
            score *= 1.1
        
        # Air quality
        if conditions.get('air_quality', 'good') == 'poor':
            score *= 1.2
        
        return score
    
    def _score_to_severity(self, score: float) -> RiskSeverity:
        """Convert numeric score to severity level"""
        
        if score < 25:
            return RiskSeverity.LOW
        elif score < 50:
            return RiskSeverity.MEDIUM
        elif score < 75:
            return RiskSeverity.HIGH
        else:
            return RiskSeverity.CRITICAL
    
    def detect_violation_pattern(self, violations: List[Dict]) -> Dict:
        """
        Detect violation patterns (repeated violations, escalation, etc.)
        
        Args:
            violations: List of recent violations
        
        Returns:
            Pattern analysis with escalation flags
        """
        
        if not violations:
            return {'pattern_detected': False}
        
        # Group by type
        violation_counts = {}
        for v in violations:
            v_type = v.get('type', 'unknown')
            violation_counts[v_type] = violation_counts.get(v_type, 0) + 1
        
        # Check for patterns
        most_common = max(violation_counts.items(), key=lambda x: x[1])
        pattern_detected = most_common[1] >= 3  # 3+ of same type = pattern
        
        return {
            'pattern_detected': pattern_detected,
            'most_common_violation': most_common[0],
            'frequency': most_common[1],
            'violation_types': list(violation_counts.keys()),
            'escalation_risk': pattern_detected and most_common[1] >= 5,
            'recommendation': self._get_escalation_recommendation(
                most_common[0],
                most_common[1]
            )
        }
    
    def _get_escalation_recommendation(self, violation_type: str, count: int) -> str:
        """Get escalation recommendation based on pattern"""
        
        if count >= 5:
            return "CRITICAL: Immediate intervention required"
        elif count >= 3:
            return "HIGH: Notify supervisor immediately"
        elif count >= 2:
            return "MEDIUM: Schedule safety review"
        else:
            return "LOW: Monitor for pattern development"


class MultiFactorRiskAssessor:
    """
    Multi-factor risk assessment combining:
    - Detection-based risks (from AI model)
    - Context-based risks (location, time, worker history)
    - Pattern-based risks (repeated violations)
    - Environmental risks
    """
    
    def __init__(self):
        """Initialize assessor"""
        self.scorer = ContextualRiskScorer()
        self.violation_window = timedelta(hours=8)  # Track violations in 8-hour window
        self.worker_violations = {}  # Track worker violation history
    
    def assess_risk(self,
                    detection_result: Dict,
                    risk_context: RiskContext) -> Dict:
        """
        Comprehensive risk assessment
        
        Args:
            detection_result: Detection from AI model
            risk_context: Context for assessment
        
        Returns:
            Dict with complete risk assessment
        """
        
        violation_type = detection_result.get('type', 'unknown')
        confidence = detection_result.get('confidence', 0.5)
        detection_count = detection_result.get('detection_count', 1)
        worker_id = detection_result.get('worker_id')
        
        # Get detection-based risk
        risk_score, severity = self.scorer.score_risk(
            violation_type,
            confidence,
            risk_context,
            detection_count
        )
        
        # Check for pattern
        worker_violations = self.worker_violations.get(worker_id, [])
        pattern = self.scorer.detect_violation_pattern(worker_violations)
        
        # Adjust score if pattern detected
        if pattern.get('pattern_detected'):
            risk_score = min(risk_score * 1.3, 100)  # Increase by 30% if pattern
            if pattern.get('escalation_risk'):
                severity = RiskSeverity.CRITICAL
        
        # Determine action required
        action = self._determine_action(severity, risk_score, pattern)
        
        return {
            'violation_type': violation_type,
            'risk_score': round(risk_score, 2),
            'severity': severity.value,
            'confidence': confidence,
            'action_required': action,
            'pattern': pattern,
            'recommendation': action.get('recommendation'),
            'escalation_level': action.get('escalation_level'),
            'notify_channels': action.get('notify_channels'),
            'context': {
                'location_hazard': risk_context.location_hazard_level,
                'time_of_day': risk_context.time_of_day,
                'worker_history': risk_context.previous_violations,
                'shift_type': risk_context.shift_type,
            }
        }
    
    def _determine_action(self, severity: RiskSeverity, score: float,
                         pattern: Dict) -> Dict:
        """Determine required action based on risk assessment"""
        
        if severity == RiskSeverity.CRITICAL:
            return {
                'action_needed': True,
                'escalation_level': 3,  # Highest
                'notify_channels': ['email', 'sms', 'whatsapp'],  # All channels
                'recommendation': 'CRITICAL: Emergency response required - Notify all emergency contacts immediately',
                'response_time_sla_minutes': 2,
            }
        elif severity == RiskSeverity.HIGH:
            return {
                'action_needed': True,
                'escalation_level': 2,
                'notify_channels': ['email', 'sms'],  # Email + SMS
                'recommendation': 'HIGH RISK: Contact supervisor and safety manager',
                'response_time_sla_minutes': 5,
            }
        elif severity == RiskSeverity.MEDIUM:
            return {
                'action_needed': True,
                'escalation_level': 1,
                'notify_channels': ['email'],  # Email only
                'recommendation': 'MEDIUM RISK: Log incident and monitor for escalation',
                'response_time_sla_minutes': 15,
            }
        else:  # LOW
            return {
                'action_needed': False,
                'escalation_level': 0,
                'notify_channels': [],
                'recommendation': 'LOW RISK: Log for records',
                'response_time_sla_minutes': 60,
            }
    
    def update_worker_violations(self, worker_id: str, violation: Dict):
        """Track worker violations for pattern detection"""
        
        if worker_id not in self.worker_violations:
            self.worker_violations[worker_id] = []
        
        # Add timestamp if not present
        if 'timestamp' not in violation:
            violation['timestamp'] = datetime.utcnow()
        
        self.worker_violations[worker_id].append(violation)
        
        # Clean old violations outside window
        cutoff_time = datetime.utcnow() - self.violation_window
        self.worker_violations[worker_id] = [
            v for v in self.worker_violations[worker_id]
            if v.get('timestamp', datetime.utcnow()) > cutoff_time
        ]
    
    def get_worker_risk_profile(self, worker_id: str) -> Dict:
        """Get comprehensive risk profile for a worker"""
        
        violations = self.worker_violations.get(worker_id, [])
        
        if not violations:
            return {
                'worker_id': worker_id,
                'risk_level': 'LOW',
                'total_violations': 0,
                'violation_types': [],
            }
        
        # Analyze violations
        violation_types = {}
        high_risk_count = 0
        
        for v in violations:
            v_type = v.get('type', 'unknown')
            violation_types[v_type] = violation_types.get(v_type, 0) + 1
            
            if v.get('severity', 'LOW') in ['HIGH', 'CRITICAL']:
                high_risk_count += 1
        
        # Determine risk level
        if high_risk_count >= 3 or len(violations) >= 10:
            risk_level = 'CRITICAL'
        elif high_risk_count >= 2 or len(violations) >= 5:
            risk_level = 'HIGH'
        elif len(violations) >= 2:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'worker_id': worker_id,
            'risk_level': risk_level,
            'total_violations': len(violations),
            'high_risk_violations': high_risk_count,
            'violation_types': violation_types,
            'last_violation': violations[-1].get('timestamp') if violations else None,
            'violation_frequency': len(violations) / (self.violation_window.total_seconds() / 3600),
        }


class RiskPredictionEngine:
    """
    Main risk prediction engine orchestrating:
    - Detection result analysis
    - Context evaluation
    - Multi-factor assessment
    - Pattern detection
    - Action determination
    """
    
    def __init__(self):
        """Initialize engine"""
        self.assessor = MultiFactorRiskAssessor()
        self.location_configs = {}  # Cache location hazard levels
    
    def predict_risk(self,
                    detection: Dict,
                    location_id: str,
                    worker_id: Optional[str] = None) -> Dict:
        """
        Predict risk for a detection
        
        Args:
            detection: Detection result from AI model
            location_id: Location/camera identifier
            worker_id: Identifier of affected worker if known
        
        Returns:
            Risk prediction with all assessment data
        """
        
        # Build risk context
        context = self._build_risk_context(location_id, worker_id)
        
        # Add detection data
        detection['worker_id'] = worker_id
        
        # Get assessment
        assessment = self.assessor.assess_risk(detection, context)
        
        # Update worker history if applicable
        if worker_id:
            self.assessor.update_worker_violations(
                worker_id,
                {
                    'type': detection.get('type'),
                    'severity': assessment.get('severity'),
                    'timestamp': datetime.utcnow(),
                }
            )
        
        return assessment
    
    def _build_risk_context(self, location_id: str,
                           worker_id: Optional[str]) -> RiskContext:
        """Build context for risk assessment"""
        
        # Determine time of day
        hour = datetime.utcnow().hour
        if 6 <= hour < 14:
            time_of_day = 'morning'
        elif 14 <= hour < 22:
            time_of_day = 'afternoon'
        else:
            time_of_day = 'night'
        
        # Get location hazard level (default: MEDIUM)
        location_hazard = self.location_configs.get(location_id, {}).get('hazard_level', 'MEDIUM')
        
        # Get worker history
        worker_violations = 0
        worker_fatigue = 0.5
        if worker_id:
            profile = self.assessor.get_worker_risk_profile(worker_id)
            worker_violations = profile.get('high_risk_violations', 0)
            # Fatigue increases with time and violations
            worker_fatigue = min(0.3 + (len(profile.get('violation_types', [])) * 0.1), 1.0)
        
        return RiskContext(
            time_of_day=time_of_day,
            location_hazard_level=location_hazard,
            shift_type=time_of_day,
            environmental_conditions=self._get_environmental_conditions(),
            nearby_hazards=self.location_configs.get(location_id, {}).get('hazards', []),
            worker_fatigue_level=worker_fatigue,
            previous_violations=worker_violations,
        )
    
    def _get_environmental_conditions(self) -> Dict:
        """Get current environmental conditions (integration point)"""
        # This would integrate with real environmental sensors
        return {
            'lighting': 'good',
            'weather': 'clear',
            'temperature': 22,
            'air_quality': 'good',
        }
    
    def set_location_config(self, location_id: str, config: Dict):
        """Configure location hazard levels"""
        self.location_configs[location_id] = config


# Global instance
risk_engine = RiskPredictionEngine()
