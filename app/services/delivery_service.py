# app/services/delivery_service.py
"""Delivery business logic - listing and advancing delivery orders"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from app.models.orders import Order, OrderStatus
from app.models.order_status_history import OrderStatusHistory
from app.repositories.order_repository import OrderRepository
from app.services.base_service import BaseService, ServiceResult
from app.services.order_lifecycle_service import OrderLifecycleService


# The subset of statuses that belong to the delivery pipeline
DELIVERY_PIPELINE = (
    OrderStatus.READY,
    OrderStatus.OUT_FOR_DELIVERY,
    OrderStatus.DELIVERED,
)

# Maps each delivery status to the next one in the pipeline
_NEXT_STATUS = {
    OrderStatus.READY:            OrderStatus.OUT_FOR_DELIVERY,
    OrderStatus.OUT_FOR_DELIVERY: OrderStatus.DELIVERED,
}

# Human-readable labels for delivery statuses
_STATUS_LABELS = {
    OrderStatus.READY:            "Ready for Pickup",
    OrderStatus.OUT_FOR_DELIVERY: "Out for Delivery",
    OrderStatus.DELIVERED:        "Delivered",
}


class DeliveryService(BaseService):
    """Handles delivery-side order management"""

    @staticmethod
    def list_delivery_orders(status_filter: str | None = None):
        try:
            filter_statuses = None

            if status_filter:
                try:
                    single = OrderStatus[status_filter.upper()]
                except KeyError:
                    return ServiceResult.fail(f"Unknown status: {status_filter}")

                if single not in DELIVERY_PIPELINE:
                    return ServiceResult.fail(
                        f"Status '{status_filter}' is not part of the delivery pipeline."
                    )
                filter_statuses = [single]

            orders = OrderRepository.list_for_delivery(statuses=filter_statuses)
            return ServiceResult.ok(data=orders)

        except Exception as e:
            logger.exception("Error listing delivery orders")
            return ServiceResult.fail(f"Error fetching delivery orders: {str(e)}")

    @staticmethod
    def advance_delivery_status(order_id: int):
        try:
            order = OrderRepository.get_by_id(order_id)
            if not order:
                return ServiceResult.fail("Order not found")

            if order.status not in _NEXT_STATUS:
                if order.status == OrderStatus.DELIVERED:
                    return ServiceResult.fail("Order has already been delivered.")
                return ServiceResult.fail(
                    f"Order is not in the delivery pipeline "
                    f"(current status: {order.status.value})."
                )

            next_status = _NEXT_STATUS[order.status]

            OrderRepository.update_status(order, next_status)
            OrderRepository.create_status_history(
                OrderStatusHistory(
                    order_id=order.id,
                    status=next_status.name,
                    changed_at=datetime.utcnow(),
                )
            )

            if OrderRepository.commit():
                OrderLifecycleService.on_status_change(order, next_status)
                return ServiceResult.ok(
                    message=f"Order #{order_id} updated to '{next_status.value}'."
                )
            return ServiceResult.fail("Database error while updating order status.")

        except Exception as e:
            logger.exception("Error advancing delivery status for order %s", order_id)
            return ServiceResult.fail(f"Error updating order status: {str(e)}")

    @staticmethod
    def delivery_status_label(status: OrderStatus) -> str:
        return _STATUS_LABELS.get(status, status.value)
