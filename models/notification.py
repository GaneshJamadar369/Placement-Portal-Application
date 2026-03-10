from models.base import db, TimestampMixin

class Notification(db.Model, TimestampMixin):
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info') # info, success, warning, danger
    is_read = db.Column(db.Boolean, default=False)
    
    # We establish the relationship dynamically backward from User
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic', cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Notification {self.title}>'
