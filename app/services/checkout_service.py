from datetime import datetime

from app.constants.rewards import DELIVERY_FEE, GLOBAL_PROMO_CODES, TAX_RATE
from app.services.base_service import BaseService, ServiceResult
from app.services.cart_service import CartService
from app.services.voucher_service import VoucherService


class CheckoutService(BaseService):
    @staticmethod
    def _validate_promo(code: str, subtotal: float):
        promo = GLOBAL_PROMO_CODES.get(code)
        if not promo:
            return ServiceResult.fail("Invalid or expired promo code")

        expires_at = promo.get("expires_at")
        if expires_at and datetime.utcnow() > expires_at:
            return ServiceResult.fail(f"Promo {code} has expired")

        min_order = float(promo.get("min_order", 0))
        if subtotal < min_order:
            return ServiceResult.fail(f"Promo {code} requires minimum order of ${min_order:.2f}")

        discount = subtotal * (promo["discount_percent"] / 100)
        return ServiceResult.ok(data={"discount": discount, "code": code})

    @staticmethod
    def calculate_totals(cart_data, user_id=None, promo_code=None, voucher_code=None):
        cart_result = CartService.get_cart_items(cart_data)
        if not cart_result.success:
            return cart_result
        subtotal = float(cart_result.data["total"])
        discount = 0.0
        voucher_id = None
        applied_promo = None
        applied_voucher = None

        if promo_code:
            code = promo_code.strip().upper()
            promo_result = CheckoutService._validate_promo(code, subtotal)
            if not promo_result.success:
                return promo_result
            discount += promo_result.data["discount"]
            applied_promo = promo_result.data["code"]

        if voucher_code and user_id:
            v_result = VoucherService.validate_for_checkout(user_id, voucher_code, subtotal)
            if not v_result.success:
                return v_result
            discount += v_result.data["discount_amount"]
            voucher_id = v_result.data["voucher_id"]
            applied_voucher = v_result.data["code"]

        after_discount = max(subtotal - discount, 0)
        delivery_fee = DELIVERY_FEE
        tax = round(after_discount * TAX_RATE, 2)
        total = round(after_discount + delivery_fee + tax, 2)

        return ServiceResult.ok(
            data={
                "subtotal": round(subtotal, 2),
                "discount": round(discount, 2),
                "delivery_fee": delivery_fee,
                "tax": tax,
                "total": total,
                "voucher_id": voucher_id,
                "applied_promo": applied_promo,
                "applied_voucher": applied_voucher,
                "items": cart_result.data["items"],
            }
        )
