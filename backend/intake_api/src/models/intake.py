"""
Database models for the Business Intake form.
"""
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .user import db  # Assuming db = SQLAlchemy() is initialized in src/models/user.py or a base file

class BusinessIntake(db.Model):
    __tablename__ = 'business_intakes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Optional: Link to a user if user accounts are implemented later
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    business_name = db.Column(db.String(255), nullable=True)
    contact_email = db.Column(db.String(255), nullable=True)

    # Stores all form answers as a JSON object
    # The structure of this JSON will correspond to intake_form_questions_v3.md
    answers_data = db.Column(JSONB, nullable=False, default=lambda: {})
    
    # Status of the intake form, e.g., 'draft', 'submitted'
    status = db.Column(db.String(50), nullable=False, default='draft')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<BusinessIntake id={self.id} business_name=\"{self.business_name}\" status=\"{self.status}\">' 

    def to_dict(self):
        return {
            'id': self.id,
            'business_name': self.business_name,
            'contact_email': self.contact_email,
            'answers_data': self.answers_data,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }

