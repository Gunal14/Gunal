#!/usr/bin/env python3
"""
Setup and initialization script for AI Smart Safety Monitoring System
Run this script to properly set up the application
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class SetupWizard:
    """Installation and setup wizard"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.venv_dir = self.project_dir / 'venv'
        
    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*70)
        print("  AI Smart Safety Monitoring System - Setup Wizard".center(70))
        print("="*70 + "\n")
    
    def check_python_version(self):
        """Check Python version"""
        print("✓ Checking Python version...")
        if sys.version_info < (3, 8):
            print("✗ Error: Python 3.8+ required")
            print(f"  Current version: {sys.version}")
            return False
        print(f"✓ Python {sys.version.split()[0]} found")
        return True
    
    def check_dependencies(self):
        """Check system dependencies"""
        print("\n✓ Checking system dependencies...")
        
        # Check for pip
        if not shutil.which('pip'):
            print("✗ Error: pip not found. Please install pip.")
            return False
        print("✓ pip found")
        
        return True
    
    def create_virtual_environment(self):
        """Create virtual environment"""
        print("\n✓ Creating virtual environment...")
        
        try:
            if self.venv_dir.exists():
                print("  Virtual environment already exists")
            else:
                subprocess.run([sys.executable, '-m', 'venv', str(self.venv_dir)],
                             check=True)
                print(f"✓ Virtual environment created at {self.venv_dir}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Error creating virtual environment: {e}")
            return False
    
    def get_venv_python(self):
        """Get virtual environment Python executable"""
        if sys.platform == 'win32':
            return self.venv_dir / 'Scripts' / 'python.exe'
        else:
            return self.venv_dir / 'bin' / 'python'
    
    def install_requirements(self):
        """Install Python requirements"""
        print("\n✓ Installing Python dependencies...")
        
        try:
            venv_python = self.get_venv_python()
            requirements_file = self.project_dir / 'requirements.txt'
            
            subprocess.run([str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'],
                         check=True, capture_output=True)
            print("  Pip upgraded")
            
            subprocess.run([str(venv_python), '-m', 'pip', 'install', '-r', str(requirements_file)],
                         check=True)
            print("✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Error installing dependencies: {e}")
            return False
    
    def create_directories(self):
        """Create necessary directories"""
        print("\n✓ Creating directories...")
        
        directories = [
            self.project_dir / 'dataset' / 'helmet',
            self.project_dir / 'dataset' / 'no_helmet',
            self.project_dir / 'dataset' / 'worker',
            self.project_dir / 'dataset' / 'machine',
            self.project_dir / 'static' / 'css',
            self.project_dir / 'static' / 'js',
            self.project_dir / 'logs',
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        print("✓ Directories created")
        return True
    
    def initialize_database(self):
        """Initialize database"""
        print("\n✓ Initializing database...")
        
        try:
            venv_python = self.get_venv_python()
            init_code = """
from app import app, db
with app.app_context():
    db.create_all()
print("Database initialized successfully")
"""
            subprocess.run([str(venv_python), '-c', init_code],
                         cwd=str(self.project_dir),
                         check=True)
            print("✓ Database initialized")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Warning: Database initialization issue: {e}")
            return False
    
    def create_startup_script(self):
        """Create startup script"""
        print("\n✓ Creating startup scripts...")
        
        if sys.platform == 'win32':
            script_name = 'run.bat'
            script_content = f"""@echo off
echo Starting Safety Monitoring System...
cd /d {self.project_dir}
call {self.venv_dir}\\Scripts\\activate.bat
python app.py
pause
"""
        else:
            script_name = 'run.sh'
            script_content = f"""#!/bin/bash
echo "Starting Safety Monitoring System..."
cd "{self.project_dir}"
source {self.venv_dir}/bin/activate
python app.py
"""
        
        script_path = self.project_dir / script_name
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        if sys.platform != 'win32':
            os.chmod(script_path, 0o755)
        
        print(f"✓ Startup script created: {script_name}")
        return True
    
    def print_completion(self):
        """Print completion message"""
        print("\n" + "="*70)
        print("  Setup Complete! ✓".center(70))
        print("="*70 + "\n")
        
        print("Next steps:")
        print("1. Activate virtual environment:")
        if sys.platform == 'win32':
            print(f"   {self.venv_dir}\\Scripts\\activate")
        else:
            print(f"   source {self.venv_dir}/bin/activate")
        
        print("\n2. Run the application:")
        if sys.platform == 'win32':
            print("   run.bat")
        else:
            print("   ./run.sh")
        
        print("\n3. Open your browser and navigate to:")
        print("   http://localhost:5000")
        
        print("\n" + "="*70)
        print("For more information, see README.md")
        print("="*70 + "\n")
    
    def run(self):
        """Run complete setup"""
        self.print_banner()
        
        steps = [
            ("Python version", self.check_python_version),
            ("System dependencies", self.check_dependencies),
            ("Virtual environment", self.create_virtual_environment),
            ("Python packages", self.install_requirements),
            ("Directories", self.create_directories),
            ("Database", self.initialize_database),
            ("Startup scripts", self.create_startup_script),
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    print(f"\n✗ Setup failed at: {step_name}")
                    return False
            except Exception as e:
                print(f"\n✗ Unexpected error during {step_name}: {e}")
                return False
        
        self.print_completion()
        return True

def main():
    """Main entry point"""
    try:
        wizard = SetupWizard()
        success = wizard.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
