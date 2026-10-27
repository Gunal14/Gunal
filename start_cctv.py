#!/usr/bin/env python3
"""
Complete CCTV Safety System Starter
Configures and starts the professional CCTV monitoring system
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cctv_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_cctv_system(config_file="cctv_config.json"):
    """
    Setup Complete CCTV System
    Uses configuration from cctv_config.json
    """
    
    # Import CCTV components
    from cctv_system import ProfessionalCCTVSystem
    from realtime_cctv_monitor import RealtimeCCTVMonitor, CCTVWebServer
    
    print("\n" + "="*70)
    print(" "*15 + "🎥 PROFESSIONAL CCTV SAFETY MONITORING SYSTEM 🎥")
    print("="*70 + "\n")
    
    # Load configuration
    config_path = Path(config_file)
    
    if config_path.exists():
        logger.info(f"Loading configuration from {config_file}")
        with open(config_path) as f:
            config = json.load(f)
    else:
        logger.warning(f"Configuration file not found. Using defaults.")
        config = create_default_config()
        # Save default config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Created default configuration: {config_file}")
    
    # Initialize system
    system = ProfessionalCCTVSystem(config.get("system_name", "CCTV Safety System"))
    logger.info(f"Initialized system: {system.system_name}")
    
    # Register cameras
    print("📷 REGISTERING CAMERAS...")
    for camera in config.get("cameras", []):
        success = system.register_camera(
            camera["id"],
            camera.get("source", 0),
            camera.get("location", "Unknown")
        )
        status = "✓" if success else "✗"
        print(f"  {status} {camera['id']} - {camera.get('location', 'Unknown')}")
    
    # Register safety zones
    print("\n🚧 REGISTERING SAFETY ZONES...")
    for zone in config.get("zones", []):
        system.analyzer.register_safety_zone(
            zone["id"],
            zone.get("type", "high_risk"),
            zone.get("coordinates", []),
            zone.get("min_ppe", {}),
            zone.get("restricted", False)
        )
        print(f"  ✓ {zone['id']} ({zone.get('type', 'high_risk')})")
    
    # Register employees
    print("\n👥 REGISTERING EMPLOYEES...")
    for employee in config.get("employees", []):
        system.analyzer.register_employee(
            employee["id"],
            employee.get("name", "Unknown"),
            employee.get("role", "Staff"),
            employee.get("required_ppe", {"helmet": True})
        )
        print(f"  ✓ {employee.get('name')} ({employee.get('role')})")
    
    # Print system summary
    status = system.get_system_status()
    print("\n" + "="*70)
    print("SYSTEM STATUS:")
    print("="*70)
    print(f"System Name:        {status['system_name']}")
    print(f"Status:             {status['status'].upper()}")
    print(f"Active Cameras:     {status['active_cameras']}/{status['total_cameras']}")
    print(f"Registered Zones:   {status['safety_zones']}")
    print(f"Registered Employees: {status['employees_registered']}")
    print("="*70 + "\n")
    
    return system, config


def create_default_config():
    """Create default CCTV configuration"""
    return {
        "system_name": "Employee Safety CCTV System",
        "cameras": [
            {
                "id": "CAM_001",
                "source": 0,
                "location": "Main Entrance",
                "zones": ["ZONE_MAIN"]
            },
            # Add more cameras as needed
            # {
            #     "id": "CAM_002",
            #     "source": "rtsp://192.168.1.100:554/stream",
            #     "location": "Warehouse Floor",
            #     "zones": ["ZONE_MAIN", "ZONE_HAZMAT"]
            # }
        ],
        "zones": [
            {
                "id": "ZONE_MAIN",
                "type": "high_risk",
                "coordinates": [[0, 0], [1280, 0], [1280, 720], [0, 720]],
                "min_ppe": {"helmet": True},
                "restricted": False
            },
            # Add more zones as needed
            # {
            #     "id": "ZONE_HAZMAT",
            #     "type": "high_risk",
            #     "coordinates": [[100, 100], [400, 100], [400, 600], [100, 600]],
            #     "min_ppe": {"helmet": True, "gloves": True, "vest": True},
            #     "restricted": False
            # }
        ],
        "employees": [
            {
                "id": "EMP001",
                "name": "John Operator",
                "role": "Operator",
                "required_ppe": {"helmet": True, "gloves": True}
            },
            # Add more employees as needed
        ],
        "recording": {
            "enabled": True,
            "fps": 15,
            "resolution": [1280, 720],
            "max_disk_usage_gb": 100,
            "output_dir": "recordings"
        },
        "alerts": {
            "enabled": True,
            "email_on_critical": False,
            "sms_on_critical": False,
            "enable_escalation": True
        }
    }


def start_monitoring(system, config, web=False, port=5000, test=False):
    """Start real-time monitoring"""
    
    from realtime_cctv_monitor import RealtimeCCTVMonitor, CCTVWebServer
    import time
    
    print("🚀 STARTING REAL-TIME MONITORING...\n")
    
    # Create monitor
    monitor = RealtimeCCTVMonitor(system)
    
    # Start monitoring
    monitor.start()
    logger.info("Monitoring system started")
    
    print(status_display(system))
    
    # Start web server if requested
    if web:
        print(f"\n🌐 Starting web server on port {port}...")
        print(f"   Dashboard: http://localhost:{port}")
        web_server = CCTVWebServer(monitor, port=port)
        
        try:
            web_server.run(debug=test)
        except KeyboardInterrupt:
            logger.info("Web server stopped")
    else:
        # Keep monitoring running
        try:
            print("Monitoring active. Press Ctrl+C to stop.\n")
            while True:
                time.sleep(60)
                # Print periodic status
                # Uncomment for verbose monitoring:
                # print(monitor.get_performance_report())
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
    
    # Cleanup
    print("\n🛑 Shutting down...")
    monitor.stop()
    logger.info("System shutdown complete")


def status_display(system):
    """Display formatted system status"""
    status = system.get_system_status()
    
    return f"""
╔════════════════════════════════════════════════════════════════╗
║  ✓ CCTV SYSTEM OPERATIONAL                                    ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  System:              {status['system_name']:35} ║
║  Status:              {status['status'].upper():35} ║
║  Uptime:              {int(status['uptime_seconds']):35} seconds ║
║                                                                ║
║  CAMERAS:                                                      ║
║    Active:            {status['active_cameras']}/{status['total_cameras']:33} ║
║                                                                ║
║  INCIDENTS:                                                    ║
║    Total:             {status['total_incidents']:35} ║
║    Active Alerts:     {status['active_alerts']:35} ║
║    Critical:          {status['critical_alerts']:35} ║
║                                                                ║
║  CONFIGURATION:                                                ║
║    Registered Employees: {status['employees_registered']:28} ║
║    Safety Zones:      {status['safety_zones']:35} ║
║                                                                ║
║  Last Update:         {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):35} ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""


def generate_incident_report(system, hours=24):
    """Generate and display incident report"""
    
    report = system.analyzer.get_incident_report(hours=hours)
    
    print("\n" + "="*70)
    print(f"INCIDENT REPORT - Last {hours} Hours")
    print("="*70)
    print(f"Generated: {report['generated_at']}\n")
    
    print(f"Total Incidents:      {report['total_incidents']}")
    print(f"Critical Incidents:   {report['critical_incidents']}")
    print(f"High Priority:        {report['high_incidents']}\n")
    
    print("Incidents by Type:")
    for incident_type, count in report['incidents_by_type'].items():
        print(f"  • {incident_type}: {count}")
    
    print("\nTop Violators:")
    if report['top_violators']:
        for emp_id, count in report['top_violators'][:5]:
            emp = system.analyzer.employee_db.get(emp_id, {})
            name = emp.get('name', emp_id)
            print(f"  • {name}: {count} violations")
    else:
        print("  • No violations found")
    
    print("\n" + "="*70)


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="Professional CCTV Safety Monitoring System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_cctv.py                    # Start with default config
  python start_cctv.py --web              # Start with web interface
  python start_cctv.py --config custom.json --web --port 8080
  python start_cctv.py --report           # Generate incident report
  python start_cctv.py --test             # Test mode with debug output
        """
    )
    
    parser.add_argument('--config', default='cctv_config.json',
                       help='Configuration file (default: cctv_config.json)')
    parser.add_argument('--web', action='store_true',
                       help='Enable web dashboard')
    parser.add_argument('--port', type=int, default=5000,
                       help='Web server port (default: 5000)')
    parser.add_argument('--report', action='store_true',
                       help='Generate incident report')
    parser.add_argument('--hours', type=int, default=24,
                       help='Report time period in hours')
    parser.add_argument('--test', action='store_true',
                       help='Test mode with debug output')
    
    args = parser.parse_args()
    
    try:
        # Setup system
        system, config = setup_cctv_system(args.config)
        
        # Generate report mode
        if args.report:
            generate_incident_report(system, hours=args.hours)
            return
        
        # Start monitoring
        start_monitoring(system, config, web=args.web, port=args.port, test=args.test)
    
    except KeyboardInterrupt:
        logger.info("System interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
