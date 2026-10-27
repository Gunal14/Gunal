"""
AI Server Configuration
Advanced settings for AI inference engine
"""

import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class AIServerConfig:
    """Advanced AI Server configuration"""
    
    # ======= Core Settings =======
    ENABLE_GPU: bool = os.getenv('AI_ENABLE_GPU', 'False').lower() == 'true'
    ENABLE_ENSEMBLE: bool = os.getenv('AI_ENABLE_ENSEMBLE', 'True').lower() == 'true'
    DEVICE: str = 'cuda' if ENABLE_GPU else 'cpu'
    
    # ======= Model Settings =======
    MODEL_DIR: str = os.getenv('AI_MODEL_DIR', 'models')
    DEFAULT_MODELS: List[str] = field(default_factory=lambda: ['helmet_detector', 'person_detector'])
    MODEL_CACHE_ENABLED: bool = True
    MODEL_OPTIMIZATION_LEVEL: int = 3  # 0=none, 1=basic, 2=medium, 3=aggressive
    
    # ======= Inference Settings =======
    INFERENCE_CACHE_SIZE: int = int(os.getenv('AI_CACHE_SIZE', '1000'))
    CACHE_TTL_SECONDS: int = int(os.getenv('AI_CACHE_TTL', '300'))
    BATCH_SIZE: int = int(os.getenv('AI_BATCH_SIZE', '4'))
    MAX_QUEUE_SIZE: int = int(os.getenv('AI_MAX_QUEUE', '100'))
    
    # ======= Detection Settings =======
    CONFIDENCE_THRESHOLD: float = float(os.getenv('AI_CONFIDENCE_THRESHOLD', '0.5'))
    NMS_THRESHOLD: float = float(os.getenv('AI_NMS_THRESHOLD', '0.5'))
    MIN_DETECTION_SIZE: int = 20  # pixels
    MAX_DETECTIONS_PER_FRAME: int = 100
    
    # ======= Performance Settings =======
    NUM_WORKERS: int = int(os.getenv('AI_NUM_WORKERS', '4'))
    PREFETCH_BUFFER_SIZE: int = int(os.getenv('AI_PREFETCH_BUFFER', '32'))
    MEMORY_POOLING_ENABLED: bool = True
    ASYNC_INFERENCE_ENABLED: bool = True
    
    # ======= Monitoring Settings =======
    ENABLE_METRICS: bool = True
    METRICS_UPDATE_INTERVAL: int = 10  # seconds
    LOG_LEVEL: str = os.getenv('AI_LOG_LEVEL', 'INFO')
    ENABLE_PROFILING: bool = False
    
    # ======= API Settings =======
    API_HOST: str = os.getenv('AI_API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('AI_API_PORT', '8000'))
    API_WORKERS: int = int(os.getenv('AI_API_WORKERS', '4'))
    API_TIMEOUT: int = 30
    
    # ======= Advanced Settings =======
    ENSEMBLE_VOTING_METHOD: str = 'weighted-average'  # 'voting' or 'weighted-average'
    ENSEMBLE_WEIGHTS: dict = field(default_factory=dict)  # Custom model weights
    ADAPTIVE_THRESHOLDS_ENABLED: bool = True
    AUTO_FALLBACK_TO_CPU: bool = True
    RESOURCE_MONITORING_ENABLED: bool = True
    AUTO_RECOVERY_ENABLED: bool = True
    
    # ======= Optimization Flags =======
    USE_TENSORRT: bool = False
    USE_ONNX: bool = False
    USE_OPENVINO: bool = False
    QUANTIZATION_ENABLED: bool = False
    MIXED_PRECISION_ENABLED: bool = False
    
    def __post_init__(self):
        """Validate configuration"""
        if self.CONFIDENCE_THRESHOLD < 0 or self.CONFIDENCE_THRESHOLD > 1:
            raise ValueError("CONFIDENCE_THRESHOLD must be between 0 and 1")
        
        if self.NMS_THRESHOLD < 0 or self.NMS_THRESHOLD > 1:
            raise ValueError("NMS_THRESHOLD must be between 0 and 1")
        
        if not os.path.exists(self.MODEL_DIR):
            os.makedirs(self.MODEL_DIR, exist_ok=True)
    
    def to_dict(self):
        """Convert config to dictionary"""
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('_')
        }


# Default configuration instance
config = AIServerConfig()
