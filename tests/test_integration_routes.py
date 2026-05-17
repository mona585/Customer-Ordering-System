"""Integration tests — Flask test client (selected routes)."""

import json

from app.constants.roles import ROLE_CUSTOMER
from app.extensions import db
from app.models.menu_item import Category, MenuItem
from app.models.order_item import OrderItem
from app.models.orders import Order, OrderStatus
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from werkzeug.security import generate_password_hash


class TestPublicRoutes:
    def test_pages_delivery_slug(self, client):
        response = client.get("/pages/delivery")
        assert response.status_code == 200
        assert b"Delivery" in response.data

    def test_pages_unknown_slug_404(self, client):
        response = client.get("/pages/not-a-real-slug")
        assert response.status_code == 404


class TestCheckoutValidateApi:
    def test_checkout_validate_requires_login(self, client):
        response = client.post(
            "/customer/api/checkout/validate",
            data=json.dumps({"promo_code": "SAVE10"}),
            content_type="application/json",
        )
        assert response.status_code in (302, 401)


class TestCustomerOrdersPage:
    def test_orders_page_renders_for_logged_in_customer(self, app, client):
        with app.app_context():
            RoleRepository.ensure_default_roles()
            user = User(
                username="ordersdemo",
                email="ordersdemo@test.example",
                password_hash=generate_password_hash("Aura@12345"),
                is_active=True,
            )
            db.session.add(user)
            db.session.flush()
            RoleRepository.attach_role_to_user(user, ROLE_CUSTOMER)
            item = MenuItem(
                name="Demo Fries",
                description="test",
                price=5.0,
                category=Category.SIDES,
                is_available=True,
                stock_quantity=10,
            )
            db.session.add(item)
            db.session.flush()
            order = Order(
                customer_id=user.id,
                total_amount=10.0,
                subtotal=5.0,
                status=OrderStatus.CONFIRMED,
                delivery_address="1 Demo St",
            )
            db.session.add(order)
            db.session.flush()
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    menu_item_id=item.id,
                    quantity=1,
                    unit_price=5.0,
                )
            )
            db.session.commit()
            user_id = user.id

        with client.session_transaction() as sess:
            sess["_user_id"] = str(user_id)
            sess["_fresh"] = True

        response = client.get("/customer/orders")
        assert response.status_code == 200
        assert b"My Orders" in response.data
        assert b"Demo Fries" in response.data

    def test_legacy_my_orders_redirects(self, client):
        response = client.get("/order/my-orders", follow_redirects=False)
        assert response.status_code in (301, 302, 303, 307, 308)
        assert "/customer/orders" in (response.headers.get("Location") or "")


def _login_as(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


class TestStaffDashboards:
    def test_admin_dashboard_for_admin_user(self, app, client):
        from app.constants.roles import ROLE_ADMIN

        with app.app_context():
            RoleRepository.ensure_default_roles()
            admin = User(
                username="admin_test",
                email="admin_test@aura.local",
                password_hash=generate_password_hash("AdminPass!123"),
                is_active=True,
            )
            db.session.add(admin)
            db.session.flush()
            RoleRepository.attach_role_to_user(admin, ROLE_ADMIN)
            db.session.commit()
            admin_id = admin.id

        _login_as(client, admin_id)
        assert client.get("/admin/").status_code == 200
        assert client.get("/admin/orders").status_code == 200
        assert client.get("/admin/menu").status_code == 200

    def test_delivery_dashboard_for_delivery_user(self, app, client):
        from app.constants.roles import ROLE_DELIVERY

        with app.app_context():
            RoleRepository.ensure_default_roles()
            driver = User(
                username="delivery_test",
                email="delivery_test@aura.local",
                password_hash=generate_password_hash("DeliveryPass!123"),
                is_active=True,
            )
            db.session.add(driver)
            db.session.flush()
            RoleRepository.attach_role_to_user(driver, ROLE_DELIVERY)
            db.session.commit()
            driver_id = driver.id

        _login_as(client, driver_id)
        response = client.get("/delivery/")
        assert response.status_code == 200
        assert b"Delivery Dashboard" in response.data

    def test_customer_cannot_access_admin(self, app, client):
        with app.app_context():
            RoleRepository.ensure_default_roles()
            user = User(
                username="cust_only",
                email="cust_only@test.example",
                password_hash=generate_password_hash("Aura@12345"),
                is_active=True,
            )
            db.session.add(user)
            db.session.flush()
            RoleRepository.attach_role_to_user(user, ROLE_CUSTOMER)
            db.session.commit()
            user_id = user.id

        _login_as(client, user_id)
        assert client.get("/admin/").status_code == 403
