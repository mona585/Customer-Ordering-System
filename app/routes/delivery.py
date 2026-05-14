# app/routes/delivery.py

from flask import Blueprint
from flask_login import login_required

from app.security.rbac import role_required

delivery_bp = Blueprint("delivery", __name__, url_prefix="/delivery")


@delivery_bp.route("/")
@login_required
@role_required("delivery")
def dashboard():
    return "<h1>Delivery dashboard</h1><p>Replace with real delivery UI.</p>", 200