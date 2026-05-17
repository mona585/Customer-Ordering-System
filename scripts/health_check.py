"""Quick local health check for demo recording."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.constants.roles import ROLE_CUSTOMER
from app.models.menu_item import Category, MenuItem
from app.models.order_item import OrderItem
from app.models.orders import Order, OrderStatus
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.routes.auth import _validate_registration, _firebase_api_key
from app.security.password_policy import validate_password_strength
from app.services.order_service import OrderService


def main() -> int:
    app = create_app("testing")
    app.config["FIREBASE_WEB_API_KEY"] = "test-key"
    errors = []

    with app.app_context():
        db.create_all()
        RoleRepository.ensure_default_roles()

        pwd_err = validate_password_strength("Aura@12345", username="demo", email="demo@test.com")
        if pwd_err:
            errors.append(f"password policy: {pwd_err}")

        reg_err = _validate_registration("demouser", "demo@test.com", "Aura@12345", "", "Aura@12345")
        if reg_err:
            errors.append(f"registration validation: {reg_err}")

        user = User(
            username="healthcheck",
            email="healthcheck@test.com",
            password_hash=generate_password_hash("Aura@12345"),
            is_active=True,
        )
        UserRepository.create(user)
        RoleRepository.attach_role_to_user(user, ROLE_CUSTOMER)

        item = MenuItem(
            name="Health Burger",
            description="test",
            price=10.0,
            category=Category.MAIN_COURSE,
            is_available=True,
            stock_quantity=5,
        )
        db.session.add(item)
        db.session.flush()

        order = Order(
            customer_id=user.id,
            total_amount=15.0,
            subtotal=10.0,
            status=OrderStatus.CONFIRMED,
            delivery_address="1 Test St",
        )
        db.session.add(order)
        db.session.flush()
        db.session.add(
            OrderItem(
                order_id=order.id,
                menu_item_id=item.id,
                quantity=1,
                unit_price=10.0,
            )
        )
        db.session.commit()

        result = OrderService.get_user_orders(user.id)
        if not result.success:
            errors.append(f"get_user_orders failed: {result.error}")

        client = app.test_client()
        with client.session_transaction() as sess:
            pass

        from flask_login import login_user

        with app.test_request_context():
            login_user(user)
            resp = client.get("/customer/orders")
            if resp.status_code != 200:
                errors.append(f"GET /customer/orders -> {resp.status_code}")
            elif b"My Orders" not in resp.data:
                errors.append("orders page missing expected content")

        reg_page = client.get("/auth/register")
        if reg_page.status_code != 200 or b"regForm" not in reg_page.data:
            errors.append("register page broken")

        login_page = client.get("/auth/login")
        if login_page.status_code != 200 or b"loginForm" not in login_page.data:
            errors.append("login page broken")

    dev_app = create_app("development")
    with dev_app.app_context():
        if not _firebase_api_key():
            print("WARN: FIREBASE_WEB_API_KEY not set — customer Firebase login/register will fail in dev.")

    if errors:
        print("FAILED:")
        for e in errors:
            print(" -", e)
        return 1

    print("OK: password, orders page, auth templates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
