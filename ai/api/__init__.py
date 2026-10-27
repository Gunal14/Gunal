"""
AI API Module
Advanced REST API endpoints for AI inference server
"""

from .ai_server import (
    AdvancedAIServer,
    AdvancedInferenceEngine,
    AdvancedModelManager,
    AdvancedCache,
    PriorityInferenceQueue,
    InferenceResult,
    DetectionResult,
    ModelMetrics
)
from .config import AIServerConfig, config

__version__ = '2.0.0'
__all__ = [
    'AdvancedAIServer',
    'AdvancedInferenceEngine',
    'AdvancedModelManager',
    'AdvancedCache',
    'PriorityInferenceQueue',
    'InferenceResult',
    'DetectionResult',
    'ModelMetrics',
    'AIServerConfig',
    'config',
]
