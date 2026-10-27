# Integration Guide: Improved Detection System

## Overview

This guide shows how to integrate the new `ImprovedSafetyDetector` into your existing Flask application.

## Files Created

1. **improved_safety_detection.py** - Core detection system with 4 fallback methods
2. **instant_test.py** - Quick start testing script
3. **quick_test_alerts.py** - Full test with alerts
4. **verify_installation.py** - System verification
5. **DETECTION_FIX_GUIDE.md** - Comprehensive documentation

## Quick Integration

### Option 1: Replace Existing Detector (Recommended)

```python
# In your Flask route or monitoring script
from improved_safety_detection import ImprovedSafetyDetector

detector = ImprovedSafetyDetector()

# In your video loop
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Get detection results
    results = detector.detect(frame)
    
    # Access detection data
    workers = results["workers"]           # List of detected worker rectangles
    helmets = results["helmets"]           # List of detected helmet rectangles
    safety_analysis = results["safety"]    # List of safety violations
    method = results["detection_method"]   # Which method was used
    
    # Get annotated frame for display
    annotated = detector.annotate_frame(frame, results)
    
    cv2.imshow("Monitoring", annotated)
```

### Option 2: Drop-in Replacement

If you have existing code using `SafetyDetector`:

**Before:**
```python
from safety_detection import SafetyDetector

detector = SafetyDetector()
workers, helmets = detector.detect_objects(frame)
```

**After:**
```python
from improved_safety_detection import ImprovedSafetyDetector

detector = ImprovedSafetyDetector()
results = detector.detect(frame)
workers = results["workers"]
helmets = results["helmets"]
```

## Integration Examples

### Example 1: Flask CSRF Route

```python
from flask import Blueprint, send_file
from improved_safety_detection import ImprovedSafetyDetector
import cv2
import io
from PIL import Image

safety_bp = Blueprint('safety', __name__)
detector = ImprovedSafetyDetector()

@safety_bp.route('/api/detect', methods=['POST'])
def detect_from_image():
    """Detect workers and helmets in uploaded image"""
    file = request.files['image']
    image = Image.open(file.stream)
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Run detection
    results = detector.detect(frame)
    
    # Return results
    return jsonify({
        'workers_count': len(results['workers']),
        'helmets_count': len(results['helmets']),
        'violations': results['safety'],
        'detection_method': results['detection_method']
    })
```

### Example 2: Continuous Monitoring Service

```python
import threading
from improved_safety_detection import ImprovedSafetyDetector

class MonitoringService:
    def __init__(self):
        self.detector = ImprovedSafetyDetector()
        self.running = False
        self.latest_results = None
        
    def start(self, camera_id=0):
        """Start continuous monitoring"""
        self.running = True
        cap = cv2.VideoCapture(camera_id)
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect
            self.latest_results = self.detector.detect(frame)
            
            # Send alerts if needed
            if self.latest_results['safety']:
                self.send_alert(self.latest_results)
        
        cap.release()
    
    def start_background(self, camera_id=0):
        """Run monitoring in background thread"""
        thread = threading.Thread(target=self.start, args=(camera_id,))
        thread.daemon = True
        thread.start()
        return thread
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
    
    def get_status(self):
        """Get current detection status"""
        if self.latest_results is None:
            return None
        
        return {
            'workers': len(self.latest_results['workers']),
            'helmets': len(self.latest_results['helmets']),
            'violations': len(self.latest_results['safety']),
            'method': self.latest_results['detection_method'],
            'timestamp': datetime.now().isoformat()
        }

# Usage in Flask
monitor = MonitoringService()

@app.route('/monitoring/start', methods=['POST'])
def start_monitoring():
    monitor.start_background(camera_id=0)
    return jsonify({'status': 'started'})

@app.route('/monitoring/status', methods=['GET'])
def get_monitoring_status():
    return jsonify(monitor.get_status())

@app.route('/monitoring/stop', methods=['POST'])
def stop_monitoring():
    monitor.stop()
    return jsonify({'status': 'stopped'})
```

### Example 3: Real-time Streaming with Detection

```python
from flask import Response
from improved_safety_detection import ImprovedSafetyDetector
import cv2

detector = ImprovedSafetyDetector()

def generate_frames(camera_id=0):
    """Generate frames with detection overlays"""
    cap = cv2.VideoCapture(camera_id)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect
        results = detector.detect(frame)
        
        # Annotate
        annotated = detector.annotate_frame(frame, results)
        
        # Encode
        ret, buffer = cv2.imencode('.jpg', annotated)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    cap.release()

@app.route('/video_feed', methods=['GET'])
def video_feed():
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')
```

## Configuration

### Adjust Detection Sensitivity

```python
# In improved_safety_detection.py
class ImprovedSafetyDetector:
    def __init__(self):
        # Make detection more or less sensitive
        self.cascade_params = {
            'scaleFactor': 1.05,      # Lower = more sensitive
            'minNeighbors': 3,         # Lower = more sensitive
            'minSize': (30, 30),       # Smaller = finds smaller objects
            'maxSize': (400, 400)      # Adjust detection range
        }
        
        # Skin tone detection ranges (HSV)
        self.lower_skin = np.array([0, 10, 60])      # Adjust for your lighting
        self.upper_skin = np.array([20, 150, 255])
        
        # Motion detection threshold
        self.motion_threshold = 1000   # Pixels changed to trigger detection
```

### Performance Tuning

```python
# For faster detection (lower quality)
def detect_fast(self, frame):
    """Fast detection on downsampled frame"""
    small = cv2.resize(frame, (320, 240))  # 50% smaller
    results = self.detect(small)
    # Scale results back up
    for rect_list in [results['workers'], results['helmets']]:
        for r in rect_list:
            r[0] *= 2
            r[1] *= 2
            r[2] *= 2
            r[3] *= 2
    return results

# For slower, more accurate detection
def detect_accurate(self, frame):
    """Accurate detection with all methods"""
    results = self.detect(frame)
    if len(results['workers']) < 2:  # If few workers found
        # Run additional passes with different parameters
        results2 = self._detect_workers_cascades(frame, 1.15)
        if len(results2) > len(results['workers']):
            results['workers'] = results2
    return results
```

## Testing Integration

```python
# test_integration.py
import cv2
from improved_safety_detection import ImprovedSafetyDetector

def test_detection():
    """Test the detector works"""
    detector = ImprovedSafetyDetector()
    cap = cv2.VideoCapture(0)
    
    for i in range(30):  # 30 frames
        ret, frame = cap.read()
        if ret:
            results = detector.detect(frame)
            print(f"Frame {i}: {len(results['workers'])} workers, "
                  f"{len(results['helmets'])} helmets [{results['detection_method']}]")
    
    cap.release()

if __name__ == "__main__":
    test_detection()
```

## Troubleshooting

### Detection Not Working?

1. **Check camera:**
   ```bash
   python verify_installation.py
   ```

2. **Test detector directly:**
   ```bash
   python instant_test.py
   ```

3. **Check detection method:**
   ```python
   results = detector.detect(frame)
   print(f"Method used: {results['detection_method']}")
   ```

4. **Verify cascade files:**
   ```python
   import cv2
   print(cv2.data.haarcascades)  # Should show cascade directory
   ```

### Performance Issues?

1. **Reduce frame size:**
   ```python
   frame = cv2.resize(frame, (320, 240))
   ```

2. **Skip frames:**
   ```python
   if frame_count % 3 == 0:  # Process every 3rd frame
       results = detector.detect(frame)
   ```

3. **Use threading:**
   ```python
   import threading
   detection_thread = threading.Thread(target=detector.detect, args=(frame,))
   ```

## Migration Checklist

- [ ] Copy `improved_safety_detection.py` to your project
- [ ] Update imports to use `ImprovedSafetyDetector`
- [ ] Test with `python instant_test.py`
- [ ] Update Flask routes to use new detection
- [ ] Configure alert system (SMS/WhatsApp/Email)
- [ ] Test with live camera
- [ ] Deploy to production
- [ ] Monitor performance metrics
- [ ] Adjust sensitivity based on results

## API Reference

### ImprovedSafetyDetector.detect(frame)

**Input:** NumPy array (BGR image frame)

**Output:** Dictionary with keys:
- `workers` - List of [x, y, w, h] rectangles for detected workers
- `helmets` - List of [x, y, w, h] rectangles for detected helmets
- `safety` - List of violation dictionaries
- `detection_method` - String: "primary", "motion", "skin_tone", or "edges"

### ImprovedSafetyDetector.annotate_frame(frame, results)

**Input:** 
- frame - Original image
- results - Output from detect()

**Output:** Annotated frame with boxes drawn

### Safety Violation Format

```python
{
    'worker_index': 0,
    'worker_rect': [x, y, w, h],
    'violation_type': 'NO_HELMET',
    'confidence': 0.85,
    'message': 'Worker without helmet detected'
}
```

## Next Steps

1. Run `python instant_test.py` to test
2. Run `python verify_installation.py` to verify setup
3. Check `DETECTION_FIX_GUIDE.md` for detailed information
4. Integrate into your Flask app using examples above
5. Configure alerts with your phone number and email
6. Deploy to production

---

**Version**: 3.0.0
**Status**: ✅ Ready for Integration