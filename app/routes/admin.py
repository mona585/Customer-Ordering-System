# app/routes/admin.py

from flask import Blueprint
from flask_login import login_required

from app.security.rbac import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
@role_required("admin")
def dashboard():
    return "<h1>Admin dashboard</h1><p>Replace with real manager UI.</p>", 200