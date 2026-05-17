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


# ==================== CART (Updated with Promo Logic) ====================

@customer_bp.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    """Display shopping cart with Promo Code support"""
    cart_data = session.get('cart', {})
    result = CartService.get_cart_items(cart_data)

    if result.data and result.data.get('errors'):
        for error in result.data['errors']:
            flash(error, 'warning')

    cart_total = result.data['total']
    
    # استرجاع بيانات الخصم من السيشين لضمان استمراريته
    discount = session.get('promo_discount', 0)
    applied_code = session.get('applied_promo', "")
    promo_error = None

    # معالجة طلب البرومو كود عند الضغط على Apply
    if request.method == 'POST' and 'promo_code' in request.form:
        promo_code = request.form.get('promo_code', '')
        
        # استخدام الـ CartService للتحقق من الكود
        promo_result = CartService.apply_promo_code(cart_total, promo_code)
        
        if promo_result.success:
            discount = promo_result.data['discount']
            applied_code = promo_result.data['code']
            session['promo_discount'] = discount
            session['applied_promo'] = applied_code
            session['promo_code'] = applied_code
            flash(promo_result.message, 'success')
        else:
            promo_error = promo_result.error
            session.pop('promo_discount', None)
            session.pop('applied_promo', None)
            session.pop('promo_code', None)
            discount = 0
            applied_code = ""
    else:
        # Recalculate discount based on current cart_total in case it changed
        if applied_code and cart_total > 0:
            promo_result = CartService.apply_promo_code(cart_total, applied_code)
            if promo_result.success:
                discount = promo_result.data['discount']
                session['promo_discount'] = discount
            else:
                session.pop('promo_discount', None)
                session.pop('applied_promo', None)
                session.pop('promo_code', None)
                discount = 0
                applied_code = ""

    return render_template('cart/cart.html',
                         cart_items=result.data['items'],
                         cart_total=cart_total,
                         discount=discount,
                         applied_code=applied_code,
                         promo_error=promo_error)


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
        result = WishlistService.get_user_wishlist(current_user.id)
        if not result.success:
            flash(result.error, 'warning')
            return render_template('cart/wishlist.html', wishlist_items=[])

        return render_template('cart/wishlist.html', wishlist_items=result.data)
    except Exception as e:
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


# ==================== AJAX API ====================

@customer_bp.route('/api/wishlist/toggle/<int:item_id>', methods=['POST'])
@csrf.exempt
@login_required
def api_toggle_wishlist(item_id):
    """AJAX toggle wishlist item"""
    try:
        from app.repositories.wishlist_repository import WishlistRepository
        existing_entry = WishlistRepository.get_customer_item(current_user.id, item_id)

        if existing_entry:
            result = WishlistService.remove_from_wishlist(current_user.id, existing_entry.id)
            if result.success:
                return jsonify({'success': True, 'action': 'removed', 'message': result.message})
            return jsonify({'success': False, 'message': result.error}), 400
        else:
            result = WishlistService.add_to_wishlist(current_user.id, item_id)
            if result.success:
                return jsonify({'success': True, 'action': 'added', 'message': result.message})
            return jsonify({'success': False, 'message': result.error}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


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
def api_cart_count():
    if not current_user.is_authenticated:
        return jsonify({'count': 0})
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
    from app.services.address_service import AddressService
    from app.services.card_service import CardService
    from app.services.checkout_service import CheckoutService
    from app.services.voucher_service import VoucherService

    cart_data = session.get('cart', {})

    prefill_voucher = request.args.get('voucher') or session.pop('checkout_voucher', None)
    promo_code = (
        request.args.get('promo')
        or session.get('promo_code')
        or session.get('applied_promo')
    )

    pricing = CheckoutService.calculate_totals(
        cart_data,
        user_id=current_user.id,
        promo_code=promo_code,
        voucher_code=prefill_voucher,
    )
    if not pricing.success:
        flash(pricing.error, 'warning')
        return redirect(url_for('customer.menu'))

    totals = pricing.data

    if request.method == 'POST':
        address_id = request.form.get('address_id', type=int)
        address = (request.form.get('delivery_address') or '').strip()
        save_address = request.form.get('save_address') == '1'

        if address_id:
            from app.repositories.address_repository import AddressRepository
            addr = AddressRepository.get_by_id(address_id, current_user.id)
            if addr:
                address = addr.formatted()
        elif save_address and address:
            label = (request.form.get('new_address_label') or 'Home').strip()[:50] or 'Home'
            created = AddressService.create_address(
                current_user.id,
                label=label,
                street=address,
                set_default=False,
            )
            if created.success:
                address = created.data.get('formatted', address)
            else:
                flash(created.error, 'warning')
        phone = (request.form.get('phone') or '').strip()
        if phone:
            from app.extensions import db
            current_user.phone = phone
            db.session.commit()

        special_instructions = request.form.get('special_instructions', '')
        payment_method = request.form.get('payment_method', 'CREDIT_CARD')
        promo = request.form.get('promo_code', '').strip() or None
        voucher = request.form.get('voucher_code', '').strip() or None
        saved_card_id = request.form.get('saved_card_id', type=int)

        if payment_method == 'CREDIT_CARD':
            from app.services.card_service import CardService

            if not saved_card_id:
                new_number = request.form.get('new_card_number', '')
                new_expiry = request.form.get('new_card_expiry', '')
                new_cvv = request.form.get('new_card_cvv', '')
                new_name = request.form.get('new_card_name', '')
                if new_number and new_expiry and new_cvv:
                    add_result = CardService.add_card(
                        current_user.id,
                        new_number,
                        set_default=True,
                        expiry_raw=new_expiry,
                        cvv=new_cvv,
                        cardholder_name=new_name,
                    )
                    if not add_result.success:
                        flash(add_result.error, 'danger')
                        return redirect(url_for('customer.checkout'))
                    saved_card_id = add_result.data.get('id')
                else:
                    flash('Please select a saved card or enter new card details.', 'danger')
                    return redirect(url_for('customer.checkout'))
            else:
                card = CardService.get_card_for_user(current_user.id, saved_card_id)
                if not card:
                    flash('Selected payment card is invalid. Choose another card.', 'danger')
                    return redirect(url_for('customer.checkout'))

        result = OrderService.create_order(
            customer_id=current_user.id,
            cart_data=cart_data,
            delivery_address=address,
            special_instructions=special_instructions,
            payment_method=payment_method,
            promo_code=promo,
            voucher_code=voucher,
            saved_card_id=saved_card_id,
        )

        if result.success:
            session.pop('cart', None)
            session.pop('promo_code', None)
            session.pop('applied_promo', None)
            session.pop('promo_discount', None)
            session.pop('checkout_voucher', None)
            session.modified = True
            flash(result.message, 'success')
            return redirect(url_for('order.order_tracking', order_id=result.data['order_id']))
        flash(result.error, 'danger')
        return redirect(url_for('customer.checkout'))

    addresses = AddressService.list_addresses(current_user.id)
    cards = CardService.list_cards(current_user.id)
    vouchers = VoucherService.list_active(current_user.id)

    return render_template(
        'cart/checkout.html',
        items=totals['items'],
        total=totals['total'],
        subtotal=totals['subtotal'],
        discount=totals['discount'],
        delivery_fee=totals['delivery_fee'],
        tax=totals['tax'],
        addresses=addresses.data if addresses.success else [],
        saved_cards=cards.data if cards.success else [],
        vouchers=vouchers.data if vouchers.success else [],
        prefill_voucher=prefill_voucher,
        prefill_promo=promo_code,
    )


@customer_bp.route('/api/checkout/validate', methods=['POST'])
@login_required
@csrf.exempt
def api_checkout_validate():
    from app.services.checkout_service import CheckoutService

    cart_data = session.get('cart', {})
    data = request.get_json(silent=True) or {}
    result = CheckoutService.calculate_totals(
        cart_data,
        user_id=current_user.id,
        promo_code=data.get('promo_code'),
        voucher_code=data.get('voucher_code'),
    )
    if result.success:
        totals = {
            k: v
            for k, v in result.data.items()
            if k != 'items'
        }
        return jsonify({'status': 'success', 'totals': totals})
    return jsonify({'status': 'error', 'message': result.error}), 400


# ==================== ORDERS & REVIEWS ====================

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