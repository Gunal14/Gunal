# Quick Start Guide - AI Smart Safety Monitoring System

Get up and running in 5 minutes!

## System Requirements
- Windows 10+, macOS, or Linux
- Python 3.8+
- Webcam/camera connected to your computer
- 4GB RAM minimum
- 2GB disk space

## Installation (Choose One Method)

### Method 1: Automated Setup (Recommended)

**Windows:**
```bash
cd "d:\major project"
python setup.py
run.bat
```

**macOS/Linux:**
```bash
cd "d:/major project"
python3 setup.py
./run.sh
```

### Method 2: Manual Setup

**Step 1:** Navigate to project directory
```bash
cd "d:\major project"
```

**Step 2:** Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Step 3:** Install dependencies
```bash
pip install -r requirements.txt
```

**Step 4:** Run application
```bash
python app.py
```

## Access the Application

1. Open your web browser
2. Navigate to: **http://localhost:5000**
3. You should see the Safety Monitoring Dashboard

## First Steps

### 1. Check System Status
- Go to Settings page
- Verify camera is detected
- Check system information

### 2. Start Monitoring
- Click **"Start Monitoring"** button in header
- Video feed should appear on Monitoring page
- Watch for real-time detection

### 3. View Dashboard
- Check Safety Score
- Review incident statistics
- Monitor active alerts

### 4. Test Detection
- Wear or hold a helmet in front of camera
- Move in and out of frame
- Check detection accuracy

## Understanding the Interface

### Dashboard
- **Safety Score**: Overall system health (0-100)
- **Total Incidents**: All-time incident count
- **Today's Incidents**: Incidents in last 24 hours
- **Critical Alerts**: High severity violations

### Live Monitoring
- Real-time video stream
- Worker and helmet count
- Compliance rate percentage
- Active alerts display

### Incidents
- Complete incident history
- Filter by date/severity
- View detailed incident info
- Export data

### Alerts
- Review active safety alerts
- Configure alert parameters
- Enable/disable notifications
- Acknowledge alerts

### Analytics
- Incident trends
- Type distribution
- Severity analysis
- Generate reports

### Settings
- Camera configuration
- Detection parameters
- Resolution/frame rate
- System information

## Common Tasks

### Change Camera
1. Go to Settings
2. Set Camera ID (0 for default, 1 for secondary, etc.)
3. Restart monitoring

### Adjust Detection Threshold
1. Go to Settings
2. Move "Helmet Detection Threshold" slider
3. Lower = more sensitive, Higher = less sensitive

### View Incident Details
1. Go to Incidents
2. Click incident row
3. View details pop-up

### Export Report
1. Go to Analytics
2. Select report type
3. Click "Generate PDF"
4. Wait for download

### Clear Alerts
1. Go to Dashboard
2. Click "Clear Alerts" button
3. All alerts marked as cleared

## Troubleshooting

### Camera Not Working
```
Problem: "Cannot open camera" error
Solution:
1. Check camera connection
2. Close other apps using camera
3. Try Camera ID 1 or 2 in Settings
```

### Poor Detection
```
Problem: Not detecting helmets correctly
Solution:
1. Ensure good lighting
2. Lower detection threshold in Settings
3. Train model on your specific helmets
```

### Port Already in Use
```
Problem: "Address already in use" on port 5000
Solution:
1. Close other Flask apps
2. Or modify port in app.py:
   app.run(port=5001)
```

### Performance Issues
```
Problem: Slow/laggy application
Solution:
1. Lower video resolution in Settings
2. Reduce frame rate
3. Close background applications
4. Use more powerful computer
```

## Performance Tips

- **Best Performance**: 640x480 @ 30 FPS
- **Better Quality**: 1280x720 @ 30 FPS (higher CPU)
- **Max Quality**: 1920x1080 @ 30 FPS (requires powerful PC)

## Advanced Usage

### API Access
Get statistics programmatically:
```bash
curl http://localhost:5000/api/statistics
```

See **API_DOCUMENTATION.md** for full API reference

### Custom Helmet Colors
Edit `safety_detection.py` HSV ranges:
```python
lower_yellow = np.array([15, 50, 50])
upper_yellow = np.array([35, 255, 255])
```

### Train Custom Model
1. Collect helmet/no-helmet images
2. Organize in `dataset/` folder
3. Create training script
4. Update model path in code

## Next Steps

1. **Read Full Documentation**: See `README.md` for comprehensive guide
2. **Check API Docs**: Review `API_DOCUMENTATION.md`
3. **Explore Configuration**: Adjust settings in `config.py`
4. **Train Models**: Prepare datasets and train detection models

## Support & Resources

- **Documentation**: README.md
- **API Guide**: API_DOCUMENTATION.md
- **Configuration**: config.py
- **Issues**: Check troubleshooting section

## Important Notes

- Application stores data in SQLite database
- Database file: `safety_monitoring.db`
- Change SECRET_KEY in production
- Enable HTTPS for production deployment
- Implement authentication for production

## Commands Cheat Sheet

```bash
# Start application
python app.py

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run setup wizard
python setup.py

# Access application
Open browser -> http://localhost:5000
```

## Default Access

- **URL**: http://localhost:5000
- **Username**: (no authentication by default)
- **Port**: 5000 (can be changed)

---

**Now you're ready to monitor safety! 🛡️**
