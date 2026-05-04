"""
cart_repository.py — The data-access layer for the Cart System.

This is the ONLY place that touches the database for cart operations.
Controllers call these functions; they never write SQL themselves.

Pattern: Repository = the middleman between code and database.
"""

from database import get_db
from models.cart_model import CartItem, Cart


# ─────────────────────────────────────────────
#  READ
# ─────────────────────────────────────────────

def get_cart(user_id: int) -> Cart:
    """Returns the full Cart object for a user (empty cart if nothing found)."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM cart_items WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()

    items = [_row_to_item(row) for row in rows]
    return Cart(user_id=user_id, items=items)


def get_cart_item(user_id: int, product_id: int):
    """Returns a single CartItem or None if not in cart."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM cart_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    ).fetchone()
    conn.close()
    return _row_to_item(row) if row else None


# ─────────────────────────────────────────────
#  WRITE
# ─────────────────────────────────────────────

def add_item(user_id: int, product_id: int, product_name: str,
             product_price: float, quantity: int = 1,
             image_url: str = None) -> CartItem:
    """
    Adds a product to the cart.
    If the product already exists for this user, increments quantity instead.
    Returns the final CartItem saved in the DB.
    """
    if quantity < 1:
        raise ValueError("Quantity must be at least 1.")
    if product_price < 0:
        raise ValueError("Price cannot be negative.")

    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM cart_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    ).fetchone()

    if existing:
        new_qty = existing["quantity"] + quantity
        conn.execute(
            "UPDATE cart_items SET quantity = ? WHERE user_id = ? AND product_id = ?",
            (new_qty, user_id, product_id)
        )
    else:
        conn.execute(
            """INSERT INTO cart_items
               (user_id, product_id, product_name, product_price, quantity, image_url)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, product_id, product_name, product_price, quantity, image_url)
        )

    conn.commit()
    row = conn.execute(
        "SELECT * FROM cart_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    ).fetchone()
    conn.close()
    return _row_to_item(row)


def update_quantity(user_id: int, product_id: int, new_quantity: int) -> bool:
    """
    Updates the quantity of an item.
    Returns True if updated, False if item not found.
    Raises ValueError if quantity < 1.
    """
    if new_quantity < 1:
        raise ValueError("Quantity must be at least 1. Use remove_item to delete.")

    conn = get_db()
    cursor = conn.execute(
        "UPDATE cart_items SET quantity = ? WHERE user_id = ? AND product_id = ?",
        (new_quantity, user_id, product_id)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def remove_item(user_id: int, product_id: int) -> bool:
    """
    Removes a specific item from the cart.
    Returns True if removed, False if it wasn't in the cart.
    """
    conn = get_db()
    cursor = conn.execute(
        "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def clear_cart(user_id: int) -> int:
    """
    Removes ALL items from a user's cart (called after checkout).
    Returns the number of rows deleted.
    """
    conn = get_db()
    cursor = conn.execute(
        "DELETE FROM cart_items WHERE user_id = ?", (user_id,)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount


# ─────────────────────────────────────────────
#  PRIVATE HELPER
# ─────────────────────────────────────────────

def _row_to_item(row) -> CartItem:
    """Converts a sqlite3.Row to a CartItem dataclass."""
    return CartItem(
        id=row["id"],
        user_id=row["user_id"],
        product_id=row["product_id"],
        product_name=row["product_name"],
        product_price=row["product_price"],
        quantity=row["quantity"],
        image_url=row["image_url"],
    )
