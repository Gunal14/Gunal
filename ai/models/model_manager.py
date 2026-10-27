"""
Model Management System
Handle model training, versioning, and switching
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ModelManager:
    """Manage detection models and versions"""
    
    def __init__(self):
        """Initialize model manager"""
        self.models = {}
        self.active_model = None
        self.model_history = []
    
    def register_model(self, model_id: str, model_config: Dict) -> bool:
        """
        Register a detection model
        
        Args:
            model_id: Unique model identifier
            model_config: Model configuration
        
        Returns:
            True if successful
        """
        try:
            model_info = {
                'id': model_id,
                'name': model_config.get('name', model_id),
                'version': model_config.get('version', '1.0'),
                'type': model_config.get('type', 'cascade'),  # cascade, ssd, yolo
                'accuracy': model_config.get('accuracy', 0.0),
                'training_date': model_config.get('training_date'),
                'status': 'active',
                'config': model_config,
                'registered_at': datetime.utcnow().isoformat()
            }
            
            self.models[model_id] = model_info
            
            if not self.active_model:
                self.set_active_model(model_id)
            
            logger.info(f"Model {model_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering model: {e}")
            return False
    
    def set_active_model(self, model_id: str) -> bool:
        """Set active model for detection"""
        if model_id not in self.models:
            logger.error(f"Model {model_id} not found")
            return False
        
        previous_model = self.active_model
        self.active_model = model_id
        
        self.model_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'from_model': previous_model,
            'to_model': model_id,
            'reason': 'Manual switch'
        })
        
        logger.info(f"Active model switched to {model_id}")
        return True
    
    def get_active_model(self) -> Optional[Dict]:
        """Get active model configuration"""
        if not self.active_model:
            return None
        return self.models.get(self.active_model)
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get information about specific model"""
        return self.models.get(model_id)
    
    def list_models(self) -> List[Dict]:
        """List all registered models"""
        return list(self.models.values())
    
    def update_model_accuracy(self, model_id: str, accuracy: float) -> bool:
        """Update model accuracy metrics"""
        if model_id not in self.models:
            return False
        
        self.models[model_id]['accuracy'] = accuracy
        logger.info(f"Model {model_id} accuracy updated to {accuracy}")
        return True
    
    def deactivate_model(self, model_id: str) -> bool:
        """Deactivate a model"""
        if model_id not in self.models:
            return False
        
        self.models[model_id]['status'] = 'inactive'
        
        if self.active_model == model_id:
            # Switch to another model
            for mid, info in self.models.items():
                if info['status'] == 'active' and mid != model_id:
                    self.set_active_model(mid)
                    break
        
        logger.info(f"Model {model_id} deactivated")
        return True
    
    def get_model_performance_history(self, model_id: str) -> List[Dict]:
        """Get performance history for model"""
        return [
            h for h in self.model_history 
            if h.get('to_model') == model_id or h.get('from_model') == model_id
        ]
    
    def export_models_config(self) -> str:
        """Export all models configuration as JSON"""
        return json.dumps({
            'models': self.models,
            'active_model': self.active_model,
            'exported_at': datetime.utcnow().isoformat()
        }, indent=2, default=str)
