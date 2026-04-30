# app/models/order.py

from enum import Enum
from app.extensions import db
from datetime import datetime


class OrderStatus(Enum):
    PENDING = "Pending"           # Cart created, not paid
    CONFIRMED = "Confirmed"       # Payment successful
    PREPARING = "Preparing"       # Kitchen started
    READY = "Ready"               # Food ready
    DELIVERED = "Delivered"       # Customer received
    CANCELLED = "Cancelled"       # Cancelled


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    delivery_address = db.Column(db.Text)
    special_instructions = db.Column(db.Text)
    estimated_ready_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id} - {self.status.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'total_amount': float(self.total_amount),
            'status': self.status.value,
            'delivery_address': self.delivery_address,
            'special_instructions': self.special_instructions,
            'estimated_ready_time': self.estimated_ready_time.isoformat() if self.estimated_ready_time else None,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calculate_total(self):
        """Calculate total from items (server-side, don't trust client)"""
        total = sum(item.subtotal for item in self.items)
        self.total_amount = total
        return total