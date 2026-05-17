"""Backfill referral codes and welcome vouchers for existing customers."""

from app.extensions import db
from app.models.user import User
from app.repositories.voucher_repository import VoucherRepository
from app.services.referral_service import ReferralService
from app.services.voucher_service import VoucherService


def ensure_rewards_compat() -> None:
    try:
        users = User.query.all()
        for user in users:
            if not user.referral_code:
                ReferralService.generate_referral_code(user)
            welcome = VoucherRepository.get_by_code(user.id, "WELCOME20")
            if not welcome:
                VoucherService.grant_welcome_voucher(user.id)
        db.session.commit()
    except Exception:
        db.session.rollback()
