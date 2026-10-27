#!/usr/bin/env python3
"""
System Setup and Validation Script
Checks all requirements and validates installation

Usage: python validate_setup.py
"""

import sys
import os
import subprocess
from pathlib import Path

class SystemValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.successes = []
    
    def check_python_version(self):
        """Check Python version"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.successes.append(f"✅ Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.errors.append(f"❌ Python 3.8+ required (found {version.major}.{version.minor})")
            return False
    
    def check_packages(self):
        """Check required packages"""
        packages = {
            'cv2': 'OpenCV',
            'numpy': 'NumPy',
            'flask': 'Flask',
            'sqlalchemy': 'SQLAlchemy'
        }
        
        for module, name in packages.items():
            try:
                __import__(module)
                self.successes.append(f"✅ {name} installed")
            except ImportError:
                self.errors.append(f"❌ {name} not installed (pip install {module})")
    
    def check_files(self):
        """Check required files exist"""
        required_files = [
            'safety_detection.py',
            'real_time_monitoring.py',
            'requirements.txt',
            'run.py'
        ]
        
        for filename in required_files:
            if (self.project_root / filename).exists():
                self.successes.append(f"✅ {filename} found")
            else:
                self.warnings.append(f"⚠️  {filename} not found")
    
    def check_camera(self):
        """Check camera availability"""
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    self.successes.append(f"✅ Camera available (resolution: {frame.shape[:2]})")
                    return True
                else:
                    self.warnings.append("⚠️  Camera found but cannot read frames")
                    return False
            else:
                self.warnings.append("⚠️  Camera not found or not connected")
                return False
        except Exception as e:
            self.warnings.append(f"⚠️  Camera check failed: {e}")
            return False
    
    def check_storage(self):
        """Check available disk space"""
        import shutil
        total, used, free = shutil.disk_usage(self.project_root)
        free_gb = free / (1024**3)
        
        if free_gb > 1:
            self.successes.append(f"✅ {free_gb:.1f}GB free disk space")
        else:
            self.warnings.append(f"⚠️  Low disk space: {free_gb:.1f}GB")
    
    def check_opencv_version(self):
        """Check OpenCV version and capabilities"""
        try:
            import cv2
            version = cv2.__version__
            major = int(version.split('.')[0])
            
            if major >= 4:
                self.successes.append(f"✅ OpenCV {version} (good for real-time)")
            else:
                self.warnings.append(f"⚠️  OpenCV {version} (upgrade to 4.5+ recommended)")
            
            # Check cascade classifiers
            cascade_path = cv2.data.haarcascades
            if Path(cascade_path).exists():
                self.successes.append(f"✅ Cascade classifiers available")
            else:
                self.warnings.append(f"⚠️  Cascade classifiers not found")
                
        except Exception as e:
            self.errors.append(f"❌ OpenCV check failed: {e}")
    
    def test_detection_import(self):
        """Test if detection modules can be imported"""
        try:
            sys.path.insert(0, str(self.project_root))
            from safety_detection import SafetyDetector
            self.successes.append("✅ SafetyDetector imports successfully")
            return True
        except ImportError as e:
            self.errors.append(f"❌ Cannot import SafetyDetector: {e}")
            return False
        except Exception as e:
            self.warnings.append(f"⚠️  SafetyDetector import issue: {e}")
            return False
    
    def check_database(self):
        """Check if database can be initialized"""
        try:
            db_file = self.project_root / 'safety_monitoring.db'
            if db_file.exists():
                self.successes.append(f"✅ Database exists")
            else:
                self.warnings.append(f"⚠️  Database will be created on first run")
        except Exception as e:
            self.warnings.append(f"⚠️  Database check failed: {e}")
    
    def run_all_checks(self):
        """Run all validation checks"""
        print("\n" + "="*70)
        print("🔍 SYSTEM VALIDATION - AI SAFETY MONITORING")
        print("="*70 + "\n")
        
        print("Checking Python environment...")
        self.check_python_version()
        
        print("Checking installed packages...")
        self.check_packages()
        
        print("Checking OpenCV...")
        self.check_opencv_version()
        
        print("Checking required files...")
        self.check_files()
        
        print("Checking detection module...")
        self.test_detection_import()
        
        print("Checking camera...")
        self.check_camera()
        
        print("Checking storage...")
        self.check_storage()
        
        print("Checking database...")
        self.check_database()
        
        self.print_report()
    
    def print_report(self):
        """Print validation report"""
        print("\n" + "="*70)
        print("📊 VALIDATION REPORT")
        print("="*70 + "\n")
        
        if self.successes:
            print("✅ PASSED CHECKS:")
            for msg in self.successes:
                print(f"   {msg}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for msg in self.warnings:
                print(f"   {msg}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for msg in self.errors:
                print(f"   {msg}")
        
        print("\n" + "="*70)
        
        if not self.errors:
            print("✅ SYSTEM READY - You can run monitoring!")
            print("\nStart with:")
            print("   python real_time_monitoring.py")
            print("\nOr test first:")
            print("   python test_detection_system.py")
            exit_code = 0
        else:
            print("❌ CRITICAL ISSUES - Please fix errors above")
            print("\nFix missing packages with:")
            print("   pip install -r requirements.txt")
            exit_code = 1
        
        print("="*70 + "\n")
        return exit_code


def main():
    validator = SystemValidator()
    exit_code = validator.run_all_checks()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
