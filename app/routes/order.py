

from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from app.models.orders import Order

order_bp = Blueprint("order", __name__)

@order_bp.route("/order/<int:order_id>/track")
@login_required
def order_tracking(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Security check - only owner can view
    if order.customer_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('customer.orders'))
    
    return render_template("orders/order_tracking.html", order=order)

