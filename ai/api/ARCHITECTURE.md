# Advanced AI Server - Architecture & Flowcharts

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend/Web UI                           │
│               (Dashboard, Real-time Monitoring)               │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP/WebSocket
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Flask Backend                               │
│  ┌──────────┐        ┌──────────────┐        ┌──────────────┐ │
│  │ /detect  │  ◄──►  │ /monitoring  │  ◄──►  │ /analytics   │ │
│  └────┬────┘        └──────────────┘        └──────────────┘ │
│       │ asyncio.run()                                          │
│       ▼─────────────────────────────────────────┐              │
│ ┌──────────────────────────────────────────────┴──────────────┐│
│ │         AdvancedAIServer (In-Process)                      ││
│ │  ┌────────────────┬──────────────┬──────────────┐          ││
│ │  │ Inference:     │ Models:      │ Cache:       │          ││
│ │  │ • Ensemble     │ • Registry   │ • LRU+TTL    │          ││
│ │  │ • NMS Merge    │ • Versions   │ • MD5 Hash   │          ││
│ │  │ • Async        │ • Activate   │ • Hit Rate   │          ││
│ │  └────────────────┴──────────────┴──────────────┘          ││
│ │  ┌────────────────────────────────────────────────────────┐ ││
│ │  │  PriorityInferenceQueue         Performance Metrics    │ ││
│ │  │  • Priority levels (0-10)       • Throughput (FPS)     │ ││
│ │  │  • Async/await                 • Latency (ms)         │ ││
│ │  │  • Timeout handling            • Cache hit rate       │ ││
│ │  │  • Request tracking            • Queue utilization     │ ││
│ │  └────────────────────────────────────────────────────────┘ ││
│ └───────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                  ┌───────────┴───────────┐
                  │ HTTP (Optional)      │
                  ▼                       ▼
        ┌─────────────────────┐   ┌──────────────────┐
        │  FastAPI Server     │   │  Database        │
        │  (Port 8000)        │   │  (Results)       │
        │                     │   │                  │
        │ • 13 REST Endpoints │   │ • MongoDB        │
        │ • WebSocket Stream  │   │ • PostgreSQL     │
        │ • Auto Swagger Docs │   │ • Elasticsearch  │
        │ • Batch Processing  │   │                  │
        └─────────────────────┘   └──────────────────┘
```

---

## 🔄 Request Flow

### Single Frame Detection Flow

```
User Uploads Image
        │
        ▼
┌──────────────────┐
│  Parse Request   │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│  Decode Image Frame  │
│  (OpenCV)            │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Generate Frame Hash │
│  (MD5)               │
└────────┬─────────────┘
         │
         ▼
    ┌────────────────────────┐
    │  Check Cache           │
    └────────┬────────┬──────┘
             │        │
          HIT│        │MISS
             ▼        ▼
        ┌────────┐  ┌──────────────────┐
        │  Return│  │ Add to Priority  │
        │ Cached │  │ Queue            │
        │ Result │  └────────┬─────────┘
        └────────┘           │
             │               ▼
             │         ┌──────────────────┐
             │         │ Get Request from │
             │         │ Queue            │
             │         └────────┬─────────┘
             │                  │
             │                  ▼
             │         ┌──────────────────────┐
             │         │ Load Active Models   │
             │         │ (Model Manager)      │
             │         └────────┬─────────────┘
             │                  │
             │                  ▼
             │         ┌──────────────────────┐
             │         │ Run Single Model or  │
             │         │ Ensemble Inference   │
             │         │ (Async)              │
             │         └────────┬─────────────┘
             │                  │
             │                  ▼
             │         ┌──────────────────────┐
             │         │ Merge Detections     │
             │         │ (NMS with IOU)       │
             │         └────────┬─────────────┘
             │                  │
             │                  ▼
             │         ┌──────────────────────┐
             │         │ Cache Result         │
             │         │ (TTL + LRU)          │
             │         └────────┬─────────────┘
             │                  │
             └──────────┬───────┘
                        │
                        ▼
                ┌──────────────────────┐
                │ Format Response      │
                │ (Pydantic)           │
                └────────┬─────────────┘
                         │
                         ▼
                    Return Result to Client
```

---

## 🎯 Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│            AdvancedAIServer (Orchestrator)                 │
│  ───────────────────────────────────────────────────────   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  detect(frame, camera_id, use_cache=True)          │  │
│  │  detect_batch(frames, camera_id)                   │  │
│  │  register_model(name, type, version)               │  │
│  │  activate_model(name, version)                     │  │
│  │  get_health_status()                               │  │
│  │  get_model_info()                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│               ┌───────────┼───────────┬───────────┐        │
│               │           │           │           │        │
│               ▼           ▼           ▼           ▼        │
│    ┌──────────────────────────────────────────────────┐    │
│    │        AdvancedInferenceEngine                  │    │
│    │  • infer(frame, camera_id, use_cache)         │    │
│    │  • batch_infer(frames, camera_id)             │    │
│    │  • get_metrics()                              │    │
│    └──────────────────────────────────────────────────┘    │
│               │                │              │             │
│               ▼                ▼              ▼             │
│    ┌─────────────────┐  ┌──────────────┐  ┌────────────┐   │
│    │AdvancedCache   │  │ModelManager  │  │Priority    │   │
│    │                │  │             │  │Queue       │   │
│    │ • get(key)     │  │ • register() │  │            │   │
│    │ • set(k,v)    │  │ • activate() │  │ • add_req()│   │
│    │ • get_hit_rate()│  │ • get_stats()│  │ • get_req()│   │
│    │ • clear()      │  │             │  │            │   │
│    └─────────────────┘  └──────────────┘  └────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Async Inference Pipeline

```
├─ Request comes in
│
├─ Check cache (non-blocking)
│  ├─ HIT: Return cached result (5ms)
│  └─ MISS: Continue to processing
│
├─ Add to PriorityInferenceQueue (non-blocking)
│
├─ Wait for worker thread
│  └─ All workers busy? Queue grows (configurable limit)
│
├─ Worker gets request from queue
│
├─ Load active models from ModelManager
│
├─ Run inference:
│  ├─ Single model: Run once (50-80ms CPU, 20-40ms GPU)
│  └─ Ensemble: Run all models in parallel
│     └─ Concurrent.futures executor
│     └─ Wait for all to complete
│
├─ Merge detections (Non-Maximum Suppression)
│  └─ Calculate IOU between all detections
│  └─ Merge if IOU > threshold
│  └─ Average confidence scores per class
│
├─ Cache result (LRU + TTL)
│  └─ Generate MD5 hash of input frame
│  └─ Store in memory cache
│  └─ Will expire after TTL
│  └─ Evict oldest if cache full
│
└─ Return response (Pydantic validation)
   └─ DetectionResult objects
   └─ Processing time metrics
   └─ Confidence scores
   └─ Model version info
```

---

## 📊 Cache Operation Flow

```
Frame Input
    │
    ▼
┌─────────────────────────────────┐
│ Generate MD5 Hash of Frame      │
│ (Frame as byte array)           │
└──────────┬──────────────────────┘
           │
           ▼
      ┌────────────────────┐
      │ Lookup in LRU      │
      │ Dictionary         │
      └────┬──────────┬────┘
           │          │
        HIT│          │MISS
           ▼          ▼
      ┌────────┐  ┌──────────────────┐
      │Return  │  │ Run Inference    │
      │Result  │  │ (Expensive)      │
      │(5ms)   │  └────────┬─────────┘
      └────────┘           │
           │               ▼
           │         ┌──────────────────┐
           │         │ Store in Cache   │
           │         │ with TTL timer   │
           │         └────────┬─────────┘
           │                  │
           │         ┌────────▼─────────┐
           │         │ Is Cache Full?   │
           │         └────┬───┬─────────┘
           │              │   │
           │            NO│   │YES
           │              ▼   ▼
           │            OK  ┌──────────────────┐
           │                │ Remove LRU Item  │
           │                │ (Least Recently  │
           │                │  Used)           │
           │                └────────┬─────────┘
           │                         │
           └──────────┬──────────────┘
                      │
                      ▼
                Return Result
              + Update Cache Stats
        (hits, misses, hit_rate)
```

---

## 🔀 Non-Maximum Suppression (NMS) Flow

```
Input: List of detections from models
    │
    ├─ Detection 1: bbox=[10,20,100,120], confidence=0.95
    ├─ Detection 2: bbox=[15,25,105,125], confidence=0.92
    ├─ Detection 3: bbox=[200,300,350,450], confidence=0.88
    └─ Detection 4: bbox=[205,305,355,455], confidence=0.85
    
    │
    ▼
┌─────────────────────────────────────────┐
│ Sort by Confidence (Descending)         │
│ ────────────────────────────────────── │
│ 1. Det 1: 0.95                          │
│ 2. Det 2: 0.92                          │
│ 3. Det 3: 0.88                          │
│ 4. Det 4: 0.85                          │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Process each detection in order:        │
│ ─────────────────────────────────────  │
│ For i = 1 to N:                        │
│   For j = i+1 to N:                    │
│     if IOU(box[i], box[j]) > threshold:│
│       DELETE detection j (lower conf)   │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Example with IOU threshold = 0.5:       │
│ ────────────────────────────────────   │
│ Iteration 1:                            │
│   IOU(Det1, Det2) = 0.87 > 0.5         │
│   → DELETE Det 2                        │
│   IOU(Det1, Det3) = 0.02 < 0.5         │
│   → KEEP Det 3                          │
│   IOU(Det1, Det4) = 0.01 < 0.5         │
│   → KEEP Det 4                          │
│                                         │
│ Iteration 3:                            │
│   IOU(Det3, Det4) = 0.91 > 0.5         │
│   → DELETE Det 4                        │
│                                         │
│ Final Result:                           │
│ ✓ Detection 1 (0.95)                    │
│ ✓ Detection 3 (0.88)                    │
└─────────────────────────────────────────┘
```

---

## 🎯 Ensemble Voting Flow

```
Input Frame
    │
    ▼
┌─────────────────────────────────────────┐
│ Get Active Models from ModelManager     │
│ ─────────────────────────────────────  │
│ • Model 1: YOLOv8 (weights: 0.4)       │
│ • Model 2: YOLOv8 (weights: 0.3)       │
│ • Model 3: Faster R-CNN (weights: 0.3) │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Model 1 │ │Model 2 │ │Model 3 │
│        │ │        │ │        │
│Detect: │ │Detect: │ │Detect: │
│• Person│ │• Person│ │• Person│
│ 0.95   │ │ 0.92   │ │ 0.91   │
│        │ │        │ │        │
│• Helmet│ │• Helmet│ │• Helmet│
│ 0.87   │ │ 0.85   │ │ 0.89   │
└────────┘ └────────┘ └────────┘
    │          │          │
    └──────────┼──────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ Combine Detections       │
    │ All overlapping boxes    │
    └──────────┬───────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ Apply NMS                │
    │ Merge similar detections │
    └──────────┬───────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ Calculate Confidence     │
    │ Weighted Average:        │
    │                          │
    │ For "Helmet":           │
    │ (0.87×0.4 + 0.85×0.3 +  │
    │  0.89×0.3) = 0.87       │
    │                          │
    │ For "Person":           │
    │ (0.95×0.4 + 0.92×0.3 +  │
    │  0.91×0.3) = 0.93       │
    └──────────┬───────────────┘
               │
               ▼
    Final Ensemble Result
    • Person: 0.93
    • Helmet: 0.87
    (More accurate than any single model!)
```

---

## 📈 Performance Metrics Flow

```
During Inference:
    │
    ├─ Record start time
    │  └─ t_start = time.time()
    │
    ├─ Run inference
    │  └─ (50-80ms)
    │
    ├─ Record end time
    │  └─ t_end = time.time()
    │
    ├─ Calculate metrics:
    │  ├─ processing_time = (t_end - t_start) * 1000 (ms)
    │  ├─ fps = 1000 / processing_time
    │  └─ inference_throughput_fps = exponential_moving_avg(fps)
    │
    ├─ Update cache metrics:
    │  ├─ if cache_hit: hits += 1
    │  └─ else: misses += 1
    │  └─ hit_rate = hits / (hits + misses)
    │
    ├─ Update queue metrics:
    │  ├─ total_processed += 1
    │  ├─ if rejected: total_rejected += 1
    │  └─ rejection_rate = rejected / processed
    │
    └─ Update model metrics:
       ├─ model.total_inferences += 1
       ├─ model.avg_time_ms = exp_moving_avg(processing_time)
       ├─ model.throughput_fps = exp_moving_avg(fps)
       ├─ model.gpu_usage = get_gpu_memory()
       └─ model.cpu_usage = get_cpu_percent()

At query time (/metrics endpoint):
    │
    ├─ Calculate overall statistics
    │  ├─ Total inferences across all frames
    │  ├─ Average processing time
    │  ├─ Overall throughput
    │  └─ Peak memory usage
    │
    └─ Return metrics JSON
```

---

## 🔌 API Integration Points

```
┌────────────────────────────────────────────┐
│         REST API Endpoints                 │
└────────────────────────────────────────────┘
           │                    │
   ┌───────┴────────┐    ┌──────┴──────────┐
   ▼                ▼    ▼                 ▼
Detection      Models  Health/Metrics   WebSocket
 Endpoints     Mgmt    Monitoring       Streaming
  │             │          │              │
  ├─ /detect    ├─ REG    ├─ /health     └─ /ws/stream/
  ├─ /base64    ├─ ACT    ├─ /detailed       {cam_id}
  └─ /batch     ├─ DEACT  └─ /metrics
               ├─ LIST    ├─ /cache
               └─ INFO    └─ /queue


         All ◄─────────────────────────────┐
      communicate                        Pydantic
         with                          Validation
         │                                 │
         ▼                                 ▼
   AdvancedAIServer

         │
         ├─────► AdvancedCache (Check/Store frames)
         ├─────► AdvancedModelManager (Get models)
         ├─────► PriorityInferenceQueue (Add request)
         └─────► AdvancedInferenceEngine (Run inference)
                       │
                       ▼
                 Backend ML Models
                (YOLOv8, Faster R-CNN, etc.)
```

---

## 🔄 Deployment Architecture

### Option 1: Single Process (Development)
```
┌───────────────────────────────────┐
│ Single Python Process             │
├───────────────────────────────────┤
│ Flask (Port 5000)                 │
│ └─ AdvancedAIServer (embedded)    │
│    └─ GPU/CPU shared with Flask   │
└───────────────────────────────────┘

Advantages:
• Simple setup
• No network latency
• Shared memory

Disadvantages:
• Flask blocked during inference
• Shared resources (GPU/CPU)
```

### Option 2: Microservices (Production)
```
┌─────────────────────┐      ┌──────────────────┐
│ Flask Service       │      │ AI Service       │
│ (Port 5000)         │◄────►│ (Port 8000)      │
│                     │ HTTP │                  │
│ Handle routing      │      │ AdvancedAIServer │
│ Serve UI            │      │                  │
│ Manage requests     │      │ GPU/CPU exclusive│
└─────────────────────┘      └──────────────────┘

Advantages:
• Separate resource allocation
• GPU isolation
• Easy scaling

Disadvantages:
• Network latency (10-50ms)
• Deployment complexity
```

### Option 3: Hybrid (Production Optimized)
```
┌─────────────────────────────────────┐
│ Flask Service                       │
├─────────────────────────────────────┤
│ Local Cache Wrapper                 │
│ └─ Check local cache first          │
│    └─ 5-10ms response time          │
│                                     │
│ Fallback:                           │
│ └─ Call remote AI Server            │
│    └─ If cache miss                 │
└────────┬────────────────────────────┘
         │ HTTP
         ▼
┌──────────────────────────────────────┐
│ FastAPI AI Server                    │
├──────────────────────────────────────┤
│ AdvancedAIServer (cached results)    │
│ └─ GPU/CPU exclusive                 │
└──────────────────────────────────────┘

Best of both worlds:
✓ Fast response on cache hit
✓ GPU isolation
✓ Easy scaling
✓ Low network overhead
```

---

## 📊 Error Handling Flow

```
API Request Received
    │
    ▼
Try:
  ├─ Validate input (Pydantic)
  │  └─ if invalid: Return 400 Bad Request
  │
  ├─ Decode image
  │  └─ if invalid: Return 400 Invalid Image
  │
  ├─ Add to queue
  │  └─ if queue full: Return 503 Service Unavailable
  │
  ├─ Run inference
  │  └─ if fails: Return 500 Internal Error
  │
  ├─ Format response
  │  └─ (Pydantic validation)
  │
  └─ Return 200 OK with results
    
Except:
  └─ Log error
     └─ Return 500 with error message
```

---

**Diagram Version**: 2.0 | **Last Updated**: 2024 | **For**: Advanced AI Server v2.0.0

