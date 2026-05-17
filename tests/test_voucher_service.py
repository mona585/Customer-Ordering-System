"""Unit/integration tests — REQ-CHK-03 vouchers."""

from datetime import datetime, timedelta

from app.models.voucher import UserVoucher
from app.extensions import db
from app.services.voucher_service import VoucherService


class TestValidateForCheckout:
    def test_active_voucher_applies_discount(self, app, customer_user, active_voucher):
        result = VoucherService.validate_for_checkout(customer_user.id, "TESTVOUCH", 50.0)
        assert result.success
        assert result.data["discount_amount"] == 5.0

    def test_expired_voucher_rejected(self, app, customer_user):
        expired = UserVoucher(
            user_id=customer_user.id,
            code="OLDVOUCH",
            discount_percent=10,
            min_order_amount=0,
            expires_at=datetime.utcnow() - timedelta(days=1),
            is_used=False,
            source="test",
        )
        db.session.add(expired)
        db.session.commit()
        result = VoucherService.validate_for_checkout(customer_user.id, "OLDVOUCH", 50.0)
        assert not result.success
        assert "expired" in result.error.lower()

    def test_below_minimum_order(self, app, customer_user, active_voucher):
        result = VoucherService.validate_for_checkout(customer_user.id, "TESTVOUCH", 15.0)
        assert not result.success
        assert "minimum" in result.error.lower()
