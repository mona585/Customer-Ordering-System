"""
test_cart.py — Unit + Integration tests for the Cart System.

Test Pyramid target:
    70% Unit tests  → test logic & repository functions in isolation
    20% Integration → test Flask routes end-to-end with a test client
    10% E2E         → handled by Playwright (see test_cart_e2e.py)

Run with:  python -m pytest tests/test_cart.py -v
"""

import pytest
import sys
import os

# Make sure we can import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import database
import repository.cart_repository as repo
from models.cart_model import CartItem, Cart
from app import app


# ═══════════════════════════════════════════════
#  FIXTURES
# ═══════════════════════════════════════════════

@pytest.fixture(autouse=True)
def use_test_db(tmp_path, monkeypatch):
    """
    Redirects DB_PATH to a fresh temp DB for every test.
    This ensures tests are fully isolated and don't pollute each other.
    """
    test_db = str(tmp_path / "test.db")
    monkeypatch.setattr(database, "DB_PATH", test_db)
    monkeypatch.setattr("repository.cart_repository.get_db",
                        lambda: _get_test_db(test_db))
    monkeypatch.setattr("database.get_db",
                        lambda: _get_test_db(test_db))
    database.init_db()
    yield


def _get_test_db(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@pytest.fixture
def flask_client():
    """Flask test client with session support."""
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1   # Simulate logged-in user
        yield client


# ═══════════════════════════════════════════════
#  UNIT TESTS — CartItem Model
# ═══════════════════════════════════════════════

class TestCartItemModel:

    def test_line_total_correct(self):
        """line_total = price × quantity"""
        item = CartItem(id=1, user_id=1, product_id=10,
                        product_name="Burger", product_price=5.99,
                        quantity=3, image_url=None)
        assert item.line_total() == 17.97

    def test_line_total_single_item(self):
        item = CartItem(id=1, user_id=1, product_id=10,
                        product_name="Cola", product_price=1.50,
                        quantity=1, image_url=None)
        assert item.line_total() == 1.50

    def test_line_total_zero_price(self):
        """Free items should have $0 line total"""
        item = CartItem(id=1, user_id=1, product_id=99,
                        product_name="Free Item", product_price=0.0,
                        quantity=5, image_url=None)
        assert item.line_total() == 0.0

    def test_to_dict_includes_line_total(self):
        item = CartItem(id=1, user_id=1, product_id=10,
                        product_name="Pizza", product_price=12.00,
                        quantity=2, image_url=None)
        d = item.to_dict()
        assert d["line_total"] == 24.00
        assert d["product_name"] == "Pizza"


class TestCartModel:

    def test_grand_total_sums_all_items(self):
        items = [
            CartItem(1, 1, 1, "A", 10.00, 2, None),   # 20.00
            CartItem(2, 1, 2, "B",  5.50, 3, None),   # 16.50
        ]
        cart = Cart(user_id=1, items=items)
        assert cart.grand_total() == 36.50

    def test_grand_total_empty_cart(self):
        cart = Cart(user_id=1, items=[])
        assert cart.grand_total() == 0.0

    def test_item_count(self):
        items = [
            CartItem(1, 1, 1, "A", 5.0, 3, None),
            CartItem(2, 1, 2, "B", 5.0, 2, None),
        ]
        cart = Cart(user_id=1, items=items)
        assert cart.item_count() == 5

    def test_is_empty_true(self):
        assert Cart(user_id=1, items=[]).is_empty() is True

    def test_is_empty_false(self):
        items = [CartItem(1, 1, 1, "A", 5.0, 1, None)]
        assert Cart(user_id=1, items=items).is_empty() is False


# ═══════════════════════════════════════════════
#  UNIT TESTS — Repository
# ═══════════════════════════════════════════════

class TestCartRepository:

    def test_get_cart_empty_returns_empty_cart(self):
        cart = repo.get_cart(user_id=999)
        assert cart.is_empty()
        assert cart.user_id == 999

    def test_add_item_creates_new_row(self):
        item = repo.add_item(user_id=1, product_id=5,
                             product_name="Fries", product_price=3.50)
        assert item.id is not None
        assert item.product_name == "Fries"
        assert item.quantity == 1

    def test_add_same_item_increments_quantity(self):
        repo.add_item(user_id=1, product_id=5, product_name="Fries",
                      product_price=3.50, quantity=2)
        repo.add_item(user_id=1, product_id=5, product_name="Fries",
                      product_price=3.50, quantity=3)
        item = repo.get_cart_item(user_id=1, product_id=5)
        assert item.quantity == 5   # 2 + 3

    def test_add_item_invalid_price_raises(self):
        with pytest.raises(ValueError):
            repo.add_item(user_id=1, product_id=5,
                          product_name="X", product_price=-1)

    def test_add_item_invalid_quantity_raises(self):
        with pytest.raises(ValueError):
            repo.add_item(user_id=1, product_id=5,
                          product_name="X", product_price=5.0, quantity=0)

    def test_update_quantity_success(self):
        repo.add_item(user_id=1, product_id=5,
                      product_name="Fries", product_price=3.50)
        result = repo.update_quantity(user_id=1, product_id=5, new_quantity=4)
        assert result is True
        item = repo.get_cart_item(user_id=1, product_id=5)
        assert item.quantity == 4

    def test_update_quantity_item_not_found_returns_false(self):
        result = repo.update_quantity(user_id=1, product_id=999, new_quantity=2)
        assert result is False

    def test_update_quantity_zero_raises(self):
        repo.add_item(user_id=1, product_id=5,
                      product_name="Fries", product_price=3.50)
        with pytest.raises(ValueError):
            repo.update_quantity(user_id=1, product_id=5, new_quantity=0)

    def test_remove_item_success(self):
        repo.add_item(user_id=1, product_id=5,
                      product_name="Fries", product_price=3.50)
        result = repo.remove_item(user_id=1, product_id=5)
        assert result is True
        assert repo.get_cart_item(user_id=1, product_id=5) is None

    def test_remove_nonexistent_item_returns_false(self):
        result = repo.remove_item(user_id=1, product_id=999)
        assert result is False

    def test_clear_cart_removes_all_items(self):
        repo.add_item(user_id=1, product_id=1, product_name="A", product_price=1.0)
        repo.add_item(user_id=1, product_id=2, product_name="B", product_price=2.0)
        count = repo.clear_cart(user_id=1)
        assert count == 2
        assert repo.get_cart(user_id=1).is_empty()

    def test_clear_cart_only_affects_target_user(self):
        repo.add_item(user_id=1, product_id=1, product_name="A", product_price=1.0)
        repo.add_item(user_id=2, product_id=1, product_name="A", product_price=1.0)
        repo.clear_cart(user_id=1)
        assert repo.get_cart(user_id=2).item_count() == 1   # user 2 untouched


# ═══════════════════════════════════════════════
#  INTEGRATION TESTS — Flask Routes
# ═══════════════════════════════════════════════

class TestCartRoutes:

    def test_add_item_route_success(self, flask_client):
        res = flask_client.post("/cart/add", json={
            "product_id": 1,
            "product_name": "Burger",
            "product_price": 9.99,
            "quantity": 2,
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["item"]["quantity"] == 2
        assert data["cart_count"] == 2

    def test_add_item_missing_fields(self, flask_client):
        res = flask_client.post("/cart/add", json={"product_id": 1})
        assert res.status_code == 400

    def test_add_item_negative_price(self, flask_client):
        res = flask_client.post("/cart/add", json={
            "product_id": 1,
            "product_name": "X",
            "product_price": -5,
        })
        assert res.status_code == 400

    def test_add_item_quantity_over_limit(self, flask_client):
        res = flask_client.post("/cart/add", json={
            "product_id": 1,
            "product_name": "X",
            "product_price": 5.0,
            "quantity": 100,
        })
        assert res.status_code == 400

    def test_update_quantity_route(self, flask_client):
        flask_client.post("/cart/add", json={
            "product_id": 3, "product_name": "Cola",
            "product_price": 1.50, "quantity": 1,
        })
        res = flask_client.post("/cart/update",
                                json={"product_id": 3, "quantity": 5})
        assert res.status_code == 200
        assert res.get_json()["cart_count"] == 5

    def test_remove_item_route(self, flask_client):
        flask_client.post("/cart/add", json={
            "product_id": 3, "product_name": "Cola",
            "product_price": 1.50,
        })
        res = flask_client.post("/cart/remove", json={"product_id": 3})
        assert res.status_code == 200
        assert res.get_json()["cart_count"] == 0

    def test_remove_nonexistent_item_returns_404(self, flask_client):
        res = flask_client.post("/cart/remove", json={"product_id": 999})
        assert res.status_code == 404

    def test_clear_cart_route(self, flask_client):
        flask_client.post("/cart/add", json={
            "product_id": 1, "product_name": "A", "product_price": 5.0,
        })
        flask_client.post("/cart/add", json={
            "product_id": 2, "product_name": "B", "product_price": 3.0,
        })
        res = flask_client.post("/cart/clear", json={})
        assert res.status_code == 200

    def test_unauthenticated_add_returns_401(self):
        """Without session, all routes should return 401."""
        with app.test_client() as client:
            res = client.post("/cart/add", json={
                "product_id": 1, "product_name": "X", "product_price": 5.0
            })
            assert res.status_code == 401

    def test_get_cart_api(self, flask_client):
        flask_client.post("/cart/add", json={
            "product_id": 7, "product_name": "Wrap",
            "product_price": 6.50, "quantity": 1,
        })
        res = flask_client.get("/cart/api")
        assert res.status_code == 200
        data = res.get_json()
        assert "cart" in data
        assert data["cart"]["grand_total"] == 6.50


# ═══════════════════════════════════════════════
#  EDGE CASE TESTS
# ═══════════════════════════════════════════════

class TestEdgeCases:

    def test_floating_point_total_rounded_correctly(self):
        """Grand total must handle floating point rounding properly."""
        items = [
            CartItem(1, 1, 1, "A", 0.1, 3, None),   # 0.3 (can be 0.30000000000000004)
            CartItem(2, 1, 2, "B", 0.2, 1, None),   # 0.2
        ]
        cart = Cart(user_id=1, items=items)
        assert cart.grand_total() == 0.50   # Not 0.5000000000000001

    def test_empty_product_name_rejected_by_route(self, flask_client):
        res = flask_client.post("/cart/add", json={
            "product_id": 1, "product_name": "   ",
            "product_price": 5.0,
        })
        assert res.status_code == 400

    def test_zero_quantity_update_rejected(self, flask_client):
        flask_client.post("/cart/add", json={
            "product_id": 1, "product_name": "A", "product_price": 5.0,
        })
        res = flask_client.post("/cart/update",
                                json={"product_id": 1, "quantity": 0})
        assert res.status_code == 400

    def test_large_cart_grand_total(self):
        """Cart with many items should still calculate correctly."""
        items = [
            CartItem(i, 1, i, f"Item{i}", 1.00, 1, None)
            for i in range(1, 51)   # 50 items at $1 each
        ]
        cart = Cart(user_id=1, items=items)
        assert cart.grand_total() == 50.00
        assert cart.item_count() == 50
