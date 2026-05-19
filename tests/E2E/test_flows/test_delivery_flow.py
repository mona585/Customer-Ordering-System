from tests.E2E.pages.delivery_dashboard_page import DeliveryDashboardPage


class TestDeliveryFlow:

    def test_login_as_delivery(self, delivery_client, base_url):
        resp = delivery_client.get("/delivery/")
        assert resp.status_code == 200

    def test_view_dashboard(self, delivery_client, base_url):
        dashboard = DeliveryDashboardPage(delivery_client)
        resp = dashboard.navigate()
        assert resp.status_code == 200

    def test_advance_order_status(self, delivery_client, sample_order, base_url):
        dashboard = DeliveryDashboardPage(delivery_client)
        resp = dashboard.advance_status(sample_order.id)
        assert resp.status_code in (200, 302)