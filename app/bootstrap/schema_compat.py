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
