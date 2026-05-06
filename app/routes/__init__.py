# app/routes/__init__.py
"""Routes package"""

from .auth import auth_bp
from .main import main_bp
from .customer import customer_bp
from .order import order_bp

__all__ = ['auth_bp', 'main_bp', 'customer_bp', 'order_bp']