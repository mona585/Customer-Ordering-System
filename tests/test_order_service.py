"""Unit/integration tests — REQ-ORD-C-01 order cancellation."""

from app.models.orders import OrderStatus
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService


class TestCancelOrder:
    def test_cancel_confirmed_order_succeeds(self, app, sample_order, customer_user):
        result = OrderService.cancel_order(sample_order.id, customer_user.id)
        assert result.success
        order = OrderRepository.get_by_id(sample_order.id)
        assert order.status == OrderStatus.CANCELLED

    def test_cancel_preparing_order_fails(self, app, sample_order, customer_user):
        OrderRepository.update_status(sample_order, OrderStatus.PREPARING)
        OrderRepository.commit()
        result = OrderService.cancel_order(sample_order.id, customer_user.id)
        assert not result.success
        assert "being prepared" in result.error.lower()

    def test_cancel_other_customers_order_denied(self, app, sample_order, customer_user):
        result = OrderService.cancel_order(sample_order.id, customer_user.id + 999)
        assert not result.success
