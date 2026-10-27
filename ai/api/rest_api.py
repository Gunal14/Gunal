"""
FastAPI REST API for Advanced AI Server
Production-grade REST endpoints with swagger documentation
"""

import asyncio
import logging
import base64
from typing import List, Optional
from io import BytesIO

import numpy as np
import cv2

try:
    from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
    from fastapi.responses import JSONResponse, StreamingResponse
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from .ai_server import AdvancedAIServer, InferenceResult

logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC REQUEST/RESPONSE MODELS
# ============================================================================

class DetectionItem(BaseModel):
    """Detection result item"""
    class_name: str
    confidence: float
    bbox: List[int]  # x1, y1, x2, y2
    detection_id: str


class DetectionResponse(BaseModel):
    """Detection response"""
    frame_id: str
    camera_id: int
    timestamp: float
    detections: List[DetectionItem]
    processing_time_ms: float
    model_version: str
    confidence_scores: dict


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    uptime_seconds: float
    models_active: int
    models_total: int


class ModelRegisterRequest(BaseModel):
    """Model registration request"""
    model_name: str
    model_path: str
    model_type: str = "yolo"
    version: str = "1.0"


class ModelListResponse(BaseModel):
    """Model list response"""
    models: List[str]
    active: List[str]


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

class AIServerAPI:
    """FastAPI REST API wrapper for AdvancedAIServer"""
    
    def __init__(self, enable_gpu: bool = False):
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI not installed. Install with: pip install fastapi uvicorn")
        
        self.app = FastAPI(
            title="Advanced AI Safety Detection Server",
            description="Production-grade AI inference API",
            version="2.0.0"
        )
        
        self.ai_server = AdvancedAIServer(enable_gpu=enable_gpu)
        
        # Setup routes
        self._setup_routes()
        
        logger.info("AIServerAPI initialized")
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        # Health endpoints
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            status = self.ai_server.get_health_status()
            return HealthResponse(
                status=status['status'],
                uptime_seconds=status['uptime_seconds'],
                models_active=status['models_active'],
                models_total=status['models_total']
            )
        
        @self.app.get("/health/detailed")
        async def health_detailed():
            """Detailed health check"""
            return self.ai_server.get_health_status()
        
        # Detection endpoints
        @self.app.post("/detect", response_model=DetectionResponse)
        async def detect(
            file: UploadFile = File(...),
            camera_id: int = 0
        ):
            """Detect objects in uploaded image"""
            try:
                # Read image
                contents = await file.read()
                nparr = np.frombuffer(contents, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid image file"
                    )
                
                # Run inference
                result = await self.ai_server.detect(frame, camera_id)
                
                if result is None:
                    raise HTTPException(
                        status_code=500,
                        detail="Inference failed"
                    )
                
                # Format response
                detections = [
                    DetectionItem(**det) 
                    for det in result['detections']
                ]
                
                return DetectionResponse(
                    frame_id=result['frame_id'],
                    camera_id=result['camera_id'],
                    timestamp=result['timestamp'],
                    detections=detections,
                    processing_time_ms=result['processing_time_ms'],
                    model_version=result['model_version'],
                    confidence_scores=result['confidence_scores']
                )
            
            except Exception as e:
                logger.error(f"Detection error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/detect/base64")
        async def detect_base64(
            image_base64: str,
            camera_id: int = 0
        ):
            """Detect objects from base64 encoded image"""
            try:
                # Decode base64
                image_data = base64.b64decode(image_base64)
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    raise HTTPException(status_code=400, detail="Invalid image")
                
                # Run inference
                result = await self.ai_server.detect(frame, camera_id)
                
                return result or {}
            
            except Exception as e:
                logger.error(f"Base64 detection error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/detect/batch")
        async def detect_batch(
            files: List[UploadFile] = File(...),
            camera_id: int = 0
        ):
            """Batch detection on multiple images"""
            try:
                frames = []
                
                # Read all images
                for file in files:
                    contents = await file.read()
                    nparr = np.frombuffer(contents, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        frames.append(frame)
                
                if not frames:
                    raise HTTPException(status_code=400, detail="No valid images")
                
                # Batch inference
                results = await self.ai_server.detect_batch(frames, camera_id)
                
                return {
                    'batch_size': len(results),
                    'results': results
                }
            
            except Exception as e:
                logger.error(f"Batch detection error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Model management endpoints
        @self.app.post("/models/register")
        async def register_model(request: ModelRegisterRequest):
            """Register a new model"""
            try:
                success = self.ai_server.register_model(
                    request.model_name,
                    request.model_path,
                    request.model_type,
                    request.version
                )
                
                return {
                    'success': success,
                    'model_name': request.model_name,
                    'version': request.version
                }
            
            except Exception as e:
                logger.error(f"Model registration error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/models/{model_name}/activate")
        async def activate_model(model_name: str):
            """Activate a model"""
            success = self.ai_server.activate_model(model_name)
            
            return {
                'success': success,
                'model_name': model_name,
                'action': 'activate'
            }
        
        @self.app.post("/models/{model_name}/deactivate")
        async def deactivate_model(model_name: str):
            """Deactivate a model"""
            success = self.ai_server.deactivate_model(model_name)
            
            return {
                'success': success,
                'model_name': model_name,
                'action': 'deactivate'
            }
        
        @self.app.get("/models", response_model=ModelListResponse)
        async def list_models():
            """List all models"""
            info = self.ai_server.get_model_info()
            
            return ModelListResponse(
                models=list(info.keys()),
                active=self.ai_server.model_manager.active_models
            )
        
        @self.app.get("/models/{model_name}")
        async def get_model_info(model_name: str):
            """Get specific model information"""
            info = self.ai_server.get_model_info(model_name)
            
            if not info:
                raise HTTPException(status_code=404, detail="Model not found")
            
            return info
        
        # Metrics endpoints
        @self.app.get("/metrics")
        async def get_metrics():
            """Get server metrics"""
            metrics = self.ai_server.inference_engine.get_metrics()
            
            return {
                'inference_time_ms': metrics.inference_time_ms,
                'throughput_fps': metrics.throughput_fps,
                'memory_usage_mb': metrics.memory_usage_mb,
                'gpu_utilization': metrics.gpu_utilization,
                'cache_hit_rate': metrics.cache_hit_rate,
                'error_count': metrics.error_count,
                'total_inferences': metrics.total_inferences
            }
        
        @self.app.get("/metrics/cache")
        async def get_cache_metrics():
            """Get cache metrics"""
            cache = self.ai_server.inference_engine.cache
            
            return {
                'hit_rate': cache.get_hit_rate(),
                'hits': cache.hits,
                'misses': cache.misses,
                'size': len(cache.cache),
                'max_size': cache.max_size
            }
        
        @self.app.get("/metrics/queue")
        async def get_queue_metrics():
            """Get queue metrics"""
            return self.ai_server.inference_engine.queue.get_stats()
        
        # WebSocket endpoint
        @self.app.websocket("/ws/stream/{camera_id}")
        async def websocket_endpoint(websocket: WebSocket, camera_id: int):
            """WebSocket endpoint for real-time streaming"""
            await websocket.accept()
            
            try:
                while True:
                    # Receive frame data
                    data = await websocket.receive_json()
                    
                    # Decode base64 frame
                    frame_data = base64.b64decode(data['frame'])
                    nparr = np.frombuffer(frame_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame is None:
                        continue
                    
                    # Run inference
                    result = await self.ai_server.detect(frame, camera_id)
                    
                    # Send result
                    await websocket.send_json({
                        'status': 'success',
                        'result': result
                    })
            
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_json({
                    'status': 'error',
                    'message': str(e)
                })
            
            finally:
                await websocket.close()
    
    def get_app(self):
        """Get FastAPI application"""
        return self.app
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
        """Run the API server"""
        try:
            import uvicorn
            
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                reload=reload,
                log_level="info"
            )
        
        except ImportError:
            logger.error("Uvicorn not installed. Install with: pip install uvicorn")


# ============================================================================
# STANDALONE USAGE
# ============================================================================

def create_app() -> FastAPI:
    """Create FastAPI application"""
    api = AIServerAPI(enable_gpu=False)
    return api.get_app()


# Module-level ASGI app export for uvicorn
app = create_app()


if __name__ == '__main__':
    # Initialize and run server
    api = AIServerAPI(enable_gpu=False)
    
    print("\n" + "="*60)
    print("🚀 Advanced AI Safety Detection Server")
    print("="*60)
    print("\n📍 Access API at:")
    print("   Main: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("   ReDoc: http://localhost:8000/redoc")
    print("\n")
    
    api.run(host="0.0.0.0", port=8000, reload=True)
