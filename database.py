"""
database.py — SQLite connection helper and table initialization.
All other modules import get_db() from here.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ordering_system.db")


def get_db() -> sqlite3.Connection:
    """Opens a new SQLite connection with row_factory set to Row."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets us access columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    Creates the cart_items table if it doesn't exist.
    Call this once on app startup from app.py.

    NOTE: This only creates the cart table. The `users` and `products`
    tables are created by the Auth and Product teams respectively.
    We reference them as foreign keys but do NOT recreate them here.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            product_id    INTEGER NOT NULL,
            product_name  TEXT    NOT NULL,
            product_price REAL    NOT NULL CHECK(product_price >= 0),
            quantity      INTEGER NOT NULL DEFAULT 1 CHECK(quantity >= 1),
            image_url     TEXT,
            UNIQUE(user_id, product_id)   -- one row per product per user
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] cart_items table ready.")


if __name__ == "__main__":
    init_db()
