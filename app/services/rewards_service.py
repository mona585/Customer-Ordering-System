from app.constants.rewards import POINT_REDEMPTION_OPTIONS, POINTS_PER_DOLLAR, TIER_THRESHOLDS
from app.extensions import db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.voucher_repository import VoucherRepository
from app.services.base_service import BaseService, ServiceResult
from app.services.notification_service import NotificationService
from app.services.voucher_service import VoucherService


class RewardsService(BaseService):
    @staticmethod
    def get_tier(points: int) -> str:
        if points >= TIER_THRESHOLDS["Gold"]:
            return "Gold"
        if points >= TIER_THRESHOLDS["Silver"]:
            return "Silver"
        return "Bronze"

    @staticmethod
    def get_profile_rewards(user_id: int) -> ServiceResult:
        user = UserRepository.get_by_id(user_id)
        if not user:
            return ServiceResult.fail("User not found")
        points = user.points or 0
        tier = RewardsService.get_tier(points)
        vouchers = VoucherRepository.list_active_for_user(user_id)
        return ServiceResult.ok(
            data={
                "points": points,
                "tier": tier,
                "vouchers": [v.to_dict() for v in vouchers],
                "referral_code": user.referral_code,
                "wallet_balance": float(user.wallet_balance or 0),
            }
        )

    @staticmethod
    def award_delivery_points(order) -> int:
        if order.points_awarded:
            return 0
        user = UserRepository.get_by_id(order.customer_id)
        if not user:
            return 0
        earned = int(float(order.total_amount) * POINTS_PER_DOLLAR)
        user.points = (user.points or 0) + earned
        order.points_awarded = True
        db.session.commit()
        NotificationService.notify(
            order.customer_id,
            "Points earned!",
            f"You earned {earned} AURA points from your delivered order #{order.id}.",
            category="points",
        )
        return earned

    @staticmethod
    def redeem_points(user_id: int, option_index: int = 0) -> ServiceResult:
        user = UserRepository.get_by_id(user_id)
        if not user:
            return ServiceResult.fail("User not found")
        if option_index < 0 or option_index >= len(POINT_REDEMPTION_OPTIONS):
            return ServiceResult.fail("Invalid redemption option")
        opt = POINT_REDEMPTION_OPTIONS[option_index]
        cost = opt["points"]
        if (user.points or 0) < cost:
            return ServiceResult.fail(f"You need at least {cost} points to redeem this voucher")
        user.points -= cost
        import secrets

        suffix = secrets.token_hex(2).upper()
        code = f"{opt['code_prefix']}-{suffix}"
        voucher = VoucherService.issue_voucher(
            user_id=user_id,
            code=code,
            discount_percent=opt["discount_percent"],
            min_order_amount=opt["min_order"],
            days_valid=30,
            source="points_redemption",
        )
        db.session.commit()
        NotificationService.notify(
            user_id,
            "New voucher unlocked!",
            f"You redeemed {cost} points for voucher {voucher.code} ({opt['discount_percent']}% off).",
            category="rewards",
        )
        return ServiceResult.ok(data=voucher.to_dict(), message="Voucher redeemed successfully")
