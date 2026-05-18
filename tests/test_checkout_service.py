"""Unit tests — REQ-CHK-02, REQ-CART-03 (CheckoutService pricing & promos)."""

from app.constants.rewards import DELIVERY_FEE, TAX_RATE
from app.services.checkout_service import CheckoutService


class TestValidatePromo:
    """Padlock: AURA20 min_order = 30.00 (rewards.GLOBAL_PROMO_CODES)."""

    def test_save10_applies_ten_percent(self):
        result = CheckoutService._validate_promo("SAVE10", 50.0)
        assert result.success
        assert result.data["discount"] == 5.0
        assert result.data["code"] == "SAVE10"

    def test_aura20_fails_below_minimum_order(self):
        result = CheckoutService._validate_promo("AURA20", 25.0)
        assert not result.success
        assert "minimum order" in result.error.lower()

    def test_aura20_passes_at_exact_minimum(self):
        result = CheckoutService._validate_promo("AURA20", 30.0)
        assert result.success
        assert result.data["discount"] == 6.0

    def test_invalid_promo_code(self):
        result = CheckoutService._validate_promo("NOTREAL", 100.0)
        assert not result.success


class TestCalculateTotals:
    def test_tax_and_delivery_formula_without_discount(self, app, menu_item):
        cart = {str(menu_item.id): {"quantity": 2, "special_requests": ""}}
        result = CheckoutService.calculate_totals(cart)
        assert result.success
        subtotal = float(result.data["subtotal"])
        assert subtotal == 24.0
        assert result.data["delivery_fee"] == DELIVERY_FEE
        after = subtotal
        expected_tax = round(after * TAX_RATE, 2)
        assert result.data["tax"] == expected_tax
        assert result.data["total"] == round(after + DELIVERY_FEE + expected_tax, 2)
