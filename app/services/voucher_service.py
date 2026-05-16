from datetime import datetime, timedelta

from app.constants.rewards import WELCOME_VOUCHER
from app.models.voucher import UserVoucher
from app.repositories.voucher_repository import VoucherRepository
from app.services.base_service import BaseService, ServiceResult


class VoucherService(BaseService):
    @staticmethod
    def issue_voucher(
        user_id: int,
        code: str,
        discount_percent: int,
        min_order_amount: float = 0,
        days_valid: int = 30,
        source: str = "manual",
    ) -> UserVoucher | None:
        code = code.upper().strip()
        existing = VoucherRepository.get_by_code(user_id, code)
        if existing and existing.is_active():
            return existing
        voucher = UserVoucher(
            user_id=user_id,
            code=code,
            discount_percent=discount_percent,
            min_order_amount=min_order_amount,
            expires_at=datetime.utcnow() + timedelta(days=days_valid),
            source=source,
        )
        VoucherRepository.create(voucher)
        VoucherRepository.commit()
        return voucher

    @staticmethod
    def grant_welcome_voucher(user_id: int) -> None:
        cfg = WELCOME_VOUCHER
        VoucherService.issue_voucher(
            user_id=user_id,
            code=cfg["code"],
            discount_percent=cfg["discount_percent"],
            min_order_amount=cfg["min_order_amount"],
            days_valid=cfg["days_valid"],
            source="welcome",
        )

    @staticmethod
    def list_active(user_id: int) -> ServiceResult:
        vouchers = VoucherRepository.list_active_for_user(user_id)
        return ServiceResult.ok(data=[v.to_dict() for v in vouchers])

    @staticmethod
    def validate_for_checkout(user_id: int, code: str, subtotal: float) -> ServiceResult:
        voucher = VoucherRepository.get_by_code(user_id, code)
        if not voucher:
            return ServiceResult.fail("Voucher not found")
        if voucher.is_used:
            return ServiceResult.fail("This voucher has already been used")
        if not voucher.is_active():
            return ServiceResult.fail("This voucher has expired")
        min_amt = float(voucher.min_order_amount or 0)
        if subtotal < min_amt:
            return ServiceResult.fail(f"Minimum order amount is ${min_amt:.2f}")
        discount = subtotal * (voucher.discount_percent / 100)
        return ServiceResult.ok(
            data={
                "voucher_id": voucher.id,
                "code": voucher.code,
                "discount_percent": voucher.discount_percent,
                "discount_amount": round(discount, 2),
            }
        )

    @staticmethod
    def mark_used(voucher_id: int, user_id: int) -> None:
        voucher = VoucherRepository.get_by_id(voucher_id, user_id)
        if voucher:
            voucher.is_used = True
            VoucherRepository.commit()

    @staticmethod
    def check_expiring_soon(user_id: int, days: int = 3) -> None:
        from app.services.notification_service import NotificationService

        now = datetime.utcnow()
        threshold = now + timedelta(days=days)
        for v in VoucherRepository.list_active_for_user(user_id):
            if v.expires_at <= threshold:
                NotificationService.notify(
                    user_id,
                    "Voucher expiring soon",
                    f"Your voucher {v.code} ({v.discount_percent}% off) expires on "
                    f"{v.expires_at.strftime('%b %d, %Y')}. Use it before it's gone!",
                    category="expiration",
                )
