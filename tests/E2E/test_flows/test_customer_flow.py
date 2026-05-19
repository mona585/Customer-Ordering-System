from tests.E2E.pages.menu_page import MenuPage
from tests.E2E.pages.cart_page import CartPage
from tests.E2E.pages.checkout_page import CheckoutPage


class TestCustomerFlow:

    def test_login_as_customer(self, customer_client, base_url):
        resp = customer_client.get("/customer/menu")
        assert resp.status_code == 200

    def test_browse_menu(self, customer_client, base_url):
        menu = MenuPage(customer_client)
        resp = menu.navigate()
        assert resp.status_code == 200

    def test_add_to_cart(self, customer_client, menu_item, base_url):
        cart = CartPage(customer_client)
        resp = cart.add_item(menu_item.id, quantity=2)
        assert resp.status_code in (200, 302)

    def test_apply_promo(self, customer_client, base_url):
        cart = CartPage(customer_client)
        resp = cart.apply_promo("SAVE10")
        assert resp.status_code in (200, 302)

    def test_checkout(self, customer_client, base_url):
        checkout = CheckoutPage(customer_client)
        resp = checkout.place_order(address="123 Test Street")
        assert resp.status_code in (200, 302)