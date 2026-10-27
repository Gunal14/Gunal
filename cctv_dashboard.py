#!/usr/bin/env python3
"""
Professional CCTV Monitoring Dashboard
Real-time safety monitoring interface with multi-camera support
"""

import cv2
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path

class CCTVDashboard:
    """Professional CCTV monitoring dashboard visualization"""
    
    def __init__(self, screen_width=1920, screen_height=1080):
        """Initialize dashboard"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.background_color = (20, 20, 20)  # Dark background
        self.text_color = (200, 200, 200)
        self.accent_color = (0, 200, 100)  # Green accent
        
        self.fonts = {
            "title": cv2.FONT_HERSHEY_TRIPLEX,
            "header": cv2.FONT_HERSHEY_DUPLEX,
            "body": cv2.FONT_HERSHEY_SIMPLEX
        }
        
        self.font_sizes = {
            "title": 1.2,
            "header": 0.8,
            "body": 0.6
        }
    
    def create_multi_camera_view(self, camera_feeds: Dict[str, np.ndarray], 
                                system_status: Dict) -> np.ndarray:
        """
        Create multi-camera dashboard view
        
        Args:
            camera_feeds: Dict of {camera_id: frame}
            system_status: System status dictionary
            
        Returns:
            Composite dashboard frame
        """
        dashboard = np.ones((self.screen_height, self.screen_width, 3), dtype=np.uint8) * 20
        
        # Draw title bar
        self._draw_title_bar(dashboard, system_status)
        
        # Draw camera grid (2x2 for 4 cameras, adjust as needed)
        num_cameras = len(camera_feeds)
        if num_cameras == 1:
            grid = (1, 1)
        elif num_cameras == 2:
            grid = (1, 2)
        elif num_cameras <= 4:
            grid = (2, 2)
        elif num_cameras <= 6:
            grid = (2, 3)
        else:
            grid = (3, 3)
        
        camera_width = (self.screen_width - 20) // grid[1]
        camera_height = (self.screen_height - 120 - 20) // grid[0]
        
        for idx, (camera_id, frame) in enumerate(camera_feeds.items()):
            row = idx // grid[1]
            col = idx % grid[1]
            
            x = 10 + col * camera_width
            y = 80 + row * camera_height
            
            self._draw_camera_view(dashboard, frame, camera_id, x, y, 
                                  camera_width - 10, camera_height - 10)
        
        # Draw status panel
        self._draw_status_panel(dashboard, system_status)
        
        # Draw alert panel
        self._draw_alert_panel(dashboard, system_status.get("active_alerts", []))
        
        return dashboard
    
    def _draw_title_bar(self, frame: np.ndarray, status: Dict):
        """Draw title bar with system name and status"""
        # Dark bar background
        cv2.rectangle(frame, (0, 0), (self.screen_width, 70), (40, 40, 40), -1)
        
        # Title
        text = f"🎥 {status.get('system_name', 'CCTV System')} - Live Monitoring"
        cv2.putText(frame, text, (20, 40),
                   self.fonts["title"], self.font_sizes["title"],
                   self.accent_color, 2)
        
        # Status indicator
        status_color = (0, 200, 100) if status.get("status") == "online" else (200, 100, 0)
        status_text = f"Status: {status.get('status', 'unknown').upper()}"
        cv2.putText(frame, status_text, (self.screen_width - 300, 40),
                   self.fonts["body"], self.font_sizes["body"],
                   status_color, 1)
        
        # Time
        time_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, time_text, (self.screen_width - 300, 60),
                   self.fonts["body"], 0.5,
                   self.text_color, 1)
    
    def _draw_camera_view(self, dashboard: np.ndarray, frame: np.ndarray, 
                         camera_id: str, x: int, y: int, w: int, h: int):
        """Draw individual camera feed with overlay"""
        if frame is None:
            # Draw offline notice
            cv2.rectangle(dashboard, (x, y), (x+w, y+h), (50, 50, 50), -1)
            cv2.rectangle(dashboard, (x, y), (x+w, y+h), (150, 150, 150), 2)
            text = f"{camera_id} - OFFLINE"
            cv2.putText(dashboard, text, (x+20, y+h//2),
                       self.fonts["body"], 0.8, (150, 150, 150), 1)
            return
        
        # Resize and place frame
        resized = cv2.resize(frame, (w, h))
        dashboard[y:y+h, x:x+w] = resized
        
        # Draw border
        cv2.rectangle(dashboard, (x, y), (x+w, y+h), (100, 100, 100), 2)
        
        # Draw camera label
        cv2.rectangle(dashboard, (x, y), (x+200, y+30), (0, 0, 0), -1)
        cv2.putText(dashboard, camera_id, (x+10, y+20),
                   self.fonts["header"], 0.7, self.accent_color, 1)
    
    def _draw_status_panel(self, frame: np.ndarray, status: Dict):
        """Draw system status panel"""
        panel_y = self.screen_height - 100
        
        # Panel background
        cv2.rectangle(frame, (0, panel_y), (self.screen_width, self.screen_height),
                     (40, 40, 40), -1)
        cv2.line(frame, (0, panel_y), (self.screen_width, panel_y), (100, 100, 100), 1)
        
        # Status items
        items = [
            f"Cameras: {status.get('active_cameras', 0)}/{status.get('total_cameras', 0)}",
            f"Incidents: {status.get('total_incidents', 0)}",
            f"Alerts: {status.get('active_alerts', 0)}",
            f"Employees: {status.get('employees_registered', 0)}"
        ]
        
        x_offset = 20
        for item in items:
            cv2.putText(frame, item, (x_offset, panel_y + 25),
                       self.fonts["body"], 0.6, self.text_color, 1)
            x_offset += 280
    
    def _draw_alert_panel(self, frame: np.ndarray, alerts: List[Dict]):
        """Draw active alerts panel"""
        alert_panel_x = self.screen_width - 350
        alert_panel_y = 80
        alert_panel_w = 340
        alert_panel_h = 200
        
        # Panel background
        cv2.rectangle(frame, (alert_panel_x, alert_panel_y),
                     (alert_panel_x + alert_panel_w, alert_panel_y + alert_panel_h),
                     (40, 40, 40), -1)
        cv2.rectangle(frame, (alert_panel_x, alert_panel_y),
                     (alert_panel_x + alert_panel_w, alert_panel_y + alert_panel_h),
                     (200, 50, 50), 2)
        
        # Title
        cv2.putText(frame, "ACTIVE ALERTS", (alert_panel_x + 10, alert_panel_y + 25),
                   self.fonts["header"], 0.7, (200, 50, 50), 1)
        
        # Alert list
        y_offset = alert_panel_y + 50
        unack_alerts = [a for a in alerts if not a.get("acknowledged", True)]
        
        if unack_alerts:
            for alert in unack_alerts[:4]:  # Show top 4
                severity_color = {
                    "critical": (0, 0, 200),
                    "high": (0, 100, 200),
                    "medium": (0, 200, 100),
                    "low": (200, 200, 0)
                }.get(alert.get("severity", "low"), (200, 200, 0))
                
                alert_text = f"[{alert.get('type', 'Unknown')}]"
                cv2.putText(frame, alert_text, (alert_panel_x + 10, y_offset),
                           self.fonts["body"], 0.5, severity_color, 1)
                y_offset += 25
        else:
            cv2.putText(frame, "No active alerts", (alert_panel_x + 10, y_offset),
                       self.fonts["body"], 0.6, (0, 200, 100), 1)
    
    def create_single_camera_view(self, frame: np.ndarray, camera_id: str,
                                 detections: Dict, alerts: List[Dict]) -> np.ndarray:
        """Create single camera detailed view with overlay"""
        if frame is None:
            frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        output = frame.copy()
        height, width = output.shape[:2]
        
        # Draw detections
        self._draw_detections(output, detections)
        
        # Draw HUD information
        self._draw_hud_info(output, camera_id, detections, alerts)
        
        return output
    
    def _draw_detections(self, frame: np.ndarray, detections: Dict):
        """Draw detection boxes and labels"""
        # Draw workers
        for worker in detections.get("workers", []):
            x, y, w, h = worker["box"]
            # Draw bounding box
            color = (0, 200, 100) if worker.get("helmet_detected") else (0, 100, 200)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Draw label
            label = f"Worker - {'🎯 Safe' if worker.get('helmet_detected') else '⚠️ No Helmet'}"
            cv2.putText(frame, label, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw PPE status
        for ppe in detections.get("ppe", []):
            x, y, w, h = ppe["box"]
            color = (0, 200, 100) if ppe.get("detected") else (0, 0, 200)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 1)
    
    def _draw_hud_info(self, frame: np.ndarray, camera_id: str, 
                      detections: Dict, alerts: List[Dict]):
        """Draw HUD information overlay"""
        height, width = frame.shape[:2]
        y_offset = 40
        
        # Camera ID and time
        cv2.putText(frame, f"Camera: {camera_id}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 100), 2)
        
        time_text = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, time_text, (width - 150, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        
        y_offset += 60
        
        # Detection statistics
        stats = [
            f"Workers: {len(detections.get('workers', []))}",
            f"Helmets: {sum(1 for w in detections.get('workers', []) if w.get('helmet_detected'))}",
            f"Compliance: {self._calculate_compliance(detections)}%",
        ]
        
        for stat in stats:
            cv2.putText(frame, stat, (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            y_offset += 30
        
        # Draw alerts
        if alerts:
            y_offset += 20
            cv2.putText(frame, f"ALERTS: {len(alerts)}", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 200), 2)
            y_offset += 30
            
            for alert in alerts[:3]:
                alert_text = f"  • {alert['type']}: {alert.get('severity', '').upper()}"
                cv2.putText(frame, alert_text, (20, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 1)
                y_offset += 25
    
    @staticmethod
    def _calculate_compliance(detections: Dict) -> int:
        """Calculate compliance percentage"""
        workers = detections.get("workers", [])
        if not workers:
            return 100
        
        safe_count = sum(1 for w in workers if w.get("helmet_detected"))
        return int((safe_count / len(workers)) * 100)
    
    def create_analytics_dashboard(self, analytics_data: Dict) -> np.ndarray:
        """Create analytics dashboard view"""
        width, height = 1280, 720
        dashboard = np.ones((height, width, 3), dtype=np.uint8) * 20
        
        # Title
        cv2.putText(dashboard, "Safety Analytics Dashboard", (40, 40),
                   cv2.FONT_HERSHEY_TRIPLEX, 1.0, (0, 200, 100), 2)
        
        # Key metrics
        metrics = [
            ("Total Incidents", str(analytics_data.get("total_incidents", 0)), (0, 200, 100)),
            ("Critical", str(analytics_data.get("critical_incidents", 0)), (0, 0, 200)),
            ("Compliance Rate", f"{analytics_data.get('compliance_rate', 0)}%", (0, 200, 100)),
            ("Safety Score", f"{analytics_data.get('safety_score', 0)}/100", (0, 200, 100)),
        ]
        
        y_offset = 100
        for label, value, color in metrics:
            cv2.putText(dashboard, f"{label}:", (40, y_offset),
                       cv2.FONT_HERSHEY_DUPLEX, 0.8, (200, 200, 200), 1)
            cv2.putText(dashboard, value, (350, y_offset),
                       cv2.FONT_HERSHEY_DUPLEX, 1.0, color, 2)
            y_offset += 80
        
        return dashboard


class CCTVRecordingPlayback:
    """Playback and review of CCTV recordings"""
    
    def __init__(self, recordings_dir="recordings"):
        """Initialize playback system"""
        self.recordings_dir = Path(recordings_dir)
    
    def list_recordings(self, camera_id: Optional[str] = None, 
                       date: Optional[str] = None) -> List[Path]:
        """List available recordings"""
        pattern = f"{camera_id or '*'}_{date or '*'}.mp4"
        return sorted(self.recordings_dir.glob(pattern))
    
    def play_incident_clip(self, incident_id: str):
        """Play incident video clip"""
        clip_path = self.recordings_dir / "incidents" / incident_id
        if clip_path.exists():
            return str(clip_path)
        return None
    
    def search_recordings(self, start_time: datetime, end_time: datetime,
                         camera_id: str, incident_type: Optional[str] = None) -> List[Dict]:
        """Search recordings by date/time and criteria"""
        results = []
        
        current = start_time
        while current <= end_time:
            date_str = current.date().isoformat()
            recordings = self.list_recordings(camera_id, date_str)
            
            for recording in recordings:
                results.append({
                    "file": str(recording),
                    "camera_id": camera_id,
                    "date": date_str,
                    "size": recording.stat().st_size
                })
            
            current += timedelta(days=1)
        
        return results


# Example usage and testing
if __name__ == "__main__":
    dashboard = CCTVDashboard()
    
    # Create sample frame for testing
    test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    test_frame[:] = (50, 50, 50)
    
    # Sample camera feeds
    camera_feeds = {
        "CAM_001": test_frame,
        "CAM_002": test_frame,
        "CAM_003": test_frame,
        "CAM_004": test_frame,
    }
    
    # Sample system status
    system_status = {
        "system_name": "Warehouse Safety CCTV",
        "status": "online",
        "active_cameras": 4,
        "total_cameras": 4,
        "total_incidents": 12,
        "active_alerts": 2,
        "employees_registered": 25,
        "active_alerts": [
            {"type": "missing_helmet", "severity": "high", "acknowledged": False},
            {"type": "unauthorized_access", "severity": "critical", "acknowledged": False},
        ]
    }
    
    # Create dashboard
    dashboard_frame = dashboard.create_multi_camera_view(camera_feeds, system_status)
    print("Dashboard frame created: shape =", dashboard_frame.shape)
