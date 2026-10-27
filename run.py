#!/usr/bin/env python
"""
Application Launcher
Run this file to start the AI Safety Monitoring System
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Change to project directory
os.chdir(Path(__file__).parent)

# Import and run the app
from backend.main import create_app

if __name__ == '__main__':
    # Create Flask app
    app = create_app(config_name='development')
    
    # Print startup info
    print("\n" + "="*70)
    print("🚀 AI SMART SAFETY MONITORING SYSTEM")
    print("="*70)
    print("\n✅ Dashboard:  http://localhost:5000/")
    print("✅ Monitoring: http://localhost:5000/monitoring")
    print("✅ API:        http://localhost:5000/api")
    print("✅ Health:     http://localhost:5000/health")
    print("\n📁 Frontend:   d:\\major project\\frontend")
    print("📁 Backend:    d:\\major project\\backend")
    print("📁 AI Module:  d:\\major project\\ai")
    print("\n💡 Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    # Run the app
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode,
        use_reloader=debug_mode
    )
