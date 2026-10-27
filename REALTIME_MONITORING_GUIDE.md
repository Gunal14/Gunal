# 🛡️ REAL-TIME HELMET DETECTION SYSTEM - COMPLETE SETUP GUIDE

## 📋 Overview
This guide will help you set up and run the AI Safety Helmet Detection system with real-time emergency alerts.

## ✅ SYSTEM REQUIREMENTS

### Hardware
- **Webcam or IP Camera** (connected and functional)
- **Processor**: Intel i7/Ryzen 7 or better (minimum i5/Ryzen 5)
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 2GB free space

### Software
- **Python**: 3.8 or higher
- **OpenCV**: 4.5+
- **NumPy**: 1.20+
- **Flask**: 2.3+

## 🚀 QUICK START (3 STEPS)

### STEP 1: Verify Python Installation
```bash
python --version
python -m pip --version
```

### STEP 2: Install Requirements
```bash
cd d:\major project
pip install -r requirements.txt
```

### STEP 3: Run Real-Time Monitoring
```bash
python real_time_monitoring.py
```

---

## 📌 OPTION 1: QUICK TEST (Recommended First)

Test the system without starting the full server:

```bash
# Test detection system initialization
python test_detection_system.py

# Test with live camera (60 seconds)
python test_detection_system.py --live
```

**Expected Output:**
```
🧪 HELMET DETECTION SYSTEM - QUICK TEST
✅ SafetyDetector imported successfully
✅ SafetyDetector initialized
✅ Detection completed
✅ Webcam accessible
```

---

## 📌 OPTION 2: STANDALONE REAL-TIME MONITORING

The most direct way to run helmet detection:

```bash
python real_time_monitoring.py
```

**This will:**
- ✅ Start live webcam feed
- ✅ Detect workers and helmets in real-time
- ✅ Display violations with bounding boxes
- ✅ Show FPS and detection statistics

**Controls:**
- `q` - Quit application
- `s` - Save screenshot

---

## 📌 OPTION 3: FULL WEB DASHBOARD

Start the complete web system:

```bash
python run.py
```

**This will:**
- Start Flask server on `http://localhost:5000`
- Deploy web dashboard
- Enable emergency alerts
- Allow multi-camera monitoring

**Access:**
- Dashboard: http://localhost:5000
- Monitoring: http://localhost:5000/monitoring
- API: http://localhost:5000/api

---

## 🎯 DETECTION FEATURES

### ✨ What Gets Detected

1. **Workers/People**
   - Face detection (primary method)
   - Skin tone detection (fallback)
   - Multiple people in frame

2. **Helmets**
   - Yellow helmets (most common)
   - Orange helmets
   - White helmets
   - Red hard hats
   - Blue helmets

3. **Violations**
   - Missing helmet on detected worker
   - No safety gear visible
   - Area overcrowding

### 📊 Real-Time Display

The live video shows:
- **Green boxes**: Detected helmets
- **Blue boxes**: Workers WITH helmets
- **Red boxes**: Workers WITHOUT helmets ❌
- **Compliance %**: Helmet coverage ratio
- **Status banner**: Real-time violations

### 🚨 Emergency Alerts

When violations detected:
- **Console Alert**: Printed to terminal
- **Visual Alert**: Red warning on screen
- **SMS Alert**: (if configured)
- **WhatsApp Alert**: (if configured)
- **Email Alert**: (if configured)

---

## 🔧 CONFIGURATION

### Detection Sensitivity

Edit `safety_detection.py`:

```python
# Line 27-29
self.helmet_confidence_threshold = 0.5     # Increase for stricter detection
self.worker_detection_threshold = 0.5      # Adjust sensitivity
self.alert_cooldown = 5                    # Seconds between alerts
```

### Color Range Adjustments

Edit `safety_detection.py` - `_detect_helmets()` method:

```python
# Yellow helmet range (line 116-118)
lower_yellow = np.array([10, 40, 50])     # H, S, V min
upper_yellow = np.array([40, 255, 255])   # H, S, V max
```

### Performance Tuning

```python
# In real_time_monitoring.py
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Reduce for faster FPS
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

---

## ⚠️ TROUBLESHOOTING

### Issue: Webcam Not Detected
```bash
# Check available cameras
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# Try camera index 1
python real_time_monitoring.py --camera 1
```

### Issue: Poor Helmet Detection
1. **Improve lighting** - Ensure good workplace lighting
2. **Adjust color ranges** - See Configuration section
3. **Check helmet color** - System optimized for yellow/orange
4. **Test with sample video**:
   ```bash
   python real_time_monitoring.py --video your_video.mp4
   ```

### Issue: Low FPS (Slow Detection)
1. Reduce frame resolution:
   ```bash
   # Edit real_time_monitoring.py, set lower resolution
   ```
2. Lower detection frequency
3. Use faster hardware

### Issue: False Positives (Detecting non-helmets)
1. Adjust HSV color ranges (more specific)
2. Increase minimum detection area
3. Add more filtering criteria

---

## 💡 TIPS FOR BEST RESULTS

1. **Lighting**: Ensure adequate workplace lighting for reliable detection
2. **Camera Placement**: Mount camera at eye level, 3-5 meters from work area
3. **Helmet Color**: System works best with bright colors (yellow/orange)
4. **Multiple Angles**: Use multiple cameras for better coverage
5. **Calibration**: Test with sample videos before live deployment

---

## 📈 MONITORING CHECKLIST

- [ ] Webcam is working and connected
- [ ] Python dependencies installed
- [ ] Test detection system passes
- [ ] Real-time monitoring shows live feed
- [ ] Violations are detected correctly
- [ ] Alerts are being triggered
- [ ] Dashboard is accessible (if using web option)

---

## 🆘 GETTING HELP

**Check Log Files:**
```bash
# View detailed logs
python real_time_monitoring.py > monitoring.log 2>&1
```

**Test Individual Components:**
```bash
# Test detection
python test_detection_system.py

# Test with video file
python real_time_monitoring.py --video test_video.mp4
```

**System Information:**
```bash
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
```

---

## 📞 EMERGENCY CONTACTS SETUP

To enable real emergency alerts:

1. Go to: http://localhost:5000
2. Register emergency contacts (max 10)
3. Configure alert preferences
4. Enable WhatsApp/SMS/Email channels

---

## 🎓 TYPICAL WORKFLOW

### Day 1: Setup
```bash
python test_detection_system.py          # Quick validation
python test_detection_system.py --live   # 60-second live test
```

### Day 1-2: Configuration
- Adjust color ranges for your helmet types
- Calibrate detection sensitivity
- Register emergency contacts

### Day 2+: Deployment
```bash
python real_time_monitoring.py           # Start monitoring
# or
python run.py                            # Full dashboard
```

---

## 📊 OUTPUT EXAMPLES

### Successful Detection:
```
🚀 REAL-TIME SAFETY MONITORING SYSTEM
  Source: Webcam (0)
  Model:  cascade
  Status: ACTIVE

[Frame 100] FPS: 28.5 | Detections: 45 | Violations: 0
```

### Violation Alert:
```
======================================================================
🚨 SAFETY VIOLATION ALERT - 2024-03-25 14:30:45
======================================================================
  Violation Type:    MISSING_HELMET
  Workers Detected:  2
  Helmets Detected:  1
  Compliance Rate:   50%
  Severity:          CRITICAL
  Action:            ⚠️  IMMEDIATE ACTION REQUIRED
======================================================================
```

---

## ✨ KEY FEATURES SUMMARY

| Feature | Status | How to Use |
|---------|--------|-----------|
| Real-time Detection | ✅ Active | `python real_time_monitoring.py` |
| Emergency Alerts | ✅ Active | Automatic when violation detected |
| Multiple Cameras | ✅ Available | Use web dashboard |
| WhatsApp Notifications | ✅ Available | Configure in settings |
| SMS Alerts | ✅ Available | Configure in settings |
| Email Reports | ✅ Available | Configure in settings |
| Analytics Dashboard | ✅ Available | http://localhost:5000 |

---

## 🎯 SUCCESS CRITERIA

System is working correctly when:

1. ✅ Live video feed displays without lag
2. ✅ Workers are detected and boxed (yellow rectangles)
3. ✅ Helmets are detected and boxed (green rectangles)
4. ✅ Missing helmets trigger red "DANGER" boxes
5. ✅ Violations print alert messages
6. ✅ FPS is 25+ on modern hardware
7. ✅ Emergency alerts send (when configured)

---

**🎉 SYSTEM READY! Your AI Safety Monitoring is now operational.**

For updates and support, check the project documentation.
