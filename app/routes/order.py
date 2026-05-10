# app/routes/order.py
"""Order tracking routes - THIN controller"""

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.order_service import OrderService

order_bp = Blueprint("order", __name__)


@order_bp.route("/order/<int:order_id>/track")
@login_required
def order_tracking(order_id):
    """Track order with timeline"""
    result = OrderService.get_tracking_info(order_id, current_user.id)

    if not result.success:
        if result.data and result.data.get('forbidden'):
            flash('Access denied', 'danger')
        else:
            flash(result.error, 'danger')
        return redirect(url_for('order.my_orders'))

    return render_template("orders/order_tracking.html", order=result.data)

# --- New Route for Order History ---
@order_bp.route("/my-orders")
@login_required
def my_orders():
    # Retrieve orders from the current_user object and sort them by date (Newest First)
    user_orders = current_user.orders if current_user.orders else []
    orders = sorted(user_orders, key=lambda x: x.created_at, reverse=True)    
    # Render the history template and pass the orders list
    return render_template("orders/my_orders.html", orders=orders)
