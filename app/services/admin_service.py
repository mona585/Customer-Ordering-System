# app/services/admin_service.py
"""Manager / admin operations — dashboard, orders, menu."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import func as sqlfunc

from app.extensions import db
from app.models.menu_item import Category, MenuItem
from app.models.order_status_history import OrderStatusHistory
from app.models.orders import Order, OrderStatus
from app.models.user import User
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository
from app.services.base_service import BaseService, ServiceResult


class AdminService(BaseService):
    """Business logic for the admin (manager) area."""

    # ----- Dashboard -----

    @staticmethod
    def get_dashboard_stats() -> ServiceResult:
        today = datetime.utcnow().date()

        total_orders = Order.query.count()
        pending_orders = Order.query.filter(Order.status == OrderStatus.PENDING).count()

        orders_today = Order.query.filter(sqlfunc.date(Order.created_at) == today).count()

        revenue_row = (
            db.session.query(sqlfunc.coalesce(sqlfunc.sum(Order.total_amount), 0))
            .filter(
                sqlfunc.date(Order.created_at) == today,
                Order.status != OrderStatus.CANCELLED,
            )
            .scalar()
        )
        revenue_today = float(revenue_row or 0)

        menu_items = MenuItem.query.count()
        users = User.query.count()

        return ServiceResult.ok(
            data={
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "orders_today": orders_today,
                "revenue_today": revenue_today,
                "menu_items": menu_items,
                "users": users,
            }
        )

    # ----- Orders -----

    @staticmethod
    def parse_order_status(raw: str | None) -> OrderStatus | None:
        if not raw:
            return None
        key = raw.strip().upper()
        try:
            return OrderStatus[key]
        except KeyError:
            return None

    @staticmethod
    def list_orders(status_filter: str | None = None) -> ServiceResult:
        status_enum = AdminService.parse_order_status(status_filter)
        orders = OrderRepository.list_for_admin(status=status_enum, limit=200)
        return ServiceResult.ok(data=orders)

    @staticmethod
    def get_order_for_admin(order_id: int) -> ServiceResult:
        order = OrderRepository.get_by_id_with_relations(order_id)
        if not order:
            return ServiceResult.fail("Order not found")
        return ServiceResult.ok(data=order)

    @staticmethod
    def update_order_status(order_id: int, new_status_raw: str) -> ServiceResult:
        new_status = AdminService.parse_order_status(new_status_raw)
        if new_status is None:
            return ServiceResult.fail("Invalid order status.")

        order = OrderRepository.get_by_id(order_id)
        if not order:
            return ServiceResult.fail("Order not found")

        try:
            OrderRepository.update_status(order, new_status)
            history = OrderStatusHistory(order_id=order.id, status=new_status.name)
            OrderRepository.create_status_history(history)
            if OrderRepository.commit():
                return ServiceResult.ok(message="Order status updated.")
            return ServiceResult.fail("Could not save status change.")
        except Exception as exc:  # pragma: no cover
            db.session.rollback()
            return ServiceResult.fail(str(exc))

    # ----- Menu -----

    @staticmethod
    def list_menu_items() -> ServiceResult:
        items = MenuRepository.list_all_for_admin()
        return ServiceResult.ok(data=items)

    @staticmethod
    def get_menu_item(item_id: int) -> ServiceResult:
        item = MenuRepository.get_by_id(item_id)
        if not item:
            return ServiceResult.fail("Menu item not found")
        return ServiceResult.ok(data=item)

    @staticmethod
    def update_menu_item(item_id: int, form: dict) -> ServiceResult:
        item = MenuRepository.get_by_id(item_id)
        if not item:
            return ServiceResult.fail("Menu item not found")

        name = (form.get("name") or "").strip()
        if not name:
            return ServiceResult.fail("Name is required.")

        category_key = (form.get("category") or "").strip()
        try:
            category = Category[category_key]
        except KeyError:
            return ServiceResult.fail("Invalid category.")

        try:
            price = Decimal(str(form.get("price", "0")).strip())
            if price < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError, TypeError):
            return ServiceResult.fail("Invalid price.")

        try:
            stock = int(form.get("stock_quantity", 0))
            prep = int(form.get("preparation_time", 15))
            calories = form.get("calories") or ""
            calories_int = int(calories) if str(calories).strip() != "" else None
        except (ValueError, TypeError):
            return ServiceResult.fail("Invalid numeric field.")

        item.name = name
        item.description = (form.get("description") or "").strip() or None
        item.price = price
        item.category = category
        item.stock_quantity = max(0, stock)
        item.preparation_time = max(1, prep)
        item.calories = calories_int
        item.ingredients = (form.get("ingredients") or "").strip() or None
        item.is_available = form.get("is_available") == "on"

        MenuRepository.save(item)
        if MenuRepository.commit():
            return ServiceResult.ok(message="Menu item saved.")
        return ServiceResult.fail("Could not save menu item.")

    @staticmethod
    def toggle_menu_item_availability(item_id: int) -> ServiceResult:
        item = MenuRepository.get_by_id(item_id)
        if not item:
            return ServiceResult.fail("Menu item not found")
        item.is_available = not bool(item.is_available)
        MenuRepository.save(item)
        if MenuRepository.commit():
            return ServiceResult.ok(
                data={"is_available": item.is_available},
                message="Availability updated.",
            )
        return ServiceResult.fail("Could not update availability.")
