"""
AI Server Integration Guide
How to integrate Advanced AI Server with Flask Backend
"""

# ============================================================================
# OPTION 1: Direct Import Integration (In-Process)
# ============================================================================
"""
Best for: Single-threaded apps, development, lightweight deployments
Pros: Simple, no network overhead
Cons: Blocks Flask thread during inference, memory shared
"""

# File: backend/routes/monitoring.py

from flask import request, jsonify
from flask_socketio import emit
import cv2
import numpy as np
import asyncio
import base64
from pathlib import Path

# Import AI Server
from ai.api import AdvancedAIServer

# Initialize AI Server (do once, share globally)
ai_server = AdvancedAIServer(
    enable_gpu=False,
    enable_ensemble=True,
    cache_size=1000
)

@app.route('/api/v1/detect', methods=['POST'])
def detect_endpoint():
    """Detect objects in uploaded image using AI Server"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        camera_id = request.form.get('camera_id', 0, type=int)
        
        # Decode image
        frame = cv2.imdecode(
            np.frombuffer(file.read(), np.uint8),
            cv2.IMREAD_COLOR
        )
        
        if frame is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        # Run async inference
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                ai_server.detect(frame, camera_id=camera_id)
            )
        finally:
            loop.close()
        
        # Format response
        detections = [
            {
                'class': det.class_label,
                'confidence': float(det.confidence),
                'bbox': det.bbox,
                'object_id': det.object_id,
                'timestamp': det.timestamp.isoformat()
            }
            for det in result.detections
        ]
        
        return jsonify({
            'detections': detections,
            'processing_time_ms': result.processing_time,
            'model_version': result.model_version,
            'confidence_scores': result.confidence_scores
        })
    
    except Exception as e:
        app.logger.error(f"Detection error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/detect/batch', methods=['POST'])
def detect_batch_endpoint():
    """Batch detect objects from multiple images"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        camera_id = request.form.get('camera_id', 0, type=int)
        
        frames = []
        for file in files:
            frame = cv2.imdecode(
                np.frombuffer(file.read(), np.uint8),
                cv2.IMREAD_COLOR
            )
            if frame is not None:
                frames.append(frame)
        
        if not frames:
            return jsonify({'error': 'No valid images'}), 400
        
        # Run batch inference
        loop = asyncio.new_event_loop()
        try:
            results = loop.run_until_complete(
                ai_server.detect_batch(frames, camera_id=camera_id)
            )
        finally:
            loop.close()
        
        # Format response
        batch_results = []
        for result in results:
            detections = [
                {
                    'class': det.class_label,
                    'confidence': float(det.confidence),
                    'bbox': det.bbox,
                }
                for det in result.detections
            ]
            batch_results.append({
                'detections': detections,
                'processing_time_ms': result.processing_time
            })
        
        return jsonify({
            'results': batch_results,
            'total_processing_time_ms': sum(r.processing_time for r in results)
        })
    
    except Exception as e:
        app.logger.error(f"Batch detection error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/ai/health', methods=['GET'])
def ai_health_endpoint():
    """Get AI Server health status"""
    try:
        health = ai_server.get_health_status()
        return jsonify(health)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/ai/models', methods=['GET'])
def get_models_endpoint():
    """List active AI models"""
    try:
        models = ai_server.get_model_info()
        return jsonify({'models': models})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@socketio.on('detect_frame')
def handle_detect_frame(data):
    """Real-time frame detection via WebSocket"""
    try:
        # Decode base64 image
        image_data = base64.b64decode(data['image_base64'])
        frame = cv2.imdecode(
            np.frombuffer(image_data, np.uint8),
            cv2.IMREAD_COLOR
        )
        
        camera_id = data.get('camera_id', 0)
        
        # Run inference
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                ai_server.detect(frame, camera_id=camera_id)
            )
        finally:
            loop.close()
        
        # Send detections back
        detections = [
            {
                'class': det.class_label,
                'confidence': float(det.confidence),
                'bbox': det.bbox,
                'object_id': det.object_id
            }
            for det in result.detections
        ]
        
        emit('detection_results', {
            'detections': detections,
            'processing_time_ms': result.processing_time,
            'timestamp': result.detections[0].timestamp.isoformat() if result.detections else None
        })
    
    except Exception as e:
        app.logger.error(f"WebSocket detection error: {e}")
        emit('detection_error', {'error': str(e)})


# ============================================================================
# OPTION 2: Separate FastAPI Server (Microservice)
# ============================================================================
"""
Best for: High-performance production, GPU servers, scaling
Pros: Non-blocking, scalable, GPU isolation
Cons: Network latency (~10-50ms), deployment complexity

To use:
1. Run AI server on separate port:
   python -m ai.api.rest_api &

2. Call from Flask:
"""

import requests
import aiohttp

@app.route('/api/v1/detect/remote', methods=['POST'])
def detect_remote():
    """Call remote AI Server via HTTP"""
    try:
        file = request.files['file']
        camera_id = request.form.get('camera_id', 0, type=int)
        
        # Send to AI Server
        files = {'file': (file.filename, file.stream, file.content_type)}
        params = {'camera_id': camera_id}
        
        response = requests.post(
            'http://localhost:8000/detect',
            files=files,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'AI Server error'}), response.status_code
    
    except Exception as e:
        app.logger.error(f"Remote detection error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/detect/async', methods=['POST'])
async def detect_async():
    """Call remote AI Server with aiohttp (async)"""
    try:
        file = await request.files
        camera_id = request.form.get('camera_id', 0, type=int)
        
        async with aiohttp.ClientSession() as session:
            with open(file, 'rb') as f:
                async with session.post(
                    'http://localhost:8000/detect',
                    data={'file': f},
                    params={'camera_id': camera_id}
                ) as resp:
                    return jsonify(await resp.json())
    
    except Exception as e:
        app.logger.error(f"Async detection error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# OPTION 3: Hybrid Approach - Local Caching + Remote Fallback
# ============================================================================
"""
Best for: Production with fallback, hybrid CPU/GPU setup
Pros: Fast cache hits locally, GPU fallback for new frames
Cons: Increased complexity
"""

class HybridDetectionService:
    """Hybrid local cache + remote server"""
    
    def __init__(self, remote_url='http://localhost:8000'):
        self.local_cache = {}
        self.remote_url = remote_url
        self.session = None
    
    async def detect(self, frame, camera_id=0, use_remote=True):
        """Detect with hybrid approach"""
        frame_hash = self._hash_frame(frame)
        
        # Try local cache first
        if frame_hash in self.local_cache:
            return self.local_cache[frame_hash]
        
        # Fall back to remote server
        if use_remote:
            result = await self._detect_remote(frame, camera_id)
            self.local_cache[frame_hash] = result
            return result
        else:
            raise ValueError("Frame not in cache and remote disabled")
    
    async def _detect_remote(self, frame, camera_id):
        """Call remote AI server"""
        _, image_bytes = cv2.imencode('.jpg', frame)
        
        async with aiohttp.ClientSession() as session:
            files = {'file': ('frame.jpg', image_bytes.tobytes())}
            async with session.post(
                f'{self.remote_url}/detect',
                data=files,
                params={'camera_id': camera_id}
            ) as resp:
                return await resp.json()
    
    def _hash_frame(self, frame):
        """Hash frame for cache key"""
        import hashlib
        return hashlib.md5(frame.tobytes()).hexdigest()


# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================

"""
STEP 1: Install dependencies
    pip install -r ai/api/requirements.txt

STEP 2: Choose integration method

    Option A (Recommended for Development):
    ========================================
    - Direct import in monitoring.py
    - No external process needed
    - Memory efficient for small deployments
    
    Code: See above OPTION 1 section
    
    Option B (Recommended for Production):
    =======================================
    - Run separate FastAPI server
    - GPU isolation
    - Scalable to multiple servers
    
    Steps:
    1. cd d:\major project\ai\api
    2. python rest_api.py
    3. Modify Flask routes to call http://localhost:8000/detect
    4. code: See above OPTION 2 section

STEP 3: Update Flask routes
    - Copy code from selected option above
    - Add to backend/routes/monitoring.py
    - Restart Flask server

STEP 4: Test integration
    - POST image to /api/v1/detect
    - Check response contains detections
    - Monitor processing time

STEP 5: Monitor performance
    - Check /api/v1/ai/health endpoint
    - Review cache hit rate
    - Monitor queue utilization
    - Adjust cache_size if needed

STEP 6: Configure for production
    - Enable GPU: enable_gpu=True
    - Increase cache: cache_size=2000
    - Enable ensemble: enable_ensemble=True
    - Add authentication to API endpoints
    - Set up load balancing if needed
"""

# ============================================================================
# PERFORMANCE TUNING GUIDE
# ============================================================================

"""
Development Setup (Option 1):
- enable_gpu=False
- enable_ensemble=False
- cache_size=500
- Expected: 50-80ms per frame

Production Setup (Option 2):
- enable_gpu=True (on GPU server)
- enable_ensemble=True
- cache_size=2000
- Expected: 20-40ms per frame (GPU), 15-25ms (cached)

High-Load Setup (Option 3):
- Multiple AI servers behind load balancer
- Each with enable_gpu=True
- Shared Redis cache
- Expected: 10-20ms per frame (with load distribution)
"""

# ============================================================================
# MONITORING & DEBUGGING
# ============================================================================

"""
Check AI Server Status:
    curl http://localhost:8000/health

View Performance Metrics:
    curl http://localhost:8000/metrics

Monitor Cache Hit Rate:
    curl http://localhost:8000/metrics/cache

Access Swagger Documentation:
    http://localhost:8000/docs

Test Detection Endpoint:
    curl -X POST http://localhost:8000/detect \
         -F "file=@test_image.jpg" \
         -F "camera_id=0"

View Active Models:
    curl http://localhost:8000/models
"""
