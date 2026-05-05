# app/models/__init__.py

# Import all models for easy access
from .user import User
from .menu_item import MenuItem, Category
from .orders import Order, OrderStatus
from .order_item import OrderItem
from .payment import Payment, PaymentStatus, PaymentMethod
from .review import Review
from .wishlist import Wishlist
from .order_status_history import OrderStatusHistory

# List all models for Flask-Migrate
__all__ = [
    'User',
    'MenuItem', 'Category',
    'Order', 'OrderStatus',
    'OrderItem',
    'Payment', 'PaymentStatus', 'PaymentMethod',
    'Review',
    'Wishlist',
    'OrderStatusHistory'
]