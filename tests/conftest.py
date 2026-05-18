"""Shared pytest fixtures for AURA tests."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.constants.roles import ROLE_ADMIN, ROLE_CUSTOMER, ROLE_DELIVERY
from app.extensions import db
from app.models.menu_item import Category, MenuItem
from app.models.orders import Order, OrderStatus
from app.models.user import User
from app.repositories.role_repository import RoleRepository

# ⚠️ Make sure this matches your actual file name! (voucher vs vouchers)
from app.models.voucher import UserVoucher 

TEST_PASSWORD = "TestPass!123"

@pytest.fixture(scope="function")
def app():
    """Fresh in-memory app + database per test."""
    application = create_app("testing")
    
    application.config["FIREBASE_WEB_API_KEY"] = "test-key-not-used-in-unit-tests"
    application.config["SKIP_FIREBASE_EMAIL_VERIFICATION"] = True
    
    with application.app_context():
        db.drop_all()
        db.create_all()
        from app.bootstrap.rbac import ensure_rbac_initialized
        ensure_rbac_initialized()
        
        yield application
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def _attach_role(user: User, slug: str) -> User:
    RoleRepository.attach_role_to_user(user, slug)
    db.session.refresh(user)
    return user

def _create_user(username: str, email: str, role_slug: str, points: int = 0) -> User:
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(TEST_PASSWORD),
        is_active=True,
        points=points,
    )
    db.session.add(user)
    db.session.commit()
    return _attach_role(user, role_slug)

@pytest.fixture
def admin_user(app):
    return _create_user("test_admin", "admin@test.aura", ROLE_ADMIN)

@pytest.fixture
def customer_user(app):
    return _create_user("test_customer", "customer@test.aura", ROLE_CUSTOMER, points=600)

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
    )
    db.session.add(item)
    db.session.commit()
    return item

@pytest.fixture
def sample_order(app, customer_user):
    order = Order(
        customer_id=customer_user.id,
        total_amount=Decimal("30.00"),
        subtotal=Decimal("25.00"),
        discount_amount=Decimal("0.00"),
        delivery_fee=Decimal("5.00"),
        tax_amount=Decimal("2.00"),
        status=OrderStatus.CONFIRMED,
        delivery_address="123 Test St",
    )
    db.session.add(order)
    db.session.commit()
    return order

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