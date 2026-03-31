from datetime import datetime
from app import db


class Money(db.Model):
    """Money transaction model for tracking all financial transactions"""
    __tablename__ = 'money'
    
    transaction_id = db.Column(db.Integer, primary_key=True)
    reference_type = db.Column(db.String(20), nullable=False)  # purchase, sale, expense
    reference_id = db.Column(db.Integer, nullable=False)  # ID of purchase/sale/expense
    party_type = db.Column(db.String(20), nullable=False)  # customer, supplier
    party_id = db.Column(db.Integer, nullable=False)  # customer_id or supplier_id
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    advance_payment = db.Column(db.Float, nullable=False, default=0.0)
    payment_type = db.Column(db.String(20), nullable=False)  # cash, card, bank_transfer, cheque
    pay_status = db.Column(db.String(20), nullable=False, default='pending')  # paid, pending, partial
    due_date = db.Column(db.Date, nullable=True)
    reminder_date = db.Column(db.Date, nullable=True)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Money Transaction:{self.transaction_id} Type:{self.reference_type}>'
