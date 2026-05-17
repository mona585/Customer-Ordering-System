# app/services/cart_service.py
"""Shopping cart business logic"""

from app.repositories.menu_repository import MenuRepository
from app.repositories.cart_repository import CartRepository
from app.services.base_service import BaseService, ServiceResult


class CartService(BaseService):
    """Handles cart operations: add, update, remove, validate"""

    @staticmethod
    def get_cart_items(cart_data):
        """Get full cart items with validation"""
        if not cart_data:
            return ServiceResult.ok(data={'items': [], 'total': 0, 'errors': []})

        cart_items = []
        cart_total = 0
        stock_errors = []

        for item_id, item_data in cart_data.items():
            menu_item = MenuRepository.get_by_id(int(item_id))
            if not menu_item:
                continue

            quantity = item_data.get('quantity', 1)
            available = menu_item.available_stock

            if quantity > available:
                stock_errors.append(f"{menu_item.name}: Only {available} available")
                quantity = min(quantity, available)

            unit_price = float(menu_item.price)
            subtotal = unit_price * quantity
            cart_total += subtotal

            cart_items.append({
                'id': f"temp_{item_id}",
                'menu_item': menu_item,
                'quantity': quantity,
                'unit_price': unit_price,
                'subtotal': subtotal,
                'special_requests': item_data.get('special_requests', ''),
                'available_stock': available
            })

        return ServiceResult.ok(data={
            'items': cart_items,
            'total': cart_total,
            'errors': stock_errors
        })

    @staticmethod
    def apply_promo_code(cart_total, promo_code):
        """Validate public promo code against shared checkout rules."""
        from app.services.checkout_service import CheckoutService

        if not promo_code:
            return ServiceResult.fail("Please enter a code")

        code = promo_code.strip().upper()
        result = CheckoutService._validate_promo(code, float(cart_total))
        if not result.success:
            return result

        discount_amount = result.data["discount"]
        return ServiceResult.ok(
            data={"discount": discount_amount, "code": code},
            message=f"Code {code} applied!",
        )

    @staticmethod
    def add_to_cart(cart_data, item_id, quantity=1, special_requests=''):
        """Add item to cart with stock validation"""
        if not item_id:
            return ServiceResult.fail("Invalid item ID")

        menu_item = MenuRepository.get_by_id(item_id)
        if not menu_item:
            return ServiceResult.fail("Item not found")

        available = menu_item.available_stock
        current_qty = CartRepository.get_item_quantity(cart_data, item_id)
        total_requested = current_qty + quantity

        if total_requested > available:
            return ServiceResult.fail(
                f"Sorry, only {available} of {menu_item.name} available. "
                f"You have {current_qty} in cart."
            )

        cart_data = CartRepository.update_item(cart_data, item_id, 
                                               current_qty + quantity, 
                                               special_requests)

        cart_count = CartRepository.get_total_count(cart_data)

        return ServiceResult.ok(data={
            'cart': cart_data,
            'cart_count': cart_count,
            'item_name': menu_item.name,
            'item_price': float(menu_item.price)
        }, message=f'{menu_item.name} added to cart!')

    @staticmethod
    def update_cart_item(cart_data, item_id, new_quantity):
        """Update item quantity in cart"""
        menu_item = MenuRepository.get_by_id(item_id)
        if not menu_item:
            return ServiceResult.fail("Item not found")

        str_id = str(item_id)
        if str_id not in cart_data:
            return ServiceResult.fail("Item not in cart")

        available = menu_item.available_stock
        current_qty = cart_data[str_id]['quantity']

        if new_quantity > current_qty:
            extra_needed = new_quantity - current_qty
            if extra_needed > available:
                return ServiceResult.fail(
                    f"Only {available + current_qty} total available"
                )

        if new_quantity <= 0:
            cart_data = CartRepository.remove_item(cart_data, item_id)
            return ServiceResult.ok(
                data={'cart': cart_data, 'removed': True},
                message="Item removed from cart"
            )

        cart_data = CartRepository.update_item(cart_data, item_id, new_quantity)

        return ServiceResult.ok(
            data={'cart': cart_data, 'removed': False},
            message="Cart updated"
        )

    @staticmethod
    def remove_from_cart(cart_data, item_id):
        """Remove item from cart"""
        if str(item_id) in cart_data:
            cart_data = CartRepository.remove_item(cart_data, item_id)
            return ServiceResult.ok(
                data={'cart': cart_data},
                message="Item removed from cart"
            )
        return ServiceResult.fail("Item not found in cart")

    @staticmethod
    def get_cart_count(cart_data):
        """Get total items count in cart"""
        count = CartRepository.get_total_count(cart_data)
        return ServiceResult.ok(data={'count': count})

    @staticmethod
    def validate_cart_for_checkout(cart_data):
        """Validate all items before checkout"""
        result = CartService.get_cart_items(cart_data)
        if not result.success:
            return result

        data = result.data
        if not data['items']:
            return ServiceResult.fail("Your cart is empty")

        if data['errors']:
            return ServiceResult.fail(
                "Stock issues found",
                data={'stock_errors': data['errors']}
            )

        return ServiceResult.ok(data=data) 