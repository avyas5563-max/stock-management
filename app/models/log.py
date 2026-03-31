from datetime import datetime
from app import db


class Log(db.Model):
    """Log model for tracking all user actions and changes"""
    __tablename__ = 'logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action_taken = db.Column(db.String(20), nullable=False)  # create, update, delete
    description = db.Column(db.Text, nullable=True)
    action_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Log {self.log_id}: {self.action_taken} on {self.table_name}>'
