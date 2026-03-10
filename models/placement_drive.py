from models.base import db, TimestampMixin
from models.company import Company

class PlacementDrive(db.Model, TimestampMixin):
    __tablename__ = 'placement_drive'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    job_title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    salary = db.Column(db.Float)
    positions = db.Column(db.Integer)
    eligibility = db.Column(db.String(120))
    location = db.Column(db.String(100))
    job_type = db.Column(db.String(50))
    min_cgpa = db.Column(db.Float)

    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending/approved/closed

    company = db.relationship('Company', backref='placement_drives')

    def __repr__(self):
        return f'<Drive {self.job_title} at {self.company.full_name}>'


#this is forrr 1 job multiple candidatess

    applications = db.relationship(
        'Application',
        back_populates='drive',
        lazy=True,
        cascade='all, delete-orphan'  # If a drive is deleted, all its applications are also deleted automatically.
    )
