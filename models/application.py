from models.base import db, TimestampMixin
from models.student import Student

class Application(db.Model, TimestampMixin):
    __tablename__ = 'application'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    status = db.Column(db.String(20), default='applied')  # applied/shortlisted/selected/rejected

    student = db.relationship('Student', backref='applications', lazy=True)
    drive = db.relationship('PlacementDrive', back_populates='applications', lazy=True)

    __table_args__ = (
       db.UniqueConstraint('student_id', 'drive_id', name='uq_student_drive'),
    )
