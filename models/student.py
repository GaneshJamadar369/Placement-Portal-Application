from models.base import db
from flask_login import UserMixin
from models.user import User

class Student(User):
    __tablename__ = 'student'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    roll_number = db.Column(db.String(20), unique=True)
    branch = db.Column(db.String(50))
    cgpa = db.Column(db.Float)
    phone = db.Column(db.String(20))
    resume_url = db.Column(db.String(255))
    cover_letter = db.Column(db.Text, nullable=True)
    final_offer_drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=True)
    final_offer_drive = db.relationship('PlacementDrive', foreign_keys=[final_offer_drive_id])

    # thiss is for singlee table inheritanceee
    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }
    
    
    def __repr__(self):
        return f'<Student {self.full_name}>'

    def selected_count(self):
        from models.application import Application
        return Application.query.filter_by(
            student_id=self.id,
            status='selected'
        ).count()

    