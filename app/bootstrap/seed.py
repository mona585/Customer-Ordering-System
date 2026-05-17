# app/bootstrap/seed.py
"""Startup seeding hook - called automatically by the app factory."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def ensure_startup_seed(config_name: str = "development") -> None:
    """
    Idempotent startup hook that seeds the database on first run.

    - In development: creates dev staff accounts (admin, delivery, test customer).
    - In all environments: no destructive changes; safe to call on every restart.
    """
    try:
        from app.bootstrap.dev_accounts import ensure_dev_accounts
        ensure_dev_accounts()
        logger.info("[seed] Dev accounts ensured (config=%s)", config_name)
    except Exception as e:
        logger.warning("[seed] ensure_dev_accounts failed: %s", e)

    if config_name == "development":
        try:
            from app.models.menu_item import MenuItem
            from app.utils.seed_data import seed_menu_items

            if MenuItem.query.count() == 0:
                seed_menu_items()
                logger.info("[seed] Menu items seeded (empty catalog)")
        except Exception as e:
            logger.warning("[seed] menu seed failed: %s", e)
