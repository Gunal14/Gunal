"""
Employee Management API Routes
CRUD operations for employees, facial recognition training, and compliance tracking
"""

from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

employee_bp = Blueprint('employee', __name__, url_prefix='/api/v1/employees')

# ============================================================================
# EMPLOYEE MANAGEMENT ENDPOINTS
# ============================================================================

@employee_bp.route('', methods=['GET'])
@cross_origin()
def get_employees():
    """
    Get all employees with optional filtering
    ---
    parameters:
      - name: department
        in: query
        type: string
        description: Filter by department
      - name: active_only
        in: query
        type: boolean
        default: true
        description: Only return active employees
    responses:
      200:
        description: List of employees
    """
    try:
        from backend.database.models import Employee, db

        # Parse query parameters
        department = request.args.get('department')
        active_only = request.args.get('active_only', 'true').lower() == 'true'

        # Build query
        query = Employee.query
        if department:
            query = query.filter_by(department=department)
        if active_only:
            query = query.filter_by(is_active=True)

        employees = query.all()

        return jsonify({
            'success': True,
            'count': len(employees),
            'employees': [
                {
                    'employee_id': emp.employee_id,
                    'name': emp.name,
                    'email': emp.email,
                    'phone': emp.phone,
                    'department': emp.department,
                    'position': emp.position,
                    'shift': emp.shift,
                    'requires_helmet': emp.requires_helmet,
                    'requires_vest': emp.requires_vest,
                    'requires_gloves': emp.requires_gloves,
                    'requires_boots': emp.requires_boots,
                    'compliance_score': emp.compliance_score,
                    'total_violations': emp.total_violations,
                    'last_seen': emp.last_seen.isoformat() if emp.last_seen else None,
                    'is_active': emp.is_active,
                    'created_at': emp.created_at.isoformat(),
                    'emergency_contact_name': emp.emergency_contact_name,
                    'emergency_contact_phone': emp.emergency_contact_phone,
                    'emergency_contact_email': emp.emergency_contact_email
                }
                for emp in employees
            ]
        })

    except Exception as e:
        logger.error(f"Error fetching employees: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('', methods=['POST'])
@cross_origin()
def add_employee():
    """
    Add new employee
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: employee_id
        in: formData
        type: string
        required: true
      - name: name
        in: formData
        type: string
        required: true
      - name: email
        in: formData
        type: string
        required: true
      - name: phone
        in: formData
        type: string
      - name: department
        in: formData
        type: string
      - name: position
        in: formData
        type: string
      - name: shift
        in: formData
        type: string
      - name: requires_helmet
        in: formData
        type: boolean
        default: true
      - name: requires_vest
        in: formData
        type: boolean
        default: true
      - name: requires_gloves
        in: formData
        type: boolean
        default: false
      - name: requires_boots
        in: formData
        type: boolean
        default: false
      - name: emergency_contact_name
        in: formData
        type: string
      - name: emergency_contact_phone
        in: formData
        type: string
      - name: emergency_contact_email
        in: formData
        type: string
      - name: face_image
        in: formData
        type: file
        description: Face image for recognition training
    responses:
      201:
        description: Employee added successfully
    """
    try:
        from backend.services.employee_service import EmployeeService
        from backend.database.models import db

        # Get form data
        employee_data = {
            'employee_id': request.form.get('employee_id'),
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'department': request.form.get('department'),
            'position': request.form.get('position'),
            'shift': request.form.get('shift'),
            'requires_helmet': request.form.get('requires_helmet', 'true').lower() == 'true',
            'requires_vest': request.form.get('requires_vest', 'true').lower() == 'true',
            'requires_gloves': request.form.get('requires_gloves', 'false').lower() == 'true',
            'requires_boots': request.form.get('requires_boots', 'false').lower() == 'true',
            'emergency_contact_name': request.form.get('emergency_contact_name'),
            'emergency_contact_phone': request.form.get('emergency_contact_phone'),
            'emergency_contact_email': request.form.get('emergency_contact_email')
        }

        # Validate required fields
        if not all([employee_data['employee_id'], employee_data['name'], employee_data['email']]):
            return jsonify({
                'success': False,
                'error': 'employee_id, name, and email are required'
            }), 400

        # Get face image if provided
        face_image = request.files.get('face_image')

        # Initialize employee service
        employee_service = EmployeeService(db.session)

        # Add employee
        success, result = employee_service.add_employee(employee_data, face_image)

        if success:
            return jsonify({
                'success': True,
                'message': 'Employee added successfully',
                'employee_id': result
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result
            }), 400

    except Exception as e:
        logger.error(f"Error adding employee: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/<employee_id>', methods=['GET'])
@cross_origin()
def get_employee(employee_id):
    """
    Get employee details
    ---
    parameters:
      - name: employee_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Employee details
    """
    try:
        from backend.database.models import Employee

        employee = Employee.query.filter_by(employee_id=employee_id).first()

        if not employee:
            return jsonify({'success': False, 'error': 'Employee not found'}), 404

        return jsonify({
            'success': True,
            'employee': {
                'employee_id': employee.employee_id,
                'name': employee.name,
                'email': employee.email,
                'phone': employee.phone,
                'department': employee.department,
                'position': employee.position,
                'shift': employee.shift,
                'requires_helmet': employee.requires_helmet,
                'requires_vest': employee.requires_vest,
                'requires_gloves': employee.requires_gloves,
                'requires_boots': employee.requires_boots,
                'compliance_score': employee.compliance_score,
                'total_violations': employee.total_violations,
                'last_seen': employee.last_seen.isoformat() if employee.last_seen else None,
                'is_active': employee.is_active,
                'created_at': employee.created_at.isoformat(),
                'emergency_contact_name': employee.emergency_contact_name,
                'emergency_contact_phone': employee.emergency_contact_phone,
                'emergency_contact_email': employee.emergency_contact_email,
                'face_image_path': employee.face_image_path,
                'helmet_training_images': employee.helmet_training_images,
                'no_helmet_training_images': employee.no_helmet_training_images
            }
        })

    except Exception as e:
        logger.error(f"Error fetching employee: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/<employee_id>', methods=['PUT'])
@cross_origin()
def update_employee(employee_id):
    """
    Update employee details
    ---
    parameters:
      - name: employee_id
        in: path
        type: string
        required: true
    consumes:
      - application/json
    responses:
      200:
        description: Employee updated successfully
    """
    try:
        from backend.database.models import Employee, db

        employee = Employee.query.filter_by(employee_id=employee_id).first()

        if not employee:
            return jsonify({'success': False, 'error': 'Employee not found'}), 404

        data = request.get_json()

        # Update fields
        for field in ['name', 'email', 'phone', 'department', 'position', 'shift',
                     'requires_helmet', 'requires_vest', 'requires_gloves', 'requires_boots',
                     'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_email']:
            if field in data:
                setattr(employee, field, data[field])

        if 'is_active' in data:
            employee.is_active = data['is_active']

        db.session.commit()

        logger.info(f"Updated employee: {employee.name}")

        return jsonify({
            'success': True,
            'message': 'Employee updated successfully'
        })

    except Exception as e:
        logger.error(f"Error updating employee: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/<employee_id>', methods=['DELETE'])
@cross_origin()
def delete_employee(employee_id):
    """
    Deactivate employee (soft delete)
    ---
    parameters:
      - name: employee_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Employee deactivated successfully
    """
    try:
        from backend.database.models import Employee, db

        employee = Employee.query.filter_by(employee_id=employee_id).first()

        if not employee:
            return jsonify({'success': False, 'error': 'Employee not found'}), 404

        employee.is_active = False
        db.session.commit()

        logger.info(f"Deactivated employee: {employee.name}")

        return jsonify({
            'success': True,
            'message': 'Employee deactivated successfully'
        })

    except Exception as e:
        logger.error(f"Error deactivating employee: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/<employee_id>/training', methods=['POST'])
@cross_origin()
def add_training_image(employee_id):
    """
    Add training image for employee
    ---
    parameters:
      - name: employee_id
        in: path
        type: string
        required: true
    consumes:
      - multipart/form-data
    parameters:
      - name: image_type
        in: formData
        type: string
        enum: [helmet, no_helmet]
        required: true
      - name: image
        in: formData
        type: file
        required: true
    responses:
      200:
        description: Training image added successfully
    """
    try:
        from backend.services.employee_service import EmployeeService
        from backend.database.models import db

        # Validate image type
        image_type = request.form.get('image_type')
        if image_type not in ['helmet', 'no_helmet']:
            return jsonify({
                'success': False,
                'error': 'image_type must be "helmet" or "no_helmet"'
            }), 400

        # Get image file
        image_file = request.files.get('image')
        if not image_file:
            return jsonify({
                'success': False,
                'error': 'Image file is required'
            }), 400

        # Initialize employee service
        employee_service = EmployeeService(db.session)

        # Add training image
        success = employee_service.update_employee_training_data(
            employee_id, image_type, image_file
        )

        if success:
            return jsonify({
                'success': True,
                'message': f'Training image added for {image_type} detection'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add training image'
            }), 400

    except Exception as e:
        logger.error(f"Error adding training image: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/<employee_id>/stats', methods=['GET'])
@cross_origin()
def get_employee_stats(employee_id):
    """
    Get employee compliance statistics
    ---
    parameters:
      - name: employee_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Employee statistics
    """
    try:
        from backend.services.employee_service import EmployeeService
        from backend.database.models import db

        employee_service = EmployeeService(db.session)
        stats = employee_service.get_employee_stats(employee_id)

        if stats:
            return jsonify({
                'success': True,
                'stats': stats
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Employee not found or no statistics available'
            }), 404

    except Exception as e:
        logger.error(f"Error fetching employee stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/stats/overview', methods=['GET'])
@cross_origin()
def get_employees_overview():
    """
    Get overview statistics for all employees
    ---
    responses:
      200:
        description: Employee overview statistics
    """
    try:
        from backend.database.models import Employee, EmployeeRecognition
        from sqlalchemy import func

        # Get total employees
        total_employees = Employee.query.filter_by(is_active=True).count()

        # Get compliance statistics
        employees = Employee.query.filter_by(is_active=True).all()

        compliance_data = []
        for emp in employees:
            # Get recent recognitions (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recognitions = EmployeeRecognition.query.filter(
                EmployeeRecognition.employee_id == emp.employee_id,
                EmployeeRecognition.timestamp >= thirty_days_ago
            ).all()

            if recognitions:
                compliant = sum(1 for r in recognitions if r.compliance_status == 'compliant')
                compliance_rate = (compliant / len(recognitions)) * 100
                compliance_data.append({
                    'employee_id': emp.employee_id,
                    'name': emp.name,
                    'compliance_rate': compliance_rate,
                    'total_recognitions': len(recognitions),
                    'total_violations': emp.total_violations
                })

        # Calculate overall statistics
        avg_compliance = sum(d['compliance_rate'] for d in compliance_data) / len(compliance_data) if compliance_data else 0
        high_risk_employees = sum(1 for d in compliance_data if d['compliance_rate'] < 70)

        return jsonify({
            'success': True,
            'overview': {
                'total_employees': total_employees,
                'employees_with_data': len(compliance_data),
                'average_compliance_rate': avg_compliance,
                'high_risk_employees': high_risk_employees,
                'compliance_distribution': compliance_data
            }
        })

    except Exception as e:
        logger.error(f"Error fetching employee overview: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500