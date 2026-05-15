# app/security/rbac.py

from __future__ import annotations

from functools import wraps

from flask import abort, redirect, request, url_for
from flask_login import current_user, login_required

from app.constants.roles import ROLE_CHEF, ROLE_CUSTOMER


def role_required(*allowed_slugs: str):
    """
    Require the logged-in user to have at least one of the given role slugs.
    Stack after @login_required on view functions.

    Example:
        @login_required
        @role_required("admin")
        def admin_page():
            ...
    """

    if not allowed_slugs:
        raise ValueError("role_required() needs at least one role slug.")

    def decorator(view_fn):
        @wraps(view_fn)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login", next=request.url))
            if not any(current_user.has_role(slug) for slug in allowed_slugs):
                abort(403)
            return view_fn(*args, **kwargs)

        return wrapped

    return decorator


def get_post_login_redirect(user) -> str:
    """
    Return a relative URL (from url_for) for the user's default landing page.
    Priority when multiple staff roles exist: admin > delivery > chef > customer.
    """
    if not getattr(user, "is_active", True):
        return url_for("auth.login")

    if user.has_role("admin"):
        return url_for("admin.dashboard")
    if user.has_role("delivery"):
        return url_for("delivery.dashboard")
    if user.has_role(ROLE_CHEF):
        # Kitchen dashboard can replace this endpoint later.
        return url_for("main.home")
    if user.has_role(ROLE_CUSTOMER):
        return url_for("customer.menu")
    # User has no recognizable role — safe default.
    return url_for("main.home")