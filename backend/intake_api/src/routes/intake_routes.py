"""
API routes for handling Business Intake form submissions.
"""
from flask import Blueprint, request, jsonify
from ..models.intake import BusinessIntake, db # Assuming db is accessible here
from datetime import datetime

intake_bp = Blueprint(
    'intake_bp',
    __name__
)

@intake_bp.route('/', methods=['POST'])
def create_intake():
    """Creates a new, empty intake record."""
    data = request.get_json() or {}
    business_name = data.get('business_name')
    contact_email = data.get('contact_email')

    new_intake = BusinessIntake(
        business_name=business_name,
        contact_email=contact_email,
        answers_data={},
        status='draft'
    )
    db.session.add(new_intake)
    db.session.commit()
    return jsonify(new_intake.to_dict()), 201

@intake_bp.route('/<int:intake_id>', methods=['GET'])
def get_intake(intake_id):
    """Retrieves an existing intake record by its ID."""
    intake = BusinessIntake.query.get(intake_id)
    if not intake:
        return jsonify({'message': 'Intake not found'}), 404
    return jsonify(intake.to_dict()), 200

@intake_bp.route('/<int:intake_id>', methods=['PUT'])
def update_intake(intake_id):
    """Updates an existing intake record (e.g., saving a draft or submitting)."""
    intake = BusinessIntake.query.get(intake_id)
    if not intake:
        return jsonify({'message': 'Intake not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided for update'}), 400

    # Update specific fields if provided
    if 'business_name' in data:
        intake.business_name = data['business_name']
    if 'contact_email' in data:
        intake.contact_email = data['contact_email']
    if 'answers_data' in data:
        # For drafts, we merge. For submissions, this might be the final set.
        if isinstance(data['answers_data'], dict):
            if intake.answers_data:
                intake.answers_data.update(data['answers_data'])
            else:
                intake.answers_data = data['answers_data']
        else:
            return jsonify({'message': 'answers_data must be a dictionary'}), 400
            
    if 'status' in data and data['status'] in ['draft', 'submitted']:
        intake.status = data['status']
        if data['status'] == 'submitted':
            intake.submitted_at = datetime.utcnow()
    
    intake.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(intake.to_dict()), 200

# Placeholder for a route to get all intakes (optional, for admin purposes)
@intake_bp.route('/', methods=['GET'])
def list_intakes():
    """Lists all intake records (consider pagination for many records)."""
    # This is a simple implementation. Add pagination and filtering for production.
    intakes = BusinessIntake.query.all()
    return jsonify([intake.to_dict() for intake in intakes]), 200

