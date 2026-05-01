"""
Cart Model — defines the shape of cart data in the database.
Follows the MVC + Repository pattern used in this project.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CartItem:
    """Represents a single item in a user's cart."""
    id: Optional[int]          # DB primary key (None before insert)
    user_id: int               # FK to users table (from Auth system)
    product_id: int            # FK to products table (from Product system)
    product_name: str          # Denormalized for display speed
    product_price: float       # Snapshot price at time of adding
    quantity: int              # Must be >= 1
    image_url: Optional[str]   # Optional product image

    def line_total(self) -> float:
        """Returns price * quantity for this line item."""
        return round(self.product_price * self.quantity, 2)

    def to_dict(self) -> dict:
        """Serializes the item to a JSON-safe dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_price": self.product_price,
            "quantity": self.quantity,
            "image_url": self.image_url,
            "line_total": self.line_total(),
        }


@dataclass
class Cart:
    """Represents the full cart for a user (a collection of CartItems)."""
    user_id: int
    items: list  # list[CartItem]

    def grand_total(self) -> float:
        """Sums all line totals."""
        return round(sum(item.line_total() for item in self.items), 2)

    def item_count(self) -> int:
        """Total number of individual units in the cart."""
        return sum(item.quantity for item in self.items)

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "items": [item.to_dict() for item in self.items],
            "grand_total": self.grand_total(),
            "item_count": self.item_count(),
        }
