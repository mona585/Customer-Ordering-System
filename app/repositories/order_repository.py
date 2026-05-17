# app/repositories/order_repository.py
"""Order data access layer"""

from sqlalchemy.orm import joinedload, selectinload

from app.extensions import db
from app.models.orders import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.order_status_history import OrderStatusHistory


class OrderRepository:
    """Abstracts all Order database operations"""

    @staticmethod
    def get_by_id(order_id):
        return db.session.get(Order, order_id)

    @staticmethod
    def get_by_id_with_relations(order_id):
        """Order with customer, line items (+ menu item), status history, payment."""
        return (
            Order.query.options(
                joinedload(Order.customer),
                selectinload(Order.items).joinedload(OrderItem.menu_item),
                selectinload(Order.status_history),
                joinedload(Order.payment),
            )
            .filter_by(id=order_id)
            .first()
        )

    @staticmethod
    def list_for_admin(status: OrderStatus | None = None, limit: int = 200):
        q = Order.query.options(
            joinedload(Order.customer),
            selectinload(Order.items).joinedload(OrderItem.menu_item),
        ).order_by(Order.created_at.desc())
        if status is not None:
            q = q.filter(Order.status == status)
        return q.limit(limit).all()

    @staticmethod
    def list_for_delivery(statuses: list[OrderStatus] | None = None, limit: int = 200):
        """Orders in the delivery pipeline (ready → out for delivery → delivered)."""
        delivery_statuses = statuses or [
            OrderStatus.READY,
            OrderStatus.OUT_FOR_DELIVERY,
            OrderStatus.DELIVERED,
        ]
        return (
            Order.query.options(joinedload(Order.customer))
            .filter(Order.status.in_(delivery_statuses))
            .order_by(Order.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_customer(customer_id):
        return (
            Order.query.options(
                selectinload(Order.items).joinedload(OrderItem.menu_item),
            )
            .filter_by(customer_id=customer_id)
            .order_by(Order.created_at.desc())
            .all()
        )

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
