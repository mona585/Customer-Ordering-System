# app/bootstrap/schema_compat.py
"""Lightweight SQLite compatibility for columns added after first deploy."""

from __future__ import annotations

from sqlalchemy import inspect, text

from app.extensions import db


def ensure_users_schema_compat() -> None:
    """Add `is_active` on legacy SQLite DBs where create_all() did not migrate."""
    try:
        inspector = inspect(db.engine)
        if "users" not in inspector.get_table_names():
            return
        columns = {col["name"] for col in inspector.get_columns("users")}
    except Exception:
        return

    if "is_active" not in columns:
        db.session.execute(
            text("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1")
        )
        db.session.commit()

    columns = {col["name"] for col in inspector.get_columns("users")}
    if "date_of_birth" not in columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN date_of_birth DATE"))
        db.session.commit()
    columns = {col["name"] for col in inspector.get_columns("users")}
    if "dietary_preferences" not in columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN dietary_preferences VARCHAR(500)"))
        db.session.commit()
    columns = {col["name"] for col in inspector.get_columns("users")}
    if "other_allergies" not in columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN other_allergies VARCHAR(500)"))
        db.session.commit()

    columns = {col["name"] for col in inspector.get_columns("users")}
    if "referral_code" not in columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN referral_code VARCHAR(20)"))
        db.session.commit()
    columns = {col["name"] for col in inspector.get_columns("users")}
    if "wallet_balance" not in columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN wallet_balance NUMERIC(10, 2) DEFAULT 0"))
        db.session.commit()

    if "orders" in inspector.get_table_names():
        order_cols = {col["name"] for col in inspector.get_columns("orders")}
        for col_name, col_def in (
            ("voucher_id", "INTEGER"),
            ("promo_code", "VARCHAR(32)"),
            ("subtotal", "NUMERIC(10, 2)"),
            ("discount_amount", "NUMERIC(10, 2) DEFAULT 0"),
            ("delivery_fee", "NUMERIC(10, 2) DEFAULT 0"),
            ("tax_amount", "NUMERIC(10, 2) DEFAULT 0"),
            ("points_awarded", "BOOLEAN NOT NULL DEFAULT 0"),
        ):
            if col_name not in order_cols:
                db.session.execute(text(f"ALTER TABLE orders ADD COLUMN {col_name} {col_def}"))
                db.session.commit()
