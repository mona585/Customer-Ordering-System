# app/routes/admin.py

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.models.menu_item import Category
from app.models.orders import OrderStatus
from app.security.rbac import role_required
from app.services.admin_service import AdminService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@login_required
@role_required("admin")
def dashboard():
    result = AdminService.get_dashboard_stats()
    stats = result.data if result.success else {}
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/orders")
@login_required
@role_required("admin")
def orders_list():
    status_filter = request.args.get("status") or None
    result = AdminService.list_orders(status_filter=status_filter)
    orders = result.data if result.success else []
    statuses = [(s.name, s.value) for s in OrderStatus]
    return render_template(
        "admin/orders_list.html",
        orders=orders,
        current_status=status_filter,
        statuses=statuses,
    )


@admin_bp.route("/orders/<int:order_id>")
@login_required
@role_required("admin")
def order_detail(order_id: int):
    result = AdminService.get_order_for_admin(order_id)
    if not result.success:
        flash(result.error, "warning")
        return redirect(url_for("admin.orders_list"))
    order_statuses = [(s.name, s.value) for s in OrderStatus]
    return render_template(
        "admin/order_detail.html",
        order=result.data,
        order_statuses=order_statuses,
    )


@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@login_required
@role_required("admin")
def order_update_status(order_id: int):
    new_status = request.form.get("status", "")
    result = AdminService.update_order_status(order_id, new_status)
    if result.success:
        flash(result.message or "Updated.", "success")
    else:
        flash(result.error or "Update failed.", "danger")
    return redirect(url_for("admin.order_detail", order_id=order_id))


@admin_bp.route("/menu")
@login_required
@role_required("admin")
def menu_list():
    result = AdminService.list_menu_items()
    items = result.data if result.success else []
    return render_template("admin/menu_list.html", items=items)


@admin_bp.route("/menu/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def menu_edit(item_id: int):
    if request.method == "POST":
        result = AdminService.update_menu_item(item_id, request.form)
        if result.success:
            flash(result.message or "Saved.", "success")
            return redirect(url_for("admin.menu_list"))
        flash(result.error or "Save failed.", "danger")

    result = AdminService.get_menu_item(item_id)
    if not result.success:
        flash(result.error, "warning")
        return redirect(url_for("admin.menu_list"))
    categories = [(c.name, c.value) for c in Category]
    return render_template(
        "admin/menu_edit.html",
        item=result.data,
        categories=categories,
    )


@admin_bp.route("/menu/<int:item_id>/toggle-availability", methods=["POST"])
@login_required
@role_required("admin")
def menu_toggle_availability(item_id: int):
    result = AdminService.toggle_menu_item_availability(item_id)
    if result.success:
        flash(result.message or "Updated.", "success")
    else:
        flash(result.error or "Update failed.", "danger")
    return redirect(url_for("admin.menu_list"))
