from tests.E2E.pages.admin_orders_page import AdminOrdersPage
from tests.E2E.pages.admin_menu_page import AdminMenuPage


class TestAdminFlow:

    def test_login_as_admin(self, admin_client, base_url):
        resp = admin_client.get("/admin/")
        assert resp.status_code == 200

    def test_view_orders(self, admin_client, base_url):
        orders = AdminOrdersPage(admin_client)
        resp = orders.navigate()
        assert resp.status_code == 200

    def test_update_order_status(self, admin_client, sample_order, base_url):
        orders = AdminOrdersPage(admin_client)
        resp = orders.update_status(sample_order.id, "delivered")
        assert resp.status_code in (200, 302)

    def test_toggle_menu_item(self, admin_client, menu_item, base_url):
        menu = AdminMenuPage(admin_client)
        resp = menu.toggle_availability(menu_item.id)
        assert resp.status_code in (200, 302)