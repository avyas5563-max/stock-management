from datetime import datetime
from app import db


class Supplier(db.Model):
    """Supplier model for managing suppliers"""
    __tablename__ = 'suppliers'
    
    supplier_id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(200), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    current_balance = db.Column(db.Float, nullable=False, default=0.0)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    purchases = db.relationship('Purchase', backref='supplier', lazy='dynamic')
    
    def __repr__(self):
        return f'<Supplier {self.supplier_name}>'
