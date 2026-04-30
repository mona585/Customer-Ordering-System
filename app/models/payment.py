# app/models/payment.py

from enum import Enum
from app.extensions import db
from datetime import datetime


class PaymentStatus(Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"


class PaymentMethod(Enum):
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    CASH = "Cash on Delivery"


class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.Enum(PaymentMethod), nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    transaction_id = db.Column(db.String(100))  # From payment gateway
    card_last_four = db.Column(db.String(4))    # Tokenized - NEVER store full card
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.status.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': float(self.amount),
            'method': self.method.value,
            'status': self.status.value,
            'transaction_id': self.transaction_id,
            'card_last_four': self.card_last_four,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def mark_completed(self, transaction_id=None):
        """Mark payment as completed"""
        self.status = PaymentStatus.COMPLETED
        self.paid_at = datetime.utcnow()
        if transaction_id:
            self.transaction_id = transaction_id
    
    def mark_failed(self):
        """Mark payment as failed"""
        self.status = PaymentStatus.FAILED