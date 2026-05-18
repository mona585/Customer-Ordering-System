"""Unit tests for AdminService (admin business logic)."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

import pytest

from app.extensions import db
from app.models.menu_item import Category, MenuItem
from app.models.orders import Order, OrderStatus
from app.services.admin_service import AdminService


class TestParseOrderStatus:
    def test_valid_status_keys(self):
        assert AdminService.parse_order_status("CONFIRMED") == OrderStatus.CONFIRMED
        assert AdminService.parse_order_status("preparing") == OrderStatus.PREPARING

    def test_invalid_or_empty(self):
        assert AdminService.parse_order_status("") is None
        assert AdminService.parse_order_status("NOT_A_STATUS") is None
        assert AdminService.parse_order_status(None) is None


class TestDashboardStats:
    def test_empty_database_returns_zeros(self, app):
        with app.app_context():
            result = AdminService.get_dashboard_stats()
        assert result.success is True
        data = result.data
        assert data["total_orders"] == 0
        assert data["pending_orders"] == 0
        assert data["revenue_today"] == 0.0
        assert data["menu_items"] == 0
        assert len(data["daily_series"]) == 7

    def test_counts_orders_and_revenue(self, app, sample_order, menu_item):
        with app.app_context():
            result = AdminService.get_dashboard_stats()
        assert result.success is True
        data = result.data
        assert data["total_orders"] == 1
        assert data["orders_by_status"]["Confirmed"] == 1
        assert data["menu_items"] >= 1


class TestOrderManagement:
    def test_list_orders_all(self, app, sample_order):
        with app.app_context():
            result = AdminService.list_orders()
        assert result.success is True
        assert len(result.data) == 1

    def test_list_orders_filtered(self, app, sample_order):
        with app.app_context():
            confirmed = AdminService.list_orders("CONFIRMED")
            pending = AdminService.list_orders("PENDING")
        assert len(confirmed.data) == 1
        assert len(pending.data) == 0

    def test_get_order_for_admin_found(self, app, sample_order):
        with app.app_context():
            result = AdminService.get_order_for_admin(sample_order.id)
        assert result.success is True
        assert result.data.id == sample_order.id

    def test_get_order_for_admin_not_found(self, app):
        with app.app_context():
            result = AdminService.get_order_for_admin(99999)
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_update_order_status_invalid(self, app, sample_order):
        with app.app_context():
            result = AdminService.update_order_status(sample_order.id, "INVALID")
        assert result.success is False
        assert "invalid" in result.error.lower()

    def test_update_order_status_not_found(self, app):
        with app.app_context():
            result = AdminService.update_order_status(99999, "PREPARING")
        assert result.success is False

    @patch("app.services.order_lifecycle_service.OrderLifecycleService.on_status_change")
    def test_update_order_status_success(
        self, mock_lifecycle, app, sample_order
    ):
        with app.app_context():
            result = AdminService.update_order_status(
                sample_order.id, "PREPARING"
            )
            order = db.session.get(Order, sample_order.id)
        assert result.success is True
        assert order.status == OrderStatus.PREPARING
        mock_lifecycle.assert_called_once()


class TestMenuManagement:
    def test_list_menu_items(self, app, menu_item):
        with app.app_context():
            result = AdminService.list_menu_items()
        assert result.success is True
        assert any(i.id == menu_item.id for i in result.data)

    def test_get_menu_item_not_found(self, app):
        with app.app_context():
            result = AdminService.get_menu_item(99999)
        assert result.success is False

    def test_update_menu_item_validation(self, app, menu_item):
        with app.app_context():
            empty_name = AdminService.update_menu_item(menu_item.id, {"name": ""})
            bad_cat = AdminService.update_menu_item(
                menu_item.id,
                {"name": "X", "category": "INVALID", "price": "5"},
            )
            bad_price = AdminService.update_menu_item(
                menu_item.id,
                {"name": "X", "category": "APPETIZERS", "price": "-1"},
            )
        assert empty_name.success is False
        assert bad_cat.success is False
        assert bad_price.success is False

    def test_update_menu_item_success(self, app, menu_item):
        with app.app_context():
            result = AdminService.update_menu_item(
                menu_item.id,
                {
                    "name": "Updated Nachos",
                    "category": "APPETIZERS",
                    "price": "14.50",
                    "stock_quantity": "25",
                    "preparation_time": "12",
                    "description": "New desc",
                    "is_available": "on",
                },
            )
            item = db.session.get(MenuItem, menu_item.id)
        assert result.success is True
        assert item.name == "Updated Nachos"
        assert item.price == Decimal("14.50")
        assert item.stock_quantity == 25

    def test_toggle_menu_item_availability(self, app, menu_item):
        with app.app_context():
            original = menu_item.is_available
            result = AdminService.toggle_menu_item_availability(menu_item.id)
            item = db.session.get(MenuItem, menu_item.id)
        assert result.success is True
        assert item.is_available is not original

    def test_toggle_menu_item_not_found(self, app):
        with app.app_context():
            result = AdminService.toggle_menu_item_availability(99999)
        assert result.success is False
