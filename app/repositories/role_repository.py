# app/repositories/role_repository.py

from __future__ import annotations

from app.constants.roles import (
    DEFAULT_ROLE_SLUGS,
    ROLE_ADMIN,
    ROLE_CHEF,
    ROLE_CUSTOMER,
    ROLE_DELIVERY,
)
from app.extensions import db
from app.models.role import Role
from app.models.user import User


_ROLE_SEED_META: dict[str, tuple[str, str]] = {
    ROLE_CUSTOMER: ("Customer", "Public self-signup; customer app access."),
    ROLE_ADMIN: ("Manager / Admin", "Internal staff; manager dashboard."),
    ROLE_DELIVERY: ("Delivery", "Internal staff; delivery dashboard."),
    ROLE_CHEF: ("Chef", "Internal staff; kitchen dashboard (future)."),
}


class RoleRepository:
    """Persistence helpers for roles and user–role links."""

    @staticmethod
    def get_by_slug(slug: str) -> Role | None:
        return Role.query.filter_by(slug=slug).first()

    @staticmethod
    def ensure_default_roles() -> None:
        """Insert missing core roles (idempotent). Call on app startup or from seed scripts."""
        changed = False
        for slug in DEFAULT_ROLE_SLUGS:
            if RoleRepository.get_by_slug(slug):
                continue
            name, description = _ROLE_SEED_META.get(
                slug,
                (slug.replace("_", " ").title(), ""),
            )
            db.session.add(Role(name=name, slug=slug, description=description))
            changed = True
        if changed:
            db.session.commit()

    @staticmethod
    def attach_role_to_user(user: User, slug: str) -> None:
        """
        Attach role `slug` to `user` if not already present.
        Caller must ensure `ensure_default_roles()` has run so the row exists.
        """
        if user.has_role(slug):
            return
        role = RoleRepository.get_by_slug(slug)
        if role is None:
            raise ValueError(f"Unknown role slug: {slug!r}. Run ensure_default_roles() first.")
        user.roles.append(role)
        db.session.commit()

    @staticmethod
    def user_has_role(user: User, slug: str) -> bool:
        return user.has_role(slug)