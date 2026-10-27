"""
AI Server Quick Start Guide & Examples
Comprehensive usage examples for the Advanced AI Server
"""

import asyncio
import base64
import cv2
import numpy as np
from pathlib import Path
from ai_server import (
    AdvancedAIServer,
    AdvancedInferenceEngine,
    AdvancedCache,
    PriorityInferenceQueue,
    AdvancedModelManager,
    DetectionResult,
    InferenceResult,
)


# ============================================================================
# EXAMPLE 1: Basic Single Image Detection
# ============================================================================

async def example_single_detection():
    """Detect objects in a single image"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Single Image Detection")
    print("="*80)
    
    # Initialize server
    server = AdvancedAIServer(enable_gpu=False, enable_ensemble=False)
    
    # Create dummy frame (640x480 RGB image)
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Run inference
    result = await server.detect(frame, camera_id=0)
    
    print(f"✓ Detections found: {len(result.detections)}")
    print(f"✓ Processing time: {result.processing_time:.2f}ms")
    print(f"✓ Model version: {result.model_version}")
    
    for detection in result.detections[:3]:  # Print first 3 detections
        print(f"  - Class: {detection.class_label}, "
              f"Confidence: {detection.confidence:.2f}, "
              f"Box: {detection.bbox}")


# ============================================================================
# EXAMPLE 2: Batch Processing Multiple Frames
# ============================================================================

async def example_batch_detection():
    """Process multiple frames in a batch"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Batch Processing")
    print("="*80)
    
    server = AdvancedAIServer(enable_gpu=False, enable_ensemble=False)
    
    # Create 5 dummy frames
    frames = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        for _ in range(5)
    ]
    
    # Run batch inference
    results = await server.detect_batch(frames, camera_id=0)
    
    print(f"✓ Processed {len(results)} frames")
    for i, result in enumerate(results):
        print(f"  Frame {i}: {len(result.detections)} detections, "
              f"Time: {result.processing_time:.2f}ms")


# ============================================================================
# EXAMPLE 3: Ensemble Model Inference
# ============================================================================

async def example_ensemble_inference():
    """Use ensemble of models for improved accuracy"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Ensemble Model Inference")
    print("="*80)
    
    server = AdvancedAIServer(enable_gpu=False, enable_ensemble=True)
    
    # Register multiple models (simulated)
    server.register_model(
        name="yolov8_helmet",
        model_type="yolov8",
        version="8.2",
        input_shape=(640, 640, 3)
    )
    server.register_model(
        name="yolov8_person",
        model_type="yolov8",
        version="8.2",
        input_shape=(640, 640, 3)
    )
    
    # Activate both models for ensemble
    server.activate_model("yolov8_helmet")
    server.activate_model("yolov8_person")
    
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Run ensemble inference
    result = await server.detect(frame, camera_id=0)
    
    active_models = server.get_model_info()
    print(f"✓ Active ensemble models: {len(active_models)}")
    for model in active_models:
        print(f"  - {model['name']} (v{model['version']})")
    
    print(f"✓ Ensemble detections: {len(result.detections)}")
    print(f"✓ Per-class confidence scores: {result.confidence_scores}")


# ============================================================================
# EXAMPLE 4: Caching & Performance
# ============================================================================

async def example_caching():
    """Demonstrate caching efficiency"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Caching & Performance Metrics")
    print("="*80)
    
    server = AdvancedAIServer(enable_gpu=False)
    
    # Create a test frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # First detection (cache miss)
    result1 = await server.detect(frame, camera_id=0, use_cache=True)
    metrics1 = server.get_health_status()
    
    print(f"✓ First detection: {result1.processing_time:.2f}ms")
    print(f"✓ Cache hit rate: {metrics1['cache_hit_rate']*100:.1f}%")
    
    # Same frame again (cache hit)
    result2 = await server.detect(frame, camera_id=0, use_cache=True)
    metrics2 = server.get_health_status()
    
    print(f"✓ Cached detection: {result2.processing_time:.2f}ms (faster!)")
    print(f"✓ Cache hit rate: {metrics2['cache_hit_rate']*100:.1f}%")
    
    # Different frame (cache miss)
    frame2 = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    result3 = await server.detect(frame2, camera_id=0, use_cache=True)
    
    print(f"✓ New frame detection: {result3.processing_time:.2f}ms")


# ============================================================================
# EXAMPLE 5: Priority Queue for Safety Alerts
# ============================================================================

async def example_priority_queue():
    """Process safety-critical frames with priority"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Priority Queue for Safety Alerts")
    print("="*80)
    
    queue = PriorityInferenceQueue(max_size=50)
    
    # Add normal priority frame
    frame1 = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    await queue.add_request(
        frame=frame1,
        camera_id=0,
        priority=1,  # Normal priority
        request_id="frame_001"
    )
    
    # Add high priority safety alert
    frame2 = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    await queue.add_request(
        frame=frame2,
        camera_id=0,
        priority=10,  # High priority
        request_id="safety_alert_001"
    )
    
    # Get high priority item first
    request = await queue.get_request()
    print(f"✓ Next request: {request['request_id']}")
    print(f"  Priority: {request['priority']}")
    
    stats = queue.get_stats()
    print(f"✓ Queue stats:")
    print(f"  - Processed: {stats['processed']}")
    print(f"  - Rejection rate: {stats['rejection_rate']:.1%}")


# ============================================================================
# EXAMPLE 6: Model Registry & Versioning
# ============================================================================

async def example_model_management():
    """Manage multiple model versions"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Model Registry & Versioning")
    print("="*80)
    
    manager = AdvancedModelManager()
    
    # Register different model versions
    manager.register_model(
        name="helmet_detector",
        model_type="yolov8",
        version="8.0",
        input_shape=(640, 640, 3)
    )
    manager.register_model(
        name="helmet_detector",
        model_type="yolov8",
        version="8.1",
        input_shape=(640, 640, 3)
    )
    manager.register_model(
        name="helmet_detector",
        model_type="yolov8",
        version="8.2",
        input_shape=(640, 640, 3)
    )
    
    # Activate latest version
    manager.activate_model("helmet_detector", version="8.2")
    
    # Get active models
    active = manager.get_ensemble_models()
    print(f"✓ Active models: {len(active)}")
    for model in active:
        print(f"  - {model['name']} v{model['version']}")
    
    # Get model statistics
    for model_name in ["helmet_detector"]:
        stats = manager.get_model_stats(model_name)
        print(f"\n✓ {model_name} statistics:")
        print(f"  - Total inferences: {stats['total_inferences']}")
        print(f"  - Avg time: {stats['avg_inference_time_ms']:.2f}ms")


# ============================================================================
# EXAMPLE 7: Health Status & Monitoring
# ============================================================================

async def example_health_monitoring():
    """Monitor server health and performance"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Health Status & Monitoring")
    print("="*80)
    
    server = AdvancedAIServer(enable_gpu=False)
    
    # Run a few inferences
    for i in range(3):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        await server.detect(frame, camera_id=i)
    
    # Get health status
    health = server.get_health_status()
    
    print(f"✓ Server Status: {health['status']}")
    print(f"✓ Uptime: {health.get('uptime_seconds', 'N/A')}s")
    print(f"✓ Total inferences: {health.get('total_inferences', 0)}")
    print(f"✓ Cache hit rate: {health.get('cache_hit_rate', 0)*100:.1f}%")
    print(f"✓ Queue utilization: {health.get('queue_utilization', 0)*100:.1f}%")
    print(f"✓ GPU available: {health.get('gpu_available', False)}")


# ============================================================================
# EXAMPLE 8: Real-time Performance Metrics
# ============================================================================

async def example_performance_metrics():
    """Monitor detailed performance metrics"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Real-time Performance Metrics")
    print("="*80)
    
    server = AdvancedAIServer(enable_gpu=False)
    
    # Run multiple inferences
    total_time = 0
    for i in range(5):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        result = await server.detect(frame, camera_id=0, use_cache=False)
        total_time += result.processing_time
    
    metrics = server.get_health_status()
    
    print(f"✓ Performance Summary:")
    print(f"  - Average inference: {total_time/5:.2f}ms")
    print(f"  - Throughput: {metrics.get('inference_throughput_fps', 0):.1f} FPS")
    print(f"  - Cache efficiency: {metrics.get('cache_hit_rate', 0)*100:.1f}%")


# ============================================================================
# MAIN: Run all examples
# ============================================================================

async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "Advanced AI Server - Complete Usage Examples".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        await example_single_detection()
        await example_batch_detection()
        await example_ensemble_inference()
        await example_caching()
        await example_priority_queue()
        await example_model_management()
        await example_health_monitoring()
        await example_performance_metrics()
        
        print("\n" + "="*80)
        print("✓ All examples completed successfully!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n[INFO] Starting Advanced AI Server Examples...")
    print("[INFO] Using directory:", Path(__file__).parent)
    
    asyncio.run(main())
