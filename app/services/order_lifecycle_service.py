"""Hooks when order status changes — points, referrals, notifications."""

from app.models.orders import OrderStatus
from app.services.notification_service import NotificationService
from app.services.referral_service import ReferralService
from app.services.rewards_service import RewardsService


_STATUS_MESSAGES = {
    "CONFIRMED": ("Order confirmed", "Your order has been confirmed and is being scheduled."),
    "PREPARING": ("Order being prepared", "Your order is now being prepared by our kitchen."),
    "READY": ("Order ready", "Your order is ready and will be dispatched soon."),
    "OUT_FOR_DELIVERY": ("Out for delivery", "Your order is on its way to you!"),
    "DELIVERED": ("Order delivered", "Your order has been delivered. Enjoy your meal!"),
}


class OrderLifecycleService:
    @staticmethod
    def on_status_change(order, new_status) -> None:
        key = new_status.name if hasattr(new_status, "name") else str(new_status).upper()
        title, message = _STATUS_MESSAGES.get(key, (f"Order update", f"Your order status is now {key}."))
        NotificationService.notify(
            order.customer_id,
            title,
            f"{message} (Order #{order.id})",
            category="order_tracking",
        )
        if key == "DELIVERED":
            OrderLifecycleService._on_delivered(order)

    @staticmethod
    def _on_delivered(order) -> None:
        RewardsService.award_delivery_points(order)
        ReferralService.complete_on_first_delivery(order.customer_id)
        from app.services.voucher_service import VoucherService

        VoucherService.check_expiring_soon(order.customer_id)
