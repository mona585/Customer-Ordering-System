import secrets

from app.constants.rewards import REFERRAL_REWARDS
from app.extensions import db
from app.models.referral import Referral
from app.models.user import User
from app.repositories.referral_repository import ReferralRepository
from app.repositories.user_repository import UserRepository
from app.services.base_service import BaseService, ServiceResult
from app.services.notification_service import NotificationService
from app.services.voucher_service import VoucherService


class ReferralService(BaseService):
    @staticmethod
    def generate_referral_code(user: User) -> str:
        if user.referral_code:
            return user.referral_code
        base = f"AURA-{user.id:04d}"
        if not UserRepository.get_by_referral_code(base):
            user.referral_code = base
            db.session.commit()
            return base
        suffix = secrets.token_hex(2).upper()
        code = f"AURA-{suffix}"
        user.referral_code = code
        db.session.commit()
        return code

    @staticmethod
    def get_by_referral_code(code: str) -> User | None:
        return ReferralRepository.find_user_by_referral_code(code)

    @staticmethod
    def link_on_registration(referred_user: User, referral_code: str) -> ServiceResult:
        code = (referral_code or "").strip().upper()
        if not code:
            return ServiceResult.ok()
        referrer = ReferralRepository.find_user_by_referral_code(code)
        if not referrer:
            return ServiceResult.fail("Invalid referral code")
        if referrer.id == referred_user.id:
            return ServiceResult.fail("You cannot use your own referral code")
        if ReferralRepository.get_by_referred(referred_user.id):
            return ServiceResult.fail("Referral already linked")
        ref = Referral(referrer_id=referrer.id, referred_id=referred_user.id, status="pending")
        ReferralRepository.create(ref)
        ReferralRepository.commit()
        NotificationService.notify(
            referrer.id,
            "New referral signup!",
            f"{referred_user.username} signed up using your referral code. "
            "You'll earn rewards when they complete their first delivered order.",
            category="referral",
        )
        return ServiceResult.ok(message="Referral linked")

    @staticmethod
    def complete_on_first_delivery(referred_user_id: int) -> None:
        ref = ReferralRepository.get_by_referred(referred_user_id)
        if not ref or ref.status != "pending":
            return
        from app.models.orders import Order, OrderStatus

        delivered_count = (
            Order.query.filter_by(customer_id=referred_user_id, status=OrderStatus.DELIVERED).count()
        )
        if delivered_count != 1:
            return
        from datetime import datetime

        ref.status = "confirmed"
        ref.completed_at = datetime.utcnow()
        ReferralRepository.commit()

        for role, cfg in REFERRAL_REWARDS.items():
            user_id = ref.referrer_id if role == "referrer" else ref.referred_id
            VoucherService.issue_voucher(
                user_id=user_id,
                code=cfg["code"] if role == "referrer" else f"{cfg['code']}-{referred_user_id}",
                discount_percent=cfg["discount_percent"],
                min_order_amount=cfg["min_order_amount"],
                days_valid=cfg["days_valid"],
                source="referral",
            )
            NotificationService.notify(
                user_id,
                "Referral reward unlocked!",
                f"You received a {cfg['discount_percent']}% discount voucher from the referral program.",
                category="rewards",
            )
