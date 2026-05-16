# app/services/order_service.py
"""Order business logic - checkout, creation, tracking, cancellation"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from app.repositories.order_repository import OrderRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.cart_repository import CartRepository
from app.models.orders import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.order_status_history import OrderStatusHistory
from app.services.base_service import BaseService, ServiceResult
from app.services.cart_service import CartService
from app.services.checkout_service import CheckoutService
from app.services.order_lifecycle_service import OrderLifecycleService
from app.services.voucher_service import VoucherService


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
    def create_order(
        customer_id,
        cart_data,
        delivery_address,
        special_instructions='',
        payment_method='CREDIT_CARD',
        promo_code=None,
        voucher_code=None,
        saved_card_id=None,
    ):
        """Create order from cart - full transaction"""
        pricing = CheckoutService.calculate_totals(
            cart_data, user_id=customer_id, promo_code=promo_code, voucher_code=voucher_code
        )
        if not pricing.success:
            return pricing

        totals = pricing.data
        cart_result = {'items': totals['items'], 'total': totals['subtotal']}

        try:
            for cart_item in cart_result['items']:
                menu_item = cart_item['menu_item']
                if cart_item['quantity'] > menu_item.available_stock:
                    return ServiceResult.fail(
                        f"{menu_item.name} is no longer available in requested quantity"
                    )

            order = Order(
                customer_id=customer_id,
                total_amount=totals['total'],
                subtotal=totals['subtotal'],
                discount_amount=totals['discount'],
                delivery_fee=totals['delivery_fee'],
                tax_amount=totals['tax'],
                promo_code=totals.get('applied_promo'),
                voucher_id=totals.get('voucher_id'),
                status=OrderStatus.CONFIRMED,
                delivery_address=delivery_address,
                special_instructions=special_instructions,
            )
            OrderRepository.create(order)

            for cart_item in cart_result['items']:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=cart_item['menu_item'].id,
                    quantity=cart_item['quantity'],
                    unit_price=cart_item['unit_price'],
                    special_requests=cart_item['special_requests'],
                )
                OrderRepository.create_order_item(order_item)

            payment = Payment(
                order_id=order.id,
                amount=totals['total'],
                method=PaymentMethod[payment_method],
                status=PaymentStatus.PENDING,
            )
            if saved_card_id and payment_method == 'CREDIT_CARD':
                from app.repositories.card_repository import CardRepository

                card = CardRepository.get_by_id(saved_card_id, customer_id)
                if card:
                    payment.card_last_four = card.last_four
            OrderRepository.create_payment(payment)

            if totals.get('voucher_id'):
                VoucherService.mark_used(totals['voucher_id'], customer_id)

            # Create initial status history — record CONFIRMED with a timestamp
            status_history = OrderStatusHistory(
                order_id=order.id,
                status='CONFIRMED',                    # ← was PENDING
                changed_at=datetime.utcnow(),
            )
            OrderRepository.create_status_history(status_history)

            # Commit all
            if OrderRepository.commit():
                OrderLifecycleService.on_status_change(order, OrderStatus.CONFIRMED)
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
                status='CANCELLED',
                changed_at=datetime.utcnow(),
            )
            OrderRepository.create_status_history(history)
            OrderRepository.commit()

            return ServiceResult.ok(message="Order cancelled successfully")

        except Exception as e:
            return ServiceResult.fail(f"Error cancelling order: {str(e)}")

    # ============== ORDER TRACKING ==============

    TRACKING_STAGES = (
        {
            'id': 'confirmation',
            'label': 'Confirmation',
            'description': 'Order received and confirmed',
            'status_key': 'CONFIRMED',
            'active_statuses': ('PENDING', 'CONFIRMED'),
        },
        {
            'id': 'preparation',
            'label': 'Preparation',
            'description': 'Chef is preparing your meal',
            'status_key': 'PREPARING',
            'active_statuses': ('PREPARING',),
        },
        {
            'id': 'shipping',
            'label': 'Shipping',
            'description': 'On the way to you',
            'status_key': 'READY',
            'active_statuses': ('READY', 'OUT_FOR_DELIVERY'),
        },
        {
            'id': 'delivery',
            'label': 'Delivery',
            'description': 'Enjoy your meal!',
            'status_key': 'DELIVERED',
            'active_statuses': ('DELIVERED',),
        },
    )

    STATUS_PROGRESS_INDEX = {
        'PENDING': 0,
        'CONFIRMED': 0,
        'PREPARING': 1,
        'READY': 2,
        'OUT_FOR_DELIVERY': 2,
        'DELIVERED': 3,
    }

    @staticmethod
    def get_tracking_info(order_id, customer_id):
        """Get order with enriched tracking timeline for the tracking page."""
        order = OrderRepository.get_by_id_with_relations(order_id)
        if not order:
            return ServiceResult.fail("Order not found")

        if order.customer_id != customer_id:
            return ServiceResult.fail("Access denied", data={'forbidden': True})

        tracking = OrderService.build_tracking_timeline(order)
        return ServiceResult.ok(data={'order': order, 'tracking': tracking})

    @staticmethod
    def _status_history_map(order):
        """Map backend status keys to first recorded timestamps."""
        history = {}
        for entry in sorted(order.status_history or [], key=lambda h: h.changed_at or datetime.min):
            key = (entry.status or '').upper()
            if key and key not in history:
                history[key] = entry.changed_at
        return history

    @staticmethod
    def _format_duration(seconds):
        if seconds is None or seconds < 0:
            return None
        seconds = int(seconds)
        if seconds < 60:
            return f'{seconds}s'
        minutes, secs = divmod(seconds, 60)
        if minutes < 60:
            return f'{minutes}m {secs}s' if secs else f'{minutes}m'
        hours, minutes = divmod(minutes, 60)
        return f'{hours}h {minutes}m'

    @staticmethod
    def build_tracking_timeline(order):
        """Build customer-facing stage timeline with timestamps and gap state."""
        now = datetime.utcnow()
        status_name = order.status.name
        progress_index = OrderService.STATUS_PROGRESS_INDEX.get(status_name, -1)
        waiting_for_preparation = status_name == 'CONFIRMED'
        cancelled = status_name == 'CANCELLED'

        history = OrderService._status_history_map(order)
        placed_at = order.created_at or now

        def stage_timestamp(stage):
            key = stage['status_key']
            if key in history:
                return history[key]
            if key == 'CONFIRMED':
                return history.get('PENDING') or placed_at
            return None

        stages = []
        for index, stage_def in enumerate(OrderService.TRACKING_STAGES):
            if cancelled:
                node_state = 'pending'
            elif progress_index > index:
                node_state = 'completed'
            elif progress_index == index and status_name in stage_def['active_statuses']:
                node_state = 'active'
            elif waiting_for_preparation and index == 0:
                node_state = 'completed'
            else:
                node_state = 'pending'

            started_at = stage_timestamp(stage_def)

            # ── FIX: active stage always gets a started_at so the JS timer works ──
            if node_state == 'active' and not started_at:
                started_at = placed_at

            if node_state == 'completed':
                next_def = OrderService.TRACKING_STAGES[index + 1] if index + 1 < len(OrderService.TRACKING_STAGES) else None
                ended_at = stage_timestamp(next_def) if next_def else (order.updated_at or now)
                if not ended_at and index == 0 and waiting_for_preparation:
                    ended_at = history.get('CONFIRMED') or order.updated_at
            elif node_state == 'active':
                ended_at = None
            else:
                ended_at = None

            if node_state == 'active' and started_at:
                duration_seconds = (now - started_at).total_seconds()
            elif node_state == 'completed' and started_at and ended_at:
                duration_seconds = (ended_at - started_at).total_seconds()
            else:
                duration_seconds = None

            stages.append({
                **stage_def,
                'state': node_state,
                'started_at': started_at,
                'ended_at': ended_at,
                'duration': OrderService._format_duration(duration_seconds),
                'duration_seconds': int(duration_seconds) if duration_seconds is not None else None,
            })

        connectors = []
        for index in range(len(stages) - 1):
            if cancelled:
                connector_state = 'pending'
            elif progress_index > index:
                connector_state = 'completed'
            elif waiting_for_preparation and index == 0:
                connector_state = 'gap_active'
            elif progress_index == index and status_name in OrderService.TRACKING_STAGES[index]['active_statuses']:
                connector_state = 'pending'
            else:
                connector_state = 'pending'

            gap_started_at = None
            if connector_state == 'gap_active':
                gap_started_at = history.get('CONFIRMED') or order.updated_at or placed_at

            connectors.append({
                'after_stage': stages[index]['id'],
                'state': connector_state,
                'started_at': gap_started_at,
                'label': 'Confirmed — waiting for preparation' if connector_state == 'gap_active' else '',
            })

        return {
            'stages': stages,
            'connectors': connectors,
            'current_status': order.status.value,
            'waiting_for_preparation': waiting_for_preparation,
            'cancelled': cancelled,
            'placed_at': placed_at,
            'gap_started_at': history.get('CONFIRMED') or order.updated_at if waiting_for_preparation else None,
        }

    @staticmethod
    def get_status_timeline(order):
        """Generate status timeline for tracking page (legacy helper)."""
        tracking = OrderService.build_tracking_timeline(order)
        return ServiceResult.ok(data=tracking['stages'])

    # ============== DEMO MODE (professor presentation only) ==============

    DEMO_FLOW = (
        OrderStatus.CONFIRMED,
        OrderStatus.PREPARING,
        OrderStatus.READY,
        OrderStatus.DELIVERED,
    )

    @staticmethod
    def _apply_demo_status(order, status):
        OrderRepository.update_status(order, status)
        OrderRepository.create_status_history(
            OrderStatusHistory(
                order_id=order.id,
                status=status.name,
                changed_at=datetime.utcnow(),
            )
        )
        committed = OrderRepository.commit()
        if committed:
            OrderLifecycleService.on_status_change(order, status)
        return committed

    @staticmethod
    def demo_start(order_id, customer_id):
        """Reset order to CONFIRMED for timeline demo (blue gap visible)."""
        result = OrderService.get_order_details(order_id, customer_id)
        if not result.success:
            return result
        order = result.data
        if not OrderService._apply_demo_status(order, OrderStatus.CONFIRMED):
            return ServiceResult.fail("Could not start demo")
        return ServiceResult.ok(data={'status': 'CONFIRMED'})

    DEMO_NEXT = {
        'CONFIRMED': OrderStatus.PREPARING,
        'PREPARING': OrderStatus.READY,
        'READY': OrderStatus.OUT_FOR_DELIVERY,
        'OUT_FOR_DELIVERY': OrderStatus.DELIVERED,
    }

    @staticmethod
    def _status_key(order):
        """Normalize order.status to enum name (CONFIRMED, PREPARING, …)."""
        status = order.status
        if isinstance(status, OrderStatus):
            return status.name
        raw = str(status).strip().upper()
        for member in OrderStatus:
            if raw == member.name or raw == member.value.upper():
                return member.name
        return raw

    @staticmethod
    def demo_advance(order_id, customer_id):
        """Advance one step: CONFIRMED → PREPARING → READY → DELIVERED."""
        result = OrderService.get_order_details(order_id, customer_id)
        if not result.success:
            return result

        order = result.data
        current_key = OrderService._status_key(order)

        if current_key == 'DELIVERED':
            return ServiceResult.ok(data={'done': True, 'status': 'DELIVERED'})

        next_status = OrderService.DEMO_NEXT.get(current_key)
        if next_status is None:
            logger.warning("[Demo] cannot advance from %s (order %s)", current_key, order_id)
            return ServiceResult.fail(f"Cannot advance from status: {current_key}")

        logger.info("[Demo] order %s: %s -> %s", order_id, current_key, next_status.name)
        if not OrderService._apply_demo_status(order, next_status):
            return ServiceResult.fail("Could not advance demo")

        return ServiceResult.ok(data={
            'done': next_status == OrderStatus.DELIVERED,
            'status': next_status.name,
        })