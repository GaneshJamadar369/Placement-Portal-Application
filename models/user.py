from models.base import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    full_name = db.Column(db.String(120))
    password = db.Column(db.String(255))
    type = db.Column(db.String(20))  # 'admin', 'student', 'company'

    __mapper_args__ = {
    'polymorphic_on': type,
    'polymorphic_identity': 'user'
    }

    def set_password(self, password):
        """we will hashh the pass before saving :)"""
        self.password = generate_password_hash(password)
    def check_password(self, password):
        """verification """
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'User {self.email}'

class Admin(User):
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }
