# SYSTEM DEPLOYMENT CHECKLIST

## Pre-Launch Verification

Run through this checklist before deploying the system to production.

---

## Phase 1: System Requirements ✓

### Python & Dependencies
- [ ] Python 3.8+ installed
  ```bash
  python --version
  ```
  
- [ ] All packages installed:
  ```bash
  pip list | grep "opencv\|numpy\|flask\|pillow\|face-recognition"
  ```

- [ ] Required packages:
  - [ ] opencv-python (4.0+)
  - [ ] numpy (1.20+)
  - [ ] flask (2.0+)
  - [ ] pillow (8.0+)
  - [ ] flask-sqlalchemy
  - [ ] python-dotenv
  - [ ] face-recognition (optional, for facial recognition)

### Hardware
- [ ] Webcam/Camera connected and working
- [ ] Adequate disk space (minimum 2 GB free)
- [ ] Stable internet connection (for alerts)
- [ ] CPU capable of running OpenCV (dual-core minimum)

---

## Phase 2: Detection System ✓

### Files Present
- [ ] `improved_safety_detection.py` (detection engine)
- [ ] `instant_test.py` (quick test script)
- [ ] `quick_test_alerts.py` (alert test script)
- [ ] `verify_installation.py` (verification script)

### Detection Functionality
- [ ] Run verification:
  ```bash
  python verify_installation.py
  ```

- [ ] Verify all checks pass:
  - [ ] Python version OK
  - [ ] OpenCV installed
  - [ ] NumPy installed
  - [ ] Camera accessible
  - [ ] Detection module loads
  - [ ] Alert service ready

### Test Detection
- [ ] Run quick test:
  ```bash
  python instant_test.py
  ```

- [ ] Verify detection works:
  - [ ] Show face to camera
  - [ ] System detects you
  - [ ] Shows detection method (primary/motion/skin_tone/edges)
  - [ ] Displays "Workers Detected: 1"

- [ ] Test alert system:
  - [ ] Submit mobile number
  - [ ] Submit email address
  - [ ] Press SPACE to send test alert
  - [ ] Verify alert formatting

---

## Phase 3: Alert System Configuration ✓

### Email Configuration
- [ ] SMTP server configured
  - [ ] Gmail: `smtp.gmail.com:587`
  - [ ] SendGrid: Credentials configured
  - [ ] Custom SMTP: Connection tested

- [ ] Email credentials set:
  - [ ] MAIL_USERNAME configured
  - [ ] MAIL_PASSWORD configured
  - [ ] MAIL_PORT set correctly
  - [ ] Test email sent successfully

- [ ] Test email alert:
  ```bash
  python instant_test.py
  # Send test alert and verify email received
  ```

### SMS/WhatsApp Configuration (Optional)
- [ ] Twilio account created (if using SMS/WhatsApp)
  - [ ] Account SID obtained
  - [ ] Auth Token obtained
  - [ ] Phone numbers configured

- [ ] Credentials stored securely:
  - [ ] .env file created (not in git)
  - [ ] Environment variables loaded
  - [ ] Credentials NOT logged anywhere

- [ ] Test SMS/WhatsApp:
  ```bash
  # Run instant_test.py and verify messages
  ```

### Contact Information
- [ ] User mobile number format valid
  - [ ] Example: +919876543210 (with country code)
  - [ ] Or: 9876543210 (without country code)

- [ ] User email verified
  - [ ] Can receive test emails
  - [ ] Spam folder checked

---

## Phase 4: Detection Accuracy ✓

### Test Scenarios

**Scenario 1: Good Lighting**
- [ ] Show face directly to camera
- [ ] Expected: Detection within 1-2 seconds
- [ ] Expected: "Workers Detected: 1"
- [ ] Result: ✅ PASS / ❌ FAIL

**Scenario 2: Side View**
- [ ] Turn head to side (90 degrees)
- [ ] Expected: Detection via motion/skin tone
- [ ] Expected: "Workers Detected: 1"
- [ ] Result: ✅ PASS / ❌ FAIL

**Scenario 3: Partial Face**
- [ ] Hide part of face with hand
- [ ] Expected: Still detected via fallback methods
- [ ] Expected: "Workers Detected: 1"
- [ ] Result: ✅ PASS / ❌ FAIL

**Scenario 4: Distance Variation**
- [ ] Step back (6+ feet away)
- [ ] Expected: Still detected with cascade
- [ ] Expected: "Workers Detected: 1"
- [ ] Result: ✅ PASS / ❌ FAIL

**Scenario 5: Poor Lighting**
- [ ] Dim the lights
- [ ] Move slightly
- [ ] Expected: Detection via motion/skin tone
- [ ] Expected: "Workers Detected: 1"
- [ ] Result: ✅ PASS / ❌ FAIL

### Helmet Detection
- [ ] With helmet on: "Helmets Detected: 1"
- [ ] Without helmet: "Helmets Detected: 0"
- [ ] Multiple people mix: Correct counts

### Alert Triggering
- [ ] Appear without helmet: Alert triggered
- [ ] Alert sent to phone ✅
- [ ] Alert sent to email ✅
- [ ] Alert has timestamp ✅
- [ ] Alert has problem statement ✅

---

## Phase 5: Performance & Stress Testing ✓

### Frame Rate Testing
- [ ] Run continuous monitoring for 5 minutes
- [ ] Check CPU usage: Should be < 80%
- [ ] Check FPS: Should be > 10 FPS
- [ ] No lag in display

### Memory Testing
- [ ] Monitor RAM usage during 10-minute run
- [ ] Should be stable < 500 MB
- [ ] No memory leaks
- [ ] Restart needed? No

### Multiple Test Runs
- [ ] Run detection 5 times consecutively
- [ ] Same person detected each time? ✅
- [ ] Detection method logs match? ✅
- [ ] Alert system consistent? ✅

---

## Phase 6: Integration & Deployment ✓

### Flask Integration
- [ ] Flask app starts: `python run.py`
- [ ] Web interface loads: `http://localhost:5000`
- [ ] Employee management works (if using)
- [ ] REST API endpoints respond

### Database
- [ ] Database initialized
- [ ] Employee table created (if using)
- [ ] Alert logs table created
- [ ] Can write to database

### File Permissions
- [ ] All Python files readable
- [ ] Camera accessible
- [ ] Can write to project directory
- [ ] Config files not world-readable

### Security Checklist
- [ ] No credentials in code
- [ ] .env file in .gitignore
- [ ] API keys not logged
- [ ] Database credentials protected
- [ ] Email passwords not exposed

---

## Phase 7: Production Readiness ✓

### Monitoring Setup
- [ ] Continuous monitoring script ready
- [ ] Logging configured
- [ ] Alert history tracked
- [ ] Performance metrics collected

### Backup & Recovery
- [ ] Employee database backed up
- [ ] Alert logs backed up
- [ ] Configuration backed up
- [ ] Recovery procedure documented

### Documentation
- [ ] DETECTION_FIX_GUIDE.md reviewed
- [ ] INTEGRATION_QUICK_START.md reviewed
- [ ] All configurations documented
- [ ] Emergency procedures documented

### Deployment
- [ ] All tests passed
- [ ] Production server configured
- [ ] Network access verified
- [ ] Camera feeds working
- [ ] Alert systems active

---

## Phase 8: Monitoring & Support ✓

### Daily Operations
- [ ] Monitor alert frequency (should be low)
- [ ] Check detection accuracy (should be >90%)
- [ ] Review alert delivery (should be <5 seconds)

### Weekly Review
- [ ] Check system logs for errors
- [ ] Verify backup completion
- [ ] Test alert system (send test alert)
- [ ] Review detection statistics

### Monthly Review
- [ ] Update cascade parameters if needed
- [ ] Optimize detection for your environment
- [ ] Review and improve false positive rate
- [ ] Plan maintenance windows

---

## Startup Sequence

### When Starting System:

1. **Verify Camera**
   ```bash
   python verify_installation.py
   ```
   Wait for all checks to pass ✅

2. **Test Detection & Alerts**
   ```bash
   python instant_test.py
   ```
   - Enter your phone number
   - Enter your email
   - Show face to camera
   - Verify detection works
   - Press SPACE for test alert

3. **Start Full System**
   ```bash
   python run.py
   ```
   Or with continuous monitoring:
   ```bash
   python enhanced_real_time_monitoring.py
   ```

4. **Verify Web Interface**
   - Open: http://localhost:5000
   - Check dashboard
   - All green? ✅

5. **Begin Monitoring**
   - System running ✅
   - Alerts active ✅
   - Ready for production ✅

---

## Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| No detection | Run `instant_test.py`, check lighting |
| Alerts not sent | Verify email/phone in config |
| High CPU usage | Reduce frame resolution |
| Lag in video | Lower FPS or reduce quality |
| Camera error | Check permissions, try camera 1 or 2 |
| Import errors | Run `verify_installation.py` |

---

## Sign-Off Checklist

- [ ] All tests passed
- [ ] Detection accuracy verified
- [ ] Alert system working
- [ ] Performance acceptable
- [ ] Documentation reviewed
- [ ] Team trained on system
- [ ] Go-live approved

**Date Verified:** _______________
**Verified By:** _______________
**Ready for Production:** ✅ YES / ❌ NO

---

## Quick Reference Commands

```bash
# Verify system setup
python verify_installation.py

# Test detection and alerts
python instant_test.py

# Quick test for alerts
python quick_test_alerts.py

# Start monitoring
python enhanced_real_time_monitoring.py

# Start Flask app
python run.py

# Check FPS and performance
python -c "
import cv2, time
cap = cv2.VideoCapture(0)
start = time.time()
for i in range(30):
    cap.read()
fps = 30 / (time.time() - start)
print(f'FPS: {fps:.1f}')
cap.release()
"
```

---

**System Version**: 3.0.0 (Enhanced Detection)
**Last Updated**: March 27, 2026
**Status**: ✅ Ready for Deployment