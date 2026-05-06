# app/repositories/order_repository.py
"""Order data access layer"""

from app.extensions import db
from app.models.orders import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.order_status_history import OrderStatusHistory


class OrderRepository:
    """Abstracts all Order database operations"""

    @staticmethod
    def get_by_id(order_id):
        return Order.query.get(order_id)

    @staticmethod
    def get_by_customer(customer_id):
        return Order.query.filter_by(customer_id=customer_id)\
                         .order_by(Order.created_at.desc()).all()

    @staticmethod
    def create(order):
        db.session.add(order)
        db.session.flush()
        return order

    @staticmethod
    def create_order_item(order_item):
        db.session.add(order_item)
        return order_item

    @staticmethod
    def create_payment(payment):
        db.session.add(payment)
        return payment

    @staticmethod
    def create_status_history(history):
        db.session.add(history)
        return history

    @staticmethod
    def update_status(order, status):
        order.status = status
        db.session.add(order)
        return order

    @staticmethod
    def commit():
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
