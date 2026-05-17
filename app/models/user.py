# app/models/user.py

from __future__ import annotations

from datetime import date, datetime

from flask_login import UserMixin

from app.constants.roles import STAFF_ROLE_SLUGS
from app.extensions import db
from app.models.role import user_role_association


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date, nullable=True)
    dietary_preferences = db.Column(db.String(500), nullable=True)
    other_allergies = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False, server_default=db.text("1"))

    orders = db.relationship("Order", back_populates="customer", lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="customer", lazy=True, cascade="all, delete-orphan")
    addresses = db.relationship("UserAddress", back_populates="user", lazy=True, cascade="all, delete-orphan")
    saved_cards = db.relationship("SavedCard", back_populates="user", lazy=True, cascade="all, delete-orphan")
    vouchers = db.relationship("UserVoucher", back_populates="user", lazy=True, cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="user", lazy=True, cascade="all, delete-orphan")
    referrals_made = db.relationship(
        "Referral", foreign_keys="Referral.referrer_id", back_populates="referrer", lazy=True
    )
    referral_received = db.relationship(
        "Referral", foreign_keys="Referral.referred_id", back_populates="referred", uselist=False
    )
    points = db.Column(db.Integer, default=0)
    referral_code = db.Column(db.String(20), unique=True, nullable=True)
    wallet_balance = db.Column(db.Numeric(10, 2), default=0)

    roles = db.relationship(
        "Role",
        secondary=user_role_association,
        back_populates="users",
        lazy="selectin",
    )

    def __init__(
        self,
        username,
        email,
        firebase_uid=None,
        password_hash=None,
        phone=None,
        address=None,
        points=0,
        is_active=True,
    ):
        self.username = username
        self.email = email
        self.firebase_uid = firebase_uid
        self.password_hash = password_hash
        self.phone = phone
        self.address = address
        self.points = points
        self.is_active = is_active

    def __repr__(self):
        return f"<User {self.username}>"

    def has_role(self, slug: str) -> bool:
        if not slug:
            return False
        return any(getattr(r, "slug", None) == slug for r in (self.roles or ()))

    def uses_staff_authentication(self) -> bool:
        return any(getattr(r, "slug", None) in STAFF_ROLE_SLUGS for r in (self.roles or ()))

    def to_dict(self):
        return {
            "id": self.id,
            "firebase_uid": self.firebase_uid,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }