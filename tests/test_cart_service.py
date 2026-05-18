"""Unit/integration tests — REQ-CART-02 stock limits."""

from app.services.cart_service import CartService


class TestAddToCartStock:
    def test_exceeding_stock_fails(self, app, menu_item):
        cart = {}
        first = CartService.add_to_cart(cart, menu_item.id, quantity=15)
        assert first.success
        cart = first.data["cart"]
        second = CartService.add_to_cart(cart, menu_item.id, quantity=10)
        assert not second.success
        assert "only 20" in second.error.lower()
