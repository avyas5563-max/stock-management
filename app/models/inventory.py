from datetime import datetime
from app import db


class Inventory(db.Model):
    """Inventory model for tracking current stock levels"""
    __tablename__ = 'inventory'
    
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), primary_key=True)
    current_stock = db.Column(db.Float, nullable=False, default=0.0)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item = db.relationship('Item', foreign_keys=[item_id])
    
    def is_low_stock(self):
        """Check if stock is below minimum threshold"""
        if self.item:
            return self.current_stock < self.item.min_stock
        return False
    
    def __repr__(self):
        return f'<Inventory Item:{self.item_id} Stock:{self.current_stock}>'
