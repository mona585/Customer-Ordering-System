# app/routes/order.py
"""Order tracking routes - THIN controller"""

import logging

from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)

order_bp = Blueprint("order", __name__)
api_order_bp = Blueprint("api_order", __name__)

DEMO_FLOW_KEYS = {s.name for s in OrderService.DEMO_FLOW}


@order_bp.route("/order/<int:order_id>/track")
@login_required
def order_tracking(order_id):
    """Track order with timeline"""
    demo_mode = request.args.get("demo") == "1"

    if demo_mode:
        order = OrderRepository.get_by_id(order_id)
        current_key = OrderService._status_key(order) if order else None
        in_demo_flow = current_key in DEMO_FLOW_KEYS
        should_reset = request.args.get("restart") == "1" or not in_demo_flow
        if should_reset:
            logger.info(
                "[Demo] reset order=%s status=%s restart=%s",
                order_id,
                current_key,
                request.args.get("restart"),
            )
            start = OrderService.demo_start(order_id, current_user.id)
            if not start.success:
                flash(start.error, "danger")
                return redirect(url_for("order.my_orders"))

    result = OrderService.get_tracking_info(order_id, current_user.id)

    if not result.success:
        if result.data and result.data.get('forbidden'):
            flash('Access denied', 'danger')
        else:
            flash(result.error, 'danger')
        return redirect(url_for('order.my_orders'))

    return render_template(
        "orders/order_tracking.html",
        order=result.data["order"],
        tracking=result.data["tracking"],
        demo_mode=demo_mode,
    )


@order_bp.route("/order/<int:order_id>/demo-advance", methods=["POST"])
@login_required
def demo_advance(order_id):
    """Legacy form POST — redirects back to tracking with demo=1."""
    result = OrderService.demo_advance(order_id, current_user.id)
    if not result.success:
        flash(result.error, "danger")
    return redirect(url_for("order.order_tracking", order_id=order_id, demo=1))


@api_order_bp.route("/api/order/<int:order_id>/advance", methods=["POST"])
@login_required
def api_order_advance(order_id):
    """JSON endpoint for demo auto-advance (CONFIRMED → PREPARING → READY → DELIVERED)."""
    result = OrderService.demo_advance(order_id, current_user.id)
    if not result.success:
        logger.warning("[Demo] advance failed order=%s: %s", order_id, result.error)
        return jsonify(success=False, error=result.error), 400

    status = result.data.get("status")
    logger.info("[Demo] advanced order=%s -> %s", order_id, status)
    return jsonify(
        success=True,
        status=status,
        done=result.data.get("done", False),
    )

# --- New Route for Order History ---
@order_bp.route("/my-orders")
@login_required
def my_orders():
    # Retrieve orders from the current_user object and sort them by date (Newest First)
    user_orders = current_user.orders if current_user.orders else []
    orders = sorted(user_orders, key=lambda x: x.created_at, reverse=True)    
    # Render the history template and pass the orders list
    return render_template("orders/my_orders.html", orders=orders)
