# app/repositories/cart_repository.py
"""Cart data access layer - handles session-based cart operations"""


class CartRepository:
    """Abstracts cart session storage operations"""

    @staticmethod
    def get_cart(session):
        return session.get('cart', {})

    @staticmethod
    def save_cart(session, cart_data):
        session['cart'] = cart_data
        session.modified = True

    @staticmethod
    def clear_cart(session):
        session.pop('cart', None)
        session.modified = True

    @staticmethod
    def get_item_quantity(cart_data, item_id):
        return cart_data.get(str(item_id), {}).get('quantity', 0)

    @staticmethod
    def update_item(cart_data, item_id, quantity, special_requests=''):
        if str(item_id) in cart_data:
            cart_data[str(item_id)]['quantity'] = quantity
            if special_requests:
                cart_data[str(item_id)]['special_requests'] = special_requests
        else:
            cart_data[str(item_id)] = {
                'quantity': quantity,
                'special_requests': special_requests
            }
        return cart_data

    @staticmethod
    def remove_item(cart_data, item_id):
        str_id = str(item_id)
        if str_id in cart_data:
            del cart_data[str_id]
        return cart_data

    @staticmethod
    def get_total_count(cart_data):
        return sum(item['quantity'] for item in cart_data.values())
