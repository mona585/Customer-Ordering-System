from app.extensions import db
from datetime import datetime


class OrderStatusHistory(db.Model):
    """Track order status changes over time"""
    __tablename__ = 'order_status_history'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<OrderStatusHistory {self.order_id}: {self.status}>'