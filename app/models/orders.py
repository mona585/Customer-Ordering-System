from enum import Enum
from app.extensions import db
from datetime import datetime


class OrderStatus(Enum):
    PENDING = "Pending"       # ← In cart / not paid yet
    CONFIRMED = "Confirmed"   # ← Paid, preparing
    PREPARING = "Preparing"
    READY = "Ready"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    delivery_address = db.Column(db.Text)
    special_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - شيلي الـ backref من هنا
    customer = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False)
    
    def __repr__(self):
        return f'<Order {self.id}>'