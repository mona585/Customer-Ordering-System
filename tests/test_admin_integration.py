"""Integration tests for admin routes (/admin/*)."""

from __future__ import annotations

from app.extensions import db
from app.models.menu_item import MenuItem
from app.models.orders import Order, OrderStatus
class TestAdminAccessControl:
    def test_dashboard_redirects_when_anonymous(self, client):
        response = client.get("/admin/", follow_redirects=False)
        assert response.status_code in (302, 401)
        assert "login" in (response.location or "").lower()

    def test_dashboard_forbidden_for_customer(self, customer_client):
        response = customer_client.get("/admin/")
        assert response.status_code == 403

    def test_dashboard_ok_for_admin(self, admin_client):
        response = admin_client.get("/admin/")
        assert response.status_code == 200
        assert b"Dashboard" in response.data or b"dashboard" in response.data.lower()


class TestAdminOrdersRoutes:
    def test_orders_list(self, admin_client, sample_order):
        response = admin_client.get("/admin/orders")
        assert response.status_code == 200
        assert str(sample_order.id).encode() in response.data

    def test_orders_list_status_filter(self, admin_client, sample_order):
        response = admin_client.get("/admin/orders?status=CONFIRMED")
        assert response.status_code == 200
        response_pending = admin_client.get("/admin/orders?status=PENDING")
        assert response_pending.status_code == 200

    def test_order_detail(self, admin_client, sample_order):
        response = admin_client.get(f"/admin/orders/{sample_order.id}")
        assert response.status_code == 200
        assert str(sample_order.id).encode() in response.data

    def test_order_detail_not_found_redirects(self, admin_client):
        response = admin_client.get("/admin/orders/99999", follow_redirects=False)
        assert response.status_code == 302
        assert "/admin/orders" in response.location

    def test_order_update_status(self, admin_client, sample_order, app):
        response = admin_client.post(
            f"/admin/orders/{sample_order.id}/status",
            data={"status": "PREPARING"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert f"/admin/orders/{sample_order.id}" in response.location
        with app.app_context():
            order = db.session.get(Order, sample_order.id)
        assert order.status == OrderStatus.PREPARING

    def test_order_update_invalid_status_shows_error(
        self, admin_client, sample_order, app
    ):
        admin_client.post(
            f"/admin/orders/{sample_order.id}/status",
            data={"status": "NOT_VALID"},
            follow_redirects=True,
        )
        with app.app_context():
            order = db.session.get(Order, sample_order.id)
        assert order.status == OrderStatus.CONFIRMED


class TestAdminMenuRoutes:
    def test_menu_list(self, admin_client, menu_item):
        response = admin_client.get("/admin/menu")
        assert response.status_code == 200
        assert menu_item.name.encode() in response.data

    def test_menu_edit_get(self, admin_client, menu_item):
        response = admin_client.get(f"/admin/menu/{menu_item.id}/edit")
        assert response.status_code == 200
        assert menu_item.name.encode() in response.data

    def test_menu_edit_post(self, admin_client, menu_item, app):
        response = admin_client.post(
            f"/admin/menu/{menu_item.id}/edit",
            data={
                "name": "Integration Nachos",
                "category": "APPETIZERS",
                "price": "15.00",
                "stock_quantity": "30",
                "preparation_time": "8",
                "description": "From integration test",
                "is_available": "on",
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/admin/menu" in response.location
        with app.app_context():
            item = db.session.get(MenuItem, menu_item.id)
        assert item.name == "Integration Nachos"

    def test_menu_toggle_availability(self, admin_client, menu_item, app):
        with app.app_context():
            before = menu_item.is_available
        admin_client.post(
            f"/admin/menu/{menu_item.id}/toggle-availability",
            follow_redirects=True,
        )
        with app.app_context():
            item = db.session.get(MenuItem, menu_item.id)
        assert item.is_available is not before

    def test_menu_routes_forbidden_for_customer(self, customer_client, menu_item):
        assert customer_client.get("/admin/menu").status_code == 403
        assert (
            customer_client.get(f"/admin/menu/{menu_item.id}/edit").status_code
            == 403
        )
