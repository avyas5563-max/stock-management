from datetime import datetime
from app import db


class Item(db.Model):
    """Item model for inventory items"""
    __tablename__ = 'items'
    
    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    unit = db.Column(db.String(50), nullable=False)  # kg, pcs, ltr, etc.
    purchase_price = db.Column(db.Float, nullable=False, default=0.0)
    sale_price = db.Column(db.Float, nullable=False, default=0.0)
    min_stock = db.Column(db.Float, nullable=False, default=0.0)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    purchase_items = db.relationship('PurchaseItem', backref='item', lazy='dynamic')
    sale_items = db.relationship('SaleItem', backref='item', lazy='dynamic')
    inventory = db.relationship('Inventory', uselist=False, viewonly=True)
    
    def __repr__(self):
        return f'<Item {self.item_name}>'
