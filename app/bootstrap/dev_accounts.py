# app/bootstrap/dev_accounts.py
"""Ensure dev login accounts exist (admin, delivery, test customer). Idempotent."""

from __future__ import annotations

from werkzeug.security import generate_password_hash

from app.constants.roles import ROLE_ADMIN, ROLE_CUSTOMER, ROLE_DELIVERY
from app.extensions import db
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository

_DEV_STAFF = (
    {
        "username": "aura_admin",
        "email": "admin@aura.local",
        "password": "AdminPass!123",
        "role": ROLE_ADMIN,
    },
    {
        "username": "aura_delivery",
        "email": "delivery@aura.local",
        "password": "DeliveryPass!123",
        "role": ROLE_DELIVERY,
    },
)


def ensure_dev_accounts() -> None:
    """
    Create or repair development accounts so login works after every restart.
    Safe to call on each app startup in DEBUG mode.
    """
    RoleRepository.ensure_default_roles()

    for spec in _DEV_STAFF:
        _ensure_staff_user(
            username=spec["username"],
            email=spec["email"],
            password=spec["password"],
            role_slug=spec["role"],
        )

    _ensure_test_customer()


def _ensure_staff_user(*, username: str, email: str, password: str, role_slug: str) -> None:
    user = UserRepository.get_by_username(username)
    if not user:
        user = User(
            username=username,
            email=email,
            firebase_uid=None,
            password_hash=generate_password_hash(password),
            is_active=True,
        )
        UserRepository.create(user)
        RoleRepository.attach_role_to_user(user, role_slug)
        return

    changed = False
    if user.is_active is False or user.is_active is None:
        user.is_active = True
        changed = True
    if user.firebase_uid is not None:
        user.firebase_uid = None
        changed = True
    if not user.password_hash or not _password_matches(user, password):
        user.password_hash = generate_password_hash(password)
        changed = True
    if not user.has_role(role_slug):
        RoleRepository.attach_role_to_user(user, role_slug)
        return
    if changed:
        db.session.commit()


def _password_matches(user: User, plain: str) -> bool:
    from werkzeug.security import check_password_hash

    if not user.password_hash:
        return False
    return check_password_hash(user.password_hash, plain)


def _ensure_test_customer() -> None:
    email = "test@aura.com"
    user = UserRepository.get_by_email(email)
    if not user:
        user = User(
            username="testuser",
            email=email,
            firebase_uid=None,
            password_hash=generate_password_hash("password123"),
            phone="+12345678901",
            address="123 Test Street",
            is_active=True,
        )
        UserRepository.create(user)
        RoleRepository.attach_role_to_user(user, ROLE_CUSTOMER)
        return

    if user.is_active is False or user.is_active is None:
        user.is_active = True
    if not user.has_role(ROLE_CUSTOMER):
        RoleRepository.attach_role_to_user(user, ROLE_CUSTOMER)
    if not user.password_hash:
        user.password_hash = generate_password_hash("password123")
    db.session.commit()
