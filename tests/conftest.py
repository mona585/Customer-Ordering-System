<<<<<<< HEAD
"""Shared pytest fixtures for AURA Customer Ordering System."""
=======
"""Shared pytest fixtures for AURA tests."""

from __future__ import annotations

from decimal import Decimal
>>>>>>> 87d1f10 (Add admin unit and integration tests for dashboard, orders, and menu)

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
<<<<<<< HEAD
=======
from app.constants.roles import ROLE_ADMIN, ROLE_CUSTOMER, ROLE_DELIVERY
>>>>>>> 87d1f10 (Add admin unit and integration tests for dashboard, orders, and menu)
from app.extensions import db
from app.models.menu_item import Category, MenuItem
from app.models.orders import Order, OrderStatus
from app.models.user import User
<<<<<<< HEAD
from app.models.voucher import UserVoucher
from datetime import datetime, timedelta


@pytest.fixture
def app():
    application = create_app("testing")
    application.config["FIREBASE_WEB_API_KEY"] = "test-key-not-used-in-unit-tests"
    application.config["SKIP_FIREBASE_EMAIL_VERIFICATION"] = True
    with application.app_context():
        db.create_all()
=======
from app.repositories.role_repository import RoleRepository

TEST_PASSWORD = "TestPass!123"


@pytest.fixture(scope="function")
def app():
    """Fresh in-memory app + database per test."""
    application = create_app("testing")
    with application.app_context():
        db.drop_all()
        db.create_all()
        from app.bootstrap.rbac import ensure_rbac_initialized

        ensure_rbac_initialized()
>>>>>>> 87d1f10 (Add admin unit and integration tests for dashboard, orders, and menu)
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


<<<<<<< HEAD
@pytest.fixture
def menu_item(app):
    item = MenuItem(
        name="Test Burger",
        description="Unit test item",
        price=12.50,
        category=Category.MAIN_COURSE,
        is_available=True,
        stock_quantity=10,
=======
def _attach_role(user: User, slug: str) -> User:
    RoleRepository.attach_role_to_user(user, slug)
    db.session.refresh(user)
    return user


def _create_user(username: str, email: str, role_slug: str) -> User:
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(TEST_PASSWORD),
        is_active=True,
    )
    db.session.add(user)
    db.session.commit()
    return _attach_role(user, role_slug)


@pytest.fixture
def admin_user(app):
    return _create_user("test_admin", "admin@test.aura", ROLE_ADMIN)


@pytest.fixture
def customer_user(app):
    return _create_user("test_customer", "customer@test.aura", ROLE_CUSTOMER)


@pytest.fixture
def delivery_user(app):
    return _create_user("test_delivery", "delivery@test.aura", ROLE_DELIVERY)


@pytest.fixture
def menu_item(app):
    item = MenuItem(
        name="Test Nachos",
        description="Crispy chips",
        price=Decimal("12.00"),
        category=Category.APPETIZERS,
        stock_quantity=20,
        preparation_time=10,
        is_available=True,
>>>>>>> 87d1f10 (Add admin unit and integration tests for dashboard, orders, and menu)
    )
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture
<<<<<<< HEAD
def customer_user(app):
    user = User(
        username="testcustomer",
        email="customer@test.example",
        password_hash=generate_password_hash("password123"),
        points=600,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_order(app, customer_user):
    order = Order(
        customer_id=customer_user.id,
        total_amount=30.00,
        subtotal=25.00,
        discount_amount=0,
        delivery_fee=5.0,
        tax_amount=2.00,
        status=OrderStatus.CONFIRMED,
        delivery_address="123 Test St",
=======
def sample_order(app, customer_user, menu_item):
    order = Order(
        customer_id=customer_user.id,
        total_amount=Decimal("17.96"),
        status=OrderStatus.CONFIRMED,
        delivery_address="Test City",
>>>>>>> 87d1f10 (Add admin unit and integration tests for dashboard, orders, and menu)
    )
    db.session.add(order)
    db.session.commit()
    return order


<<<<<<< HEAD
@pytest.fixture
def active_voucher(app, customer_user):
    voucher = UserVoucher(
        user_id=customer_user.id,
        code="TESTVOUCH",
        discount_percent=10,
        min_order_amount=20.0,
        expires_at=datetime.utcnow() + timedelta(days=7),
        is_used=False,
        source="test",
    )
    db.session.add(voucher)
    db.session.commit()
    return voucher
=======
def login_client(client, user: User):
    """Set Flask-Login session for integration tests."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


@pytest.fixture
def admin_client(client, admin_user):
    login_client(client, admin_user)
    return client


@pytest.fixture
def customer_client(client, customer_user):
    login_client(client, customer_user)
    return client
>>>>>>> 87d1f10 (Add admin unit and integration tests for dashboard, orders, and menu)
