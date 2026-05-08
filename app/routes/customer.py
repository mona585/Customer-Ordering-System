# app/routes/customer.py
"""Customer routes - THIN controllers, all logic moved to services"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required, current_user
from app.services.menu_service import MenuService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.review_service import ReviewService
from app.services.wishlist_service import WishlistService
from app.extensions import csrf

customer_bp = Blueprint('customer', __name__)


# ==================== MENU ====================

@customer_bp.route('/menu')
def menu():
    """Display menu with all categories"""
    category = request.args.get('category', 'all')

    if category != 'all':
        result = MenuService.get_category_items(category)
        if not result.success:
            flash(result.error, 'warning')
            return redirect(url_for('customer.menu'))

        items = result.data
        categories = {}
        for item in items:
            cat_name = item.category.value
            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(item)
    else:
        result = MenuService.get_all_categories()
        categories = result.data

    # Get wishlist status for each item if user is logged in
    wishlist_ids = set()
    if current_user.is_authenticated:
        try:
            wishlist_result = WishlistService.get_user_wishlist(current_user.id)
            if wishlist_result.success:
                wishlist_ids = {entry['menu_item'].id for entry in wishlist_result.data}
        except Exception:
            pass

    return render_template('products/home.html',
                         categories=categories,
                         active_category=category,
                         wishlist_ids=wishlist_ids)


@customer_bp.route('/search')
def search():
    """Advanced search"""
    query = request.args.get('q', '').strip()

    result = MenuService.search_items(query)

    if not result.success:
        flash(result.error, 'info')
        return redirect(url_for('customer.menu'))

    # Get wishlist status for each item if user is logged in
    wishlist_ids = set()
    if current_user.is_authenticated:
        try:
            wishlist_result = WishlistService.get_user_wishlist(current_user.id)
            if wishlist_result.success:
                wishlist_ids = {entry['menu_item'].id for entry in wishlist_result.data}
        except Exception:
            pass

    return render_template('products/home.html',
                         categories=result.data,
                         active_category='all',
                         search_query=query,
                         wishlist_ids=wishlist_ids)


@customer_bp.route('/product/<int:id>')
def product_details(id):
    """Display product details page"""
    result = MenuService.get_product_details(id)

    if not result.success:
        flash(result.error, 'danger')
        return redirect(url_for('customer.menu'))

    data = result.data
    reviews_result = ReviewService.get_product_reviews(id)

    # Check if item is in user's wishlist
    is_wishlisted = False
    if current_user.is_authenticated:
        try:
            wishlist_result = WishlistService.is_in_wishlist(current_user.id, id)
            if wishlist_result.success:
                is_wishlisted = wishlist_result.data['is_wishlisted']
        except Exception:
            pass

    return render_template('products/product_details.html',
                         item=data['item'],
                         related=data['related'],
                         reviews=reviews_result.data['reviews'] if reviews_result.success else [],
                         is_wishlisted=is_wishlisted)


# ==================== CART ====================

@customer_bp.route('/cart')
@login_required
def cart():
    """Display shopping cart"""
    cart_data = session.get('cart', {})
    result = CartService.get_cart_items(cart_data)

    if result.data and result.data.get('errors'):
        for error in result.data['errors']:
            flash(error, 'warning')

    return render_template('cart/cart.html',
                         cart_items=result.data['items'],
                         cart_total=result.data['total'])


@customer_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Add item to cart"""
    item_id = request.form.get('item_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    special_requests = request.form.get('special_requests', '')

    cart_data = session.get('cart', {})
    result = CartService.add_to_cart(cart_data, item_id, quantity, special_requests)

    if result.success:
        session['cart'] = result.data['cart']
        session.modified = True
        flash(result.message, 'success')
    else:
        flash(result.error, 'warning')

    next_page = request.args.get('next') or request.referrer
    if next_page and 'product' in next_page:
        return redirect(next_page)
    return redirect(url_for('customer.menu'))


@customer_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    """Update cart item quantity"""
    quantity = request.form.get('quantity', 0, type=int)
    cart_data = dict(session.get('cart', {}))

    result = CartService.update_cart_item(cart_data, item_id, quantity)

    if result.success:
        session['cart'] = result.data['cart']
        session.modified = True
        flash(result.message, 'success' if not result.data.get('removed') else 'info')
    else:
        flash(result.error, 'warning')

    return redirect(url_for('customer.cart'))


@customer_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """Remove item from cart"""
    cart_data = dict(session.get('cart', {}))
    result = CartService.remove_from_cart(cart_data, item_id)

    if result.success:
        session['cart'] = result.data['cart']
        session.modified = True
        flash(result.message, 'info')
    else:
        flash(result.error, 'warning')

    return redirect(url_for('customer.cart'))


# ==================== WISHLIST ====================

@customer_bp.route('/wishlist')
@login_required
def wishlist():
    """Display user's wishlist"""
    try:
        print(f"[DEBUG] Loading wishlist for user_id={current_user.id}, username={current_user.username}")
        result = WishlistService.get_user_wishlist(current_user.id)
        print(f"[DEBUG] WishlistService result: success={result.success}, data_count={len(result.data) if result.data else 0}")

        if not result.success:
            flash(result.error, 'warning')
            return render_template('cart/wishlist.html', wishlist_items=[])

        return render_template('cart/wishlist.html', wishlist_items=result.data)
    except Exception as e:
        import traceback
        print(f"[DEBUG] WISHLIST ROUTE ERROR: {e}")
        traceback.print_exc()
        flash(f'Wishlist error: {str(e)}', 'danger')
        return render_template('cart/wishlist.html', wishlist_items=[])


@customer_bp.route('/wishlist/remove/<int:wishlist_id>', methods=['POST'])
@login_required
def remove_from_wishlist(wishlist_id):
    """Remove item from wishlist via form submission"""
    result = WishlistService.remove_from_wishlist(current_user.id, wishlist_id)

    if result.success:
        flash(result.message or 'Item removed from wishlist.', 'success')
    else:
        flash(result.error or 'Could not remove item.', 'warning')

    return redirect(url_for('customer.wishlist'))


@customer_bp.route('/api/wishlist/toggle/<int:item_id>', methods=['POST'])
@csrf.exempt
@login_required
def api_toggle_wishlist(item_id):
    """AJAX toggle wishlist item"""
    try:
        from app.repositories.wishlist_repository import WishlistRepository

        # Single direct query — no ambiguity about current state
        existing_entry = WishlistRepository.get_customer_item(current_user.id, item_id)

        if existing_entry:
            # Item IS in wishlist → remove it
            result = WishlistService.remove_from_wishlist(current_user.id, existing_entry.id)
            if result.success:
                return jsonify({'success': True, 'action': 'removed', 'message': result.message})
            return jsonify({'success': False, 'message': result.error}), 400
        else:
            # Item is NOT in wishlist → add it
            result = WishlistService.add_to_wishlist(current_user.id, item_id)
            if result.success:
                return jsonify({'success': True, 'action': 'added', 'message': result.message})
            return jsonify({'success': False, 'message': result.error}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== AJAX API ====================

@customer_bp.route('/api/cart/add', methods=['POST'])
@login_required
def api_add_to_cart():
    """Ajax add to cart"""
    if request.is_json:
        data = request.get_json()
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        special_requests = data.get('special_requests', '')
    else:
        data = request.form
        item_id = data.get('item_id', type=int)
        quantity = data.get('quantity', 1, type=int)
        special_requests = data.get('special_requests', '')

    if isinstance(item_id, str):
        item_id = int(item_id)
    if isinstance(quantity, str):
        quantity = int(quantity)

    cart_data = session.get('cart', {})
    result = CartService.add_to_cart(cart_data, item_id, quantity, special_requests)

    if result.success:
        session['cart'] = result.data['cart']
        session.modified = True
        return jsonify({
            'success': True,
            'message': result.message,
            'cart_count': result.data['cart_count'],
            'item_name': result.data['item_name'],
            'item_price': result.data['item_price']
        })

    return jsonify({'success': False, 'message': result.error}), 400


@customer_bp.route('/api/cart/count')
@login_required
def api_cart_count():
    """Get current cart count"""
    cart_data = session.get('cart', {})
    result = CartService.get_cart_count(cart_data)
    return jsonify(result.data)


@customer_bp.route('/api/product/<int:item_id>')
def api_product_details(item_id):
    """Get product details for quick view modal"""
    result = MenuService.get_product_for_api(item_id)

    if not result.success:
        return jsonify({'error': result.error}), 404

    return jsonify(result.data)


# ==================== CHECKOUT ====================

@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page with stock validation"""
    cart_data = session.get('cart', {})

    # Validate cart
    result = OrderService.prepare_checkout(cart_data)
    if not result.success:
        flash(result.error, 'warning')
        return redirect(url_for('customer.menu'))

    cart_result = result.data

    if request.method == 'POST':
        address = request.form.get('delivery_address', '')
        special_instructions = request.form.get('special_instructions', '')
        payment_method = request.form.get('payment_method', 'CREDIT_CARD')

        result = OrderService.create_order(
            customer_id=current_user.id,
            cart_data=cart_data,
            delivery_address=address,
            special_instructions=special_instructions,
            payment_method=payment_method
        )

        if result.success:
            session.pop('cart', None)
            session.modified = True
            flash(result.message, 'success')
            return redirect(url_for('order.order_tracking', order_id=result.data['order_id']))
        else:
            flash(result.error, 'danger')
            return redirect(url_for('customer.checkout'))

    return render_template('cart/checkout.html',
                         items=cart_result['items'],
                         total=cart_result['total'])


# ==================== ORDERS ====================

@customer_bp.route('/orders')
@login_required
def orders():
    """Display order history"""
    result = OrderService.get_user_orders(current_user.id)
    return render_template('orders/orders_list.html', orders=result.data['all'])


@customer_bp.route('/order/cancel/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancel order"""
    result = OrderService.cancel_order(order_id, current_user.id)

    if result.success:
        flash(result.message, 'success')
    else:
        flash(result.error, 'warning')

    return redirect(url_for('customer.orders'))


# ==================== REVIEWS ====================

@customer_bp.route('/product/<int:item_id>/review', methods=['POST'])
@login_required
def add_review(item_id):
    """Add a review for a product"""
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()

    result = ReviewService.add_review(
        item_id=item_id,
        customer_id=current_user.id,
        rating=rating,
        comment=comment
    )

    if result.success:
        flash(result.message, 'success')
    else:
        flash(result.error, 'warning' if 'already reviewed' in result.error else 'danger')

    return redirect(url_for('customer.product_details', id=item_id))