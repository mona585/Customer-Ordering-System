"""Shared pytest fixtures for AURA Customer Ordering System."""

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models.menu_item import Category, MenuItem
from app.models.orders import Order, OrderStatus
from app.models.user import User
from app.models.voucher import UserVoucher
from datetime import datetime, timedelta


@pytest.fixture
def app():
    application = create_app("testing")
    application.config["FIREBASE_WEB_API_KEY"] = "test-key-not-used-in-unit-tests"
    application.config["SKIP_FIREBASE_EMAIL_VERIFICATION"] = True
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def menu_item(app):
    item = MenuItem(
        name="Test Burger",
        description="Unit test item",
        price=12.50,
        category=Category.MAIN_COURSE,
        is_available=True,
        stock_quantity=10,
    )
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture
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
