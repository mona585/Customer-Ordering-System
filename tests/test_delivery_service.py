"""Unit/integration tests — REQ-DEL-02 delivery pipeline."""

from app.models.orders import OrderStatus
from app.repositories.order_repository import OrderRepository
from app.services.delivery_service import DeliveryService


class TestAdvanceDeliveryStatus:
    def test_ready_to_out_for_delivery(self, app, sample_order):
        OrderRepository.update_status(sample_order, OrderStatus.READY)
        OrderRepository.commit()
        result = DeliveryService.advance_delivery_status(sample_order.id)
        assert result.success
        order = OrderRepository.get_by_id(sample_order.id)
        assert order.status == OrderStatus.OUT_FOR_DELIVERY

    def test_confirmed_status_not_in_pipeline(self, app, sample_order):
        result = DeliveryService.advance_delivery_status(sample_order.id)
        assert not result.success
        assert "delivery pipeline" in result.error.lower()
