"""
Employee Management and Facial Recognition Service
Handles employee database, facial recognition training, and compliance tracking
"""

import os
import cv2
import numpy as np
import face_recognition
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class EmployeeService:
    """Service for managing employees and facial recognition"""

    def __init__(self, db_session, upload_folder='static/uploads/employees'):
        """
        Initialize employee service

        Args:
            db_session: Database session
            upload_folder: Folder for storing employee images
        """
        self.db = db_session
        self.upload_folder = Path(upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)

        # Initialize face recognition
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_employee_ids = []

        # Load existing employee data
        self._load_employee_data()

    def _load_employee_data(self):
        """Load existing employee face encodings"""
        try:
            from backend.database.models import Employee

            employees = Employee.query.filter_by(is_active=True).all()

            for employee in employees:
                if employee.face_encoding:
                    encoding = np.array(employee.face_encoding)
                    self.known_face_encodings.append(encoding)
                    self.known_face_names.append(employee.name)
                    self.known_employee_ids.append(employee.employee_id)

            logger.info(f"Loaded {len(self.known_face_encodings)} employee face encodings")

        except Exception as e:
            logger.error(f"Error loading employee data: {e}")

    def add_employee(self, employee_data: Dict, face_image=None) -> Tuple[bool, str]:
        """
        Add new employee to database

        Args:
            employee_data: Employee information
            face_image: Face image file for recognition training

        Returns:
            (success, employee_id or error_message)
        """
        try:
            from backend.database.models import Employee

            # Check if employee already exists
            existing = Employee.query.filter_by(
                employee_id=employee_data['employee_id']
            ).first()

            if existing:
                return False, "Employee ID already exists"

            # Process face image if provided
            face_encoding = None
            face_image_path = None

            if face_image:
                encoding, image_path = self._process_face_image(
                    face_image,
                    employee_data['employee_id']
                )
                face_encoding = encoding.tolist() if encoding is not None else None
                face_image_path = image_path

            # Create employee record
            employee = Employee(
                employee_id=employee_data['employee_id'],
                name=employee_data['name'],
                email=employee_data['email'],
                phone=employee_data.get('phone'),
                department=employee_data.get('department'),
                position=employee_data.get('position'),
                shift=employee_data.get('shift'),
                requires_helmet=employee_data.get('requires_helmet', True),
                requires_vest=employee_data.get('requires_vest', True),
                requires_gloves=employee_data.get('requires_gloves', False),
                requires_boots=employee_data.get('requires_boots', False),
                face_encoding=face_encoding,
                face_image_path=face_image_path,
                emergency_contact_name=employee_data.get('emergency_contact_name'),
                emergency_contact_phone=employee_data.get('emergency_contact_phone'),
                emergency_contact_email=employee_data.get('emergency_contact_email'),
                is_active=True
            )

            self.db.session.add(employee)
            self.db.session.commit()

            # Update face recognition data
            if face_encoding:
                self.known_face_encodings.append(np.array(face_encoding))
                self.known_face_names.append(employee.name)
                self.known_employee_ids.append(employee.employee_id)

            logger.info(f"Added employee: {employee.name} ({employee.employee_id})")
            return True, employee.employee_id

        except Exception as e:
            logger.error(f"Error adding employee: {e}")
            self.db.session.rollback()
            return False, str(e)

    def _process_face_image(self, image_file, employee_id: str) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Process face image for recognition

        Args:
            image_file: Uploaded image file
            employee_id: Employee ID for filename

        Returns:
            (face_encoding, image_path)
        """
        try:
            # Save image
            filename = f"{employee_id}_face_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
            image_path = self.upload_folder / filename
            image_file.save(str(image_path))

            # Load and process image
            image = face_recognition.load_image_file(str(image_path))
            face_encodings = face_recognition.face_encodings(image)

            if len(face_encodings) == 0:
                # Remove saved image if no face found
                os.remove(str(image_path))
                return None, None

            if len(face_encodings) > 1:
                logger.warning(f"Multiple faces detected in image for {employee_id}, using first one")

            # Use the first face encoding
            return face_encodings[0], str(image_path)

        except Exception as e:
            logger.error(f"Error processing face image: {e}")
            return None, None

    def recognize_employee(self, frame) -> List[Dict]:
        """
        Recognize employees in frame

        Args:
            frame: Video frame (numpy array)

        Returns:
            List of recognized employees with compliance status
        """
        try:
            # Convert BGR to RGB for face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Find faces in frame
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            recognized_employees = []

            for face_encoding, face_location in zip(face_encodings, face_locations):
                # Compare with known faces
                matches = face_recognition.compare_faces(
                    self.known_face_encodings,
                    face_encoding,
                    tolerance=0.6  # Adjust tolerance as needed
                )

                face_distances = face_recognition.face_distance(
                    self.known_face_encodings,
                    face_encoding
                )

                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        employee_id = self.known_employee_ids[best_match_index]
                        confidence = 1 - face_distances[best_match_index]

                        # Get employee details
                        employee = self._get_employee_by_id(employee_id)
                        if employee:
                            # Check safety compliance
                            compliance = self._check_compliance(frame, face_location, employee)

                            recognized_employee = {
                                'employee_id': employee_id,
                                'name': employee.name,
                                'face_location': face_location,
                                'confidence': float(confidence),
                                'compliance': compliance,
                                'department': employee.department,
                                'requires_helmet': employee.requires_helmet
                            }

                            recognized_employees.append(recognized_employee)

                            # Update last seen
                            employee.last_seen = datetime.utcnow()
                            self.db.session.commit()

            return recognized_employees

        except Exception as e:
            logger.error(f"Error recognizing employees: {e}")
            return []

    def _get_employee_by_id(self, employee_id: str):
        """Get employee by ID"""
        try:
            from backend.database.models import Employee
            return Employee.query.filter_by(employee_id=employee_id, is_active=True).first()
        except Exception as e:
            logger.error(f"Error getting employee {employee_id}: {e}")
            return None

    def _check_compliance(self, frame, face_location, employee) -> Dict:
        """
        Check safety equipment compliance for employee

        Args:
            frame: Video frame
            face_location: Face location (top, right, bottom, left)
            employee: Employee object

        Returns:
            Compliance status dictionary
        """
        try:
            # Use existing safety detection for helmet
            from safety_detection import SafetyDetector
            detector = SafetyDetector()

            # Get region around employee (expand face location)
            top, right, bottom, left = face_location
            height, width = frame.shape[:2]

            # Expand region to include upper body
            expand_factor = 2.5
            center_x = (left + right) // 2
            center_y = (top + bottom) // 2

            region_left = max(0, center_x - int((right - left) * expand_factor))
            region_right = min(width, center_x + int((right - left) * expand_factor))
            region_top = max(0, center_y - int((bottom - top) * expand_factor))
            region_bottom = min(height, center_y + int((bottom - top) * expand_factor))

            employee_region = frame[region_top:region_bottom, region_left:region_right]

            if employee_region.size == 0:
                return {'status': 'unknown', 'violations': ['region_extraction_failed']}

            # Detect helmets in employee region
            gray = cv2.cvtColor(employee_region, cv2.COLOR_BGR2GRAY)
            helmets = detector._detect_helmets(gray, employee_region)

            compliance = {
                'helmet_compliant': len(helmets) > 0 if employee.requires_helmet else True,
                'vest_compliant': True,  # Placeholder - would need vest detection
                'gloves_compliant': True,  # Placeholder
                'boots_compliant': True,  # Placeholder
                'violations': []
            }

            # Determine overall status
            if employee.requires_helmet and not compliance['helmet_compliant']:
                compliance['violations'].append('missing_helmet')

            compliance['status'] = 'compliant' if not compliance['violations'] else 'non_compliant'

            return compliance

        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            return {'status': 'error', 'violations': [str(e)]}

    def update_employee_training_data(self, employee_id: str, image_type: str, image_file) -> bool:
        """
        Add training image for employee

        Args:
            employee_id: Employee ID
            image_type: 'helmet' or 'no_helmet'
            image_file: Training image file

        Returns:
            Success status
        """
        try:
            from backend.database.models import Employee

            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if not employee:
                return False

            # Save training image
            filename = f"{employee_id}_{image_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
            image_path = self.upload_folder / "training" / filename
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image_file.save(str(image_path))

            # Update training data
            if image_type == 'helmet':
                training_images = employee.helmet_training_images or []
                training_images.append(str(image_path))
                employee.helmet_training_images = training_images
            elif image_type == 'no_helmet':
                training_images = employee.no_helmet_training_images or []
                training_images.append(str(image_path))
                employee.no_helmet_training_images = training_images

            self.db.session.commit()
            return True

        except Exception as e:
            logger.error(f"Error updating training data: {e}")
            return False

    def get_employee_stats(self, employee_id: str) -> Dict:
        """Get employee compliance statistics"""
        try:
            from backend.database.models import Employee, EmployeeRecognition

            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if not employee:
                return {}

            # Get recognition history
            recognitions = EmployeeRecognition.query.filter_by(employee_id=employee_id).all()

            total_recognitions = len(recognitions)
            compliant_recognitions = sum(1 for r in recognitions if r.compliance_status == 'compliant')
            violation_recognitions = total_recognitions - compliant_recognitions

            compliance_rate = (compliant_recognitions / total_recognitions * 100) if total_recognitions > 0 else 0

            return {
                'employee_id': employee_id,
                'name': employee.name,
                'total_recognitions': total_recognitions,
                'compliant_recognitions': compliant_recognitions,
                'violation_recognitions': violation_recognitions,
                'compliance_rate': compliance_rate,
                'total_violations': employee.total_violations,
                'last_seen': employee.last_seen.isoformat() if employee.last_seen else None
            }

        except Exception as e:
            logger.error(f"Error getting employee stats: {e}")
            return {}