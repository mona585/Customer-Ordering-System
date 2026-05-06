# app/services/order_service.py
"""Order business logic - checkout, creation, tracking, cancellation"""

from app.repositories.order_repository import OrderRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.cart_repository import CartRepository
from app.models.orders import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.order_status_history import OrderStatusHistory
from app.services.base_service import BaseService, ServiceResult
from app.services.cart_service import CartService


class OrderService(BaseService):
    """Handles order lifecycle: checkout, creation, tracking, cancellation"""

    # ============== CHECKOUT ==============

    @staticmethod
    def prepare_checkout(cart_data):
        """Prepare checkout page data with validation"""
        result = CartService.validate_cart_for_checkout(cart_data)
        if not result.success:
            return result

        return ServiceResult.ok(data=result.data)

    @staticmethod
    def create_order(customer_id, cart_data, delivery_address, special_instructions='', payment_method='CREDIT_CARD'):
        """Create order from cart - full transaction"""
        # Validate cart first
        result = CartService.validate_cart_for_checkout(cart_data)
        if not result.success:
            return result

        cart_result = result.data

        try:
            # Final stock check
            for cart_item in cart_result['items']:
                menu_item = cart_item['menu_item']
                if cart_item['quantity'] > menu_item.available_stock:
                    return ServiceResult.fail(
                        f"{menu_item.name} is no longer available in requested quantity"
                    )

            # Create order
            order = Order(
                customer_id=customer_id,
                total_amount=cart_result['total'],
                status=OrderStatus.PENDING,
                delivery_address=delivery_address,
                special_instructions=special_instructions
            )
            OrderRepository.create(order)

            # Create order items
            for cart_item in cart_result['items']:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=cart_item['menu_item'].id,
                    quantity=cart_item['quantity'],
                    unit_price=cart_item['unit_price'],
                    special_requests=cart_item['special_requests']
                )
                OrderRepository.create_order_item(order_item)

            # Create payment
            payment = Payment(
                order_id=order.id,
                amount=cart_result['total'],
                method=PaymentMethod[payment_method],
                status=PaymentStatus.PENDING
            )
            OrderRepository.create_payment(payment)

            # Create initial status history
            status_history = OrderStatusHistory(
                order_id=order.id,
                status='PENDING'
            )
            OrderRepository.create_status_history(status_history)

            # Commit all
            if OrderRepository.commit():
                return ServiceResult.ok(
                    data={'order_id': order.id},
                    message="Order placed successfully!"
                )
            else:
                return ServiceResult.fail("Database error during order creation")

        except Exception as e:
            return ServiceResult.fail(f"Error processing order: {str(e)}")

    # ============== ORDER MANAGEMENT ==============

    @staticmethod
    def get_user_orders(customer_id):
        """Get all orders for a user, organized by status"""
        orders = OrderRepository.get_by_customer(customer_id)

        active = [o for o in orders if o.status.value != 'Cancelled']
        cancelled = [o for o in orders if o.status.value == 'Cancelled']

        return ServiceResult.ok(data={
            'all': orders,
            'active': active,
            'cancelled': cancelled
        })

    @staticmethod
    def get_order_details(order_id, customer_id):
        """Get order with security check"""
        order = OrderRepository.get_by_id(order_id)
        if not order:
            return ServiceResult.fail("Order not found")

        if order.customer_id != customer_id:
            return ServiceResult.fail("Access denied", data={'forbidden': True})

        return ServiceResult.ok(data=order)

    @staticmethod
    def cancel_order(order_id, customer_id):
        """Cancel order if allowed"""
        result = OrderService.get_order_details(order_id, customer_id)
        if not result.success:
            return result

        order = result.data

        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            return ServiceResult.fail(
                "Cannot cancel this order - it is already being prepared or delivered"
            )

        try:
            OrderRepository.update_status(order, OrderStatus.CANCELLED)

            # Add status history
            history = OrderStatusHistory(
                order_id=order.id,
                status='CANCELLED'
            )
            OrderRepository.create_status_history(history)
            OrderRepository.commit()

            return ServiceResult.ok(message="Order cancelled successfully")

        except Exception as e:
            return ServiceResult.fail(f"Error cancelling order: {str(e)}")

    # ============== ORDER TRACKING ==============

    @staticmethod
    def get_tracking_info(order_id, customer_id):
        """Get order tracking with security check"""
        return OrderService.get_order_details(order_id, customer_id)

    @staticmethod
    def get_status_timeline(order):
        """Generate status timeline for tracking page"""
        status_order = ['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'DELIVERED']
        current_status = order.status.value
        current_index = status_order.index(current_status) if current_status in status_order else -1

        timeline = []
        for i, status in enumerate(status_order):
            timeline.append({
                'status': status,
                'label': status.replace('_', ' '),
                'state': 'completed' if i < current_index else ('active' if i == current_index else 'pending'),
                'description': {
                    'PENDING': 'Waiting for confirmation',
                    'CONFIRMED': 'Your order has been confirmed',
                    'PREPARING': 'Chef is preparing your meal',
                    'READY': 'Your order is ready for pickup/delivery',
                    'DELIVERED': 'Enjoy your meal!'
                }.get(status, '')
            })

        return ServiceResult.ok(data=timeline)