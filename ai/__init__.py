"""
AI Module - Advanced Detection Engine
Multi-camera support, real-time processing, model management
"""

import os
import sys
from pathlib import Path

# Add ai module to path
AI_DIR = Path(__file__).parent
sys.path.insert(0, str(AI_DIR))

from .detection.advanced_detector import AdvancedSafetyDetector
from .detection.multi_camera_manager import MultiCameraManager
from .models.model_manager import ModelManager

__version__ = '2.0.0'
__all__ = [
    'AdvancedSafetyDetector',
    'MultiCameraManager',
    'ModelManager'
]
