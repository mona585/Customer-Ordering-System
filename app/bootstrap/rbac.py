# app/bootstrap/rbac.py

from __future__ import annotations

from app.constants.roles import ROLE_CUSTOMER
from app.models.user import User
from app.repositories.role_repository import RoleRepository


def ensure_rbac_initialized() -> None:
    """
    Idempotent startup hook:
    - Ensure core Role rows exist.
    - Backfill `customer` role for legacy customer rows that have Firebase UID
      but no role rows yet (typical after adding RBAC to an existing DB).

    Internal staff without `firebase_uid` and without roles are left unchanged
    on purpose so they are not auto-labeled as customers — fix those via seed/SQL.
    """
    RoleRepository.ensure_default_roles()

    for user in User.query.all():
        if list(user.roles):
            continue
        if user.firebase_uid:
            RoleRepository.attach_role_to_user(user, ROLE_CUSTOMER)