#!/usr/bin/env python3
"""
Employee Database Setup and Sample Data Population
Run this script to initialize the employee database with sample data
Usage: python setup_employee_database.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)

def setup_employee_database():
    """Setup employee database with sample data"""
    try:
        # Initialize Flask app context for database operations
        from backend.database.models import db, Employee
        from config import Config

        config = Config()
        app = config.create_app()

        with app.app_context():
            # Create all tables
            db.create_all()
            logger.info("✅ Database tables created")

            # Check if sample data already exists
            existing_count = Employee.query.count()
            if existing_count > 0:
                logger.info(f"Sample data already exists ({existing_count} employees)")
                return

            # Sample employee data
            sample_employees = [
                {
                    'employee_id': 'EMP001',
                    'name': 'John Smith',
                    'email': 'john.smith@company.com',
                    'phone': '+1234567890',
                    'department': 'Construction',
                    'position': 'Site Supervisor',
                    'shift': 'Morning',
                    'requires_helmet': True,
                    'requires_vest': True,
                    'requires_gloves': True,
                    'requires_boots': True,
                    'emergency_contact_name': 'Jane Smith',
                    'emergency_contact_phone': '+1234567891',
                    'emergency_contact_email': 'jane.smith@email.com'
                },
                {
                    'employee_id': 'EMP002',
                    'name': 'Sarah Johnson',
                    'email': 'sarah.johnson@company.com',
                    'phone': '+1234567892',
                    'department': 'Construction',
                    'position': 'Safety Officer',
                    'shift': 'Afternoon',
                    'requires_helmet': True,
                    'requires_vest': True,
                    'requires_gloves': True,
                    'requires_boots': True,
                    'emergency_contact_name': 'Mike Johnson',
                    'emergency_contact_phone': '+1234567893',
                    'emergency_contact_email': 'mike.johnson@email.com'
                },
                {
                    'employee_id': 'EMP003',
                    'name': 'David Brown',
                    'email': 'david.brown@company.com',
                    'phone': '+1234567894',
                    'department': 'Maintenance',
                    'position': 'Electrician',
                    'shift': 'Night',
                    'requires_helmet': True,
                    'requires_vest': True,
                    'requires_gloves': True,
                    'requires_boots': True,
                    'emergency_contact_name': 'Lisa Brown',
                    'emergency_contact_phone': '+1234567895',
                    'emergency_contact_email': 'lisa.brown@email.com'
                },
                {
                    'employee_id': 'EMP004',
                    'name': 'Maria Garcia',
                    'email': 'maria.garcia@company.com',
                    'phone': '+1234567896',
                    'department': 'Construction',
                    'position': 'Laborer',
                    'shift': 'Morning',
                    'requires_helmet': True,
                    'requires_vest': True,
                    'requires_gloves': True,
                    'requires_boots': True,
                    'emergency_contact_name': 'Carlos Garcia',
                    'emergency_contact_phone': '+1234567897',
                    'emergency_contact_email': 'carlos.garcia@email.com'
                },
                {
                    'employee_id': 'EMP005',
                    'name': 'Robert Wilson',
                    'email': 'robert.wilson@company.com',
                    'phone': '+1234567898',
                    'department': 'Maintenance',
                    'position': 'Plumber',
                    'shift': 'Afternoon',
                    'requires_helmet': True,
                    'requires_vest': True,
                    'requires_gloves': True,
                    'requires_boots': True,
                    'emergency_contact_name': 'Anna Wilson',
                    'emergency_contact_phone': '+1234567899',
                    'emergency_contact_email': 'anna.wilson@email.com'
                }
            ]

            # Add sample employees
            for emp_data in sample_employees:
                employee = Employee(**emp_data)
                db.session.add(employee)

            db.session.commit()
            logger.info(f"✅ Added {len(sample_employees)} sample employees")

            # Create training data directories
            training_dir = Path('static/uploads/employees/training')
            training_dir.mkdir(parents=True, exist_ok=True)

            # Create sample training data instructions
            instructions_file = training_dir / 'README.md'
            instructions_content = """
# Employee Training Data

This directory should contain training images for employee recognition and helmet detection.

## Directory Structure:
- `EMP001_helmet_*.jpg` - Images of EMP001 wearing helmet
- `EMP001_no_helmet_*.jpg` - Images of EMP001 without helmet
- `EMP002_helmet_*.jpg` - Images of EMP002 wearing helmet
- etc.

## Instructions:
1. Take multiple photos of each employee from different angles
2. Include both helmet and no-helmet images for training
3. Ensure good lighting and clear face visibility
4. Use the web interface to upload training images

## Sample Data:
The system will work with basic face detection initially.
Upload employee face photos through the web interface for better recognition.
"""

            with open(instructions_file, 'w') as f:
                f.write(instructions_content)

            logger.info("✅ Training data directory and instructions created")
            logger.info("✅ Employee database setup complete!")

            print("\n" + "="*60)
            print("EMPLOYEE DATABASE SETUP COMPLETE")
            print("="*60)
            print("Sample employees added:")
            for emp in sample_employees:
                print(f"  • {emp['name']} ({emp['employee_id']}) - {emp['department']}")
            print("\nNext steps:")
            print("1. Upload face images for employees via the web interface")
            print("2. Add training images (with/without helmets)")
            print("3. Configure notification settings")
            print("4. Start the enhanced monitoring system")
            print("="*60 + "\n")

    except Exception as e:
        logger.error(f"❌ Error setting up employee database: {e}")
        print(f"Error: {e}")
        sys.exit(1)

def create_sample_training_data():
    """Create sample training data structure"""
    try:
        training_dir = Path('static/uploads/employees/training')

        # Create sample data files (placeholders)
        sample_files = [
            'EMP001_helmet_sample.jpg',
            'EMP001_no_helmet_sample.jpg',
            'EMP002_helmet_sample.jpg',
            'EMP002_no_helmet_sample.jpg',
        ]

        for filename in sample_files:
            filepath = training_dir / filename
            # Create empty placeholder files
            with open(filepath, 'w') as f:
                f.write("# Placeholder training image\n")
                f.write("# Replace with actual employee photos\n")

        logger.info("✅ Sample training data placeholders created")

    except Exception as e:
        logger.error(f"Error creating sample training data: {e}")

if __name__ == "__main__":
    print("Setting up employee database...")
    setup_employee_database()
    create_sample_training_data()
    print("Setup complete!")