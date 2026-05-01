"""
cart_controller.py — Flask Blueprint for all Cart routes.

URL Prefix: /cart
All routes expect a logged-in user (user_id stored in session).

API Contract (used by frontend JS):
    GET  /cart/             → renders cart page (HTML)
    GET  /cart/api          → returns cart JSON  { cart: {...} }
    POST /cart/add          → add item           { product_id, product_name, product_price, quantity?, image_url? }
    POST /cart/update       → change quantity    { product_id, quantity }
    POST /cart/remove       → remove one item    { product_id }
    POST /cart/clear        → empty cart         {}
"""

from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
import repository.cart_repository as repo

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


# ─────────────────────────────────────────────
#  Helper
# ─────────────────────────────────────────────

def _get_user_id():
    """Returns user_id from session, or None if not logged in."""
    return session.get("user_id")


def _require_login():
    """Returns a 401 JSON response if user is not in session."""
    uid = _get_user_id()
    if not uid:
        return None, jsonify({"error": "Not logged in"}), 401
    return uid, None, None


# ─────────────────────────────────────────────
#  VIEW (HTML)
# ─────────────────────────────────────────────

@cart_bp.route("/")
def cart_page():
    """Renders the cart HTML page. Redirects to login if not authenticated."""
    user_id = _get_user_id()
    if not user_id:
        return redirect("/dev-login")

    cart = repo.get_cart(user_id)
    return render_template("cart.html", cart=cart)


# ─────────────────────────────────────────────
#  API — Read
# ─────────────────────────────────────────────

@cart_bp.route("/api", methods=["GET"])
def get_cart_api():
    """Returns cart as JSON. Used by frontend JS for dynamic updates."""
    user_id = _get_user_id()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    cart = repo.get_cart(user_id)
    return jsonify({"cart": cart.to_dict()}), 200


# ─────────────────────────────────────────────
#  API — Add Item
# ─────────────────────────────────────────────

@cart_bp.route("/add", methods=["POST"])
def add_to_cart():
    """
    Adds a product to the cart.
    Request body (JSON):
        product_id    (int, required)
        product_name  (str, required)
        product_price (float, required, >= 0)
        quantity      (int, optional, default=1, >= 1)
        image_url     (str, optional)
    """
    user_id = _get_user_id()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json(silent=True) or {}

    # ── Validate required fields ──────────────────
    product_id = data.get("product_id")
    product_name = data.get("product_name", "").strip()
    product_price = data.get("product_price")
    quantity = data.get("quantity", 1)

    if not product_id or not isinstance(product_id, int):
        return jsonify({"error": "product_id must be a positive integer"}), 400
    if not product_name:
        return jsonify({"error": "product_name is required"}), 400
    if product_price is None or not isinstance(product_price, (int, float)) or product_price < 0:
        return jsonify({"error": "product_price must be a non-negative number"}), 400
    if not isinstance(quantity, int) or quantity < 1:
        return jsonify({"error": "quantity must be a positive integer"}), 400
    if quantity > 99:
        return jsonify({"error": "quantity cannot exceed 99 per item"}), 400

    try:
        item = repo.add_item(
            user_id=user_id,
            product_id=product_id,
            product_name=product_name,
            product_price=float(product_price),
            quantity=quantity,
            image_url=data.get("image_url"),
        )
        cart = repo.get_cart(user_id)
        return jsonify({
            "message": "Item added to cart",
            "item": item.to_dict(),
            "cart_total": cart.grand_total(),
            "cart_count": cart.item_count(),
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# ─────────────────────────────────────────────
#  API — Update Quantity
# ─────────────────────────────────────────────

@cart_bp.route("/update", methods=["POST"])
def update_cart():
    """
    Updates quantity of an existing cart item.
    Request body (JSON):
        product_id  (int)
        quantity    (int, >= 1)
    """
    user_id = _get_user_id()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not isinstance(product_id, int):
        return jsonify({"error": "product_id must be a positive integer"}), 400
    if not isinstance(quantity, int) or quantity < 1:
        return jsonify({"error": "quantity must be a positive integer >= 1"}), 400
    if quantity > 99:
        return jsonify({"error": "quantity cannot exceed 99 per item"}), 400

    try:
        updated = repo.update_quantity(user_id, product_id, quantity)
        if not updated:
            return jsonify({"error": "Item not found in cart"}), 404
        cart = repo.get_cart(user_id)
        return jsonify({
            "message": "Quantity updated",
            "cart_total": cart.grand_total(),
            "cart_count": cart.item_count(),
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# ─────────────────────────────────────────────
#  API — Remove Item
# ─────────────────────────────────────────────

@cart_bp.route("/remove", methods=["POST"])
def remove_from_cart():
    """
    Removes one specific item from cart.
    Request body (JSON):
        product_id (int)
    """
    user_id = _get_user_id()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")

    if not product_id or not isinstance(product_id, int):
        return jsonify({"error": "product_id must be a positive integer"}), 400

    removed = repo.remove_item(user_id, product_id)
    if not removed:
        return jsonify({"error": "Item not found in cart"}), 404

    cart = repo.get_cart(user_id)
    return jsonify({
        "message": "Item removed",
        "cart_total": cart.grand_total(),
        "cart_count": cart.item_count(),
    }), 200


# ─────────────────────────────────────────────
#  API — Clear Cart
# ─────────────────────────────────────────────

@cart_bp.route("/clear", methods=["POST"])
def clear_cart():
    """
    Removes ALL items from the user's cart.
    Called by the Order/Checkout team after a successful order.
    """
    user_id = _get_user_id()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    count = repo.clear_cart(user_id)
    return jsonify({"message": f"Cart cleared. {count} item(s) removed."}), 200
