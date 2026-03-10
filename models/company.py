from models.base import db
from flask_login import UserMixin
from models.user import User

class Company(User):  # Inherits from Userrr
    __tablename__ = 'company'  # Separate tableee
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    cin = db.Column(db.String(21), unique=True)  # Company ID Numberrr
    sector = db.Column(db.String(120))
    approval_status = db.Column(db.String(20), default='pending')  # pending/approved
    __mapper_args__ = {
        'polymorphic_identity': 'company',
    }
    def __repr__(self):
        return f'<Company {self.full_name}>'
