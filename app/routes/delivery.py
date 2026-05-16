# app/routes/delivery.py

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.models.orders import OrderStatus
from app.security.rbac import role_required
from app.services.delivery_service import DELIVERY_PIPELINE, DeliveryService

delivery_bp = Blueprint("delivery", __name__, url_prefix="/delivery")


@delivery_bp.route("/")
@login_required
@role_required("delivery")
def dashboard():
    status_filter = request.args.get("status") or None
    result = DeliveryService.list_delivery_orders(status_filter=status_filter)
    orders_data = result.data if result.success else []
    if not result.success and result.error:
        flash(result.error, "warning")

    delivery_statuses = [
        (s.name, DeliveryService.delivery_status_label(s))
        for s in DELIVERY_PIPELINE
    ]
    return render_template(
        "delivery/dashboard.html",
        orders_data=orders_data,
        current_status=status_filter,
        delivery_statuses=delivery_statuses,
    )


@delivery_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@login_required
@role_required("delivery")
def update_order_status(order_id: int):
    result = DeliveryService.advance_delivery_status(order_id)
    if result.success:
        flash(result.message or "Status updated.", "success")
    else:
        flash(result.error or "Update failed.", "danger")
    status = request.args.get("status") or None
    return redirect(url_for("delivery.dashboard", status=status) if status else url_for("delivery.dashboard"))
