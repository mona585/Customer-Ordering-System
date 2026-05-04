from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required, current_user
from app.extensions import db
from datetime import datetime

from app.models.review import Review

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/menu')
def menu():
    """Display menu with all categories"""
    from app.models.menu_item import MenuItem, Category

    category = request.args.get('category', 'all')

    # Fetch all available items first - more reliable than query-level enum filtering
    all_items = MenuItem.query.filter_by(is_available=True).all()

    # Filter by category in Python if needed
    if category != 'all':
        try:
            cat_enum = Category[category.upper()]
            items = [item for item in all_items if item.category == cat_enum]
        except (ValueError, KeyError):
            items = all_items
            category = 'all'
    else:
        items = all_items

    categories = {
        'Appetizers': [],
        'Main Course': [],
        'Desserts': [],
        'Beverages': [],
        'Sides': []
    }

    for item in items:
        categories[item.category.value].append(item)

    return render_template('products/home.html', 
                         categories=categories,
                         active_category=category)


@customer_bp.route('/search')
def search():
    """Advanced search in name, description, and ingredients"""
    from app.models.menu_item import MenuItem

    query = request.args.get('q', '').strip()

    if query:
        search_term = f'%{query}%'
        items = MenuItem.query.filter(
            db.or_(
                MenuItem.name.ilike(search_term),
                MenuItem.description.ilike(search_term),
                MenuItem.ingredients.ilike(search_term)
            ),
            MenuItem.is_available == True
        ).all()
    else:
        items = []

    categories = {}
    for item in items:
        cat_name = item.category.value
        if cat_name not in categories:
            categories[cat_name] = []
        categories[cat_name].append(item)

    return render_template('products/home.html', 
                         categories=categories,
                         active_category='all',
                         search_query=query)




@customer_bp.route('/cart')
@login_required
def cart():
    """Display shopping cart"""
    from app.models.menu_item import MenuItem

    cart_data = session.get('cart', {})

    cart_items = []
    cart_total = 0
    stock_errors = []

    for item_id, item_data in cart_data.items():
        menu_item = MenuItem.query.get(int(item_id))
        if menu_item:
            quantity = item_data.get('quantity', 1)
            available = menu_item.available_stock

            if quantity > available + quantity:
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

    if stock_errors:
        for error in stock_errors:
            flash(error, 'warning')

    return render_template('cart/cart.html', 
                         cart_items=cart_items,
                         cart_total=cart_total)


@customer_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Add item to cart with stock check"""
    from app.models.menu_item import MenuItem

    item_id = request.form.get('item_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    special_requests = request.form.get('special_requests', '')

    if not item_id:
        flash('Invalid item', 'danger')
        return redirect(url_for('customer.menu'))

    menu_item = MenuItem.query.get(item_id)
    if not menu_item:
        flash('Item not found', 'danger')
        return redirect(url_for('customer.menu'))

    available = menu_item.available_stock

    cart = session.get('cart', {})
    current_qty = cart.get(str(item_id), {}).get('quantity', 0)
    total_requested = current_qty + quantity

    if total_requested > available:
        flash(f'Sorry, only {available} of {menu_item.name} available. You have {current_qty} in cart.', 'warning')
        return redirect(request.referrer or url_for('customer.menu'))

    if 'cart' not in session:
        session['cart'] = {}

    if str(item_id) in cart:
        cart[str(item_id)]['quantity'] += quantity
        if special_requests:
            cart[str(item_id)]['special_requests'] = special_requests
    else:
        cart[str(item_id)] = {
            'quantity': quantity,
            'special_requests': special_requests
        }

    session['cart'] = cart
    session.modified = True

    flash(f'{menu_item.name} added to cart!', 'success')

    next_page = request.args.get('next') or request.referrer
    if next_page and 'product' in next_page:
        return redirect(next_page)
    return redirect(url_for('customer.menu'))


@customer_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    """Update cart item quantity with stock check"""
    from app.models.menu_item import MenuItem

    quantity = request.form.get('quantity', 0, type=int)

    menu_item = MenuItem.query.get(item_id)
    if not menu_item:
        flash('Item not found', 'danger')
        return redirect(url_for('customer.cart'))

    if 'cart' in session:
        cart = session['cart']
        str_id = str(item_id)

        if str_id in cart:
            available = menu_item.available_stock

            if quantity > cart[str_id]['quantity']:
                extra_needed = quantity - cart[str_id]['quantity']
                if extra_needed > available:
                    flash(f'Only {available + cart[str_id]["quantity"]} total available', 'warning')
                    return redirect(url_for('customer.cart'))

            if quantity <= 0:
                del cart[str_id]
                flash('Item removed from cart', 'info')
            else:
                cart[str_id]['quantity'] = quantity
                flash('Cart updated', 'success')

            session['cart'] = cart
            session.modified = True

    return redirect(url_for('customer.cart'))


@customer_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """Remove item from cart - release stock"""
    if 'cart' in session:
        cart = session['cart']
        str_id = str(item_id)

        if str_id in cart:
            del cart[str_id]
            session['cart'] = cart
            session.modified = True
            flash('Item removed from cart', 'info')

    return redirect(url_for('customer.cart'))


@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page with stock validation"""
    from app.models.order import Order, OrderStatus
    from app.models.order_item import OrderItem
    from app.models.payment import Payment, PaymentMethod, PaymentStatus
    from app.models.menu_item import MenuItem

    cart_data = session.get('cart', {})

    if not cart_data:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('customer.menu'))

    cart_items = []
    cart_total = 0
    stock_errors = []

    for item_id, item_data in cart_data.items():
        menu_item = MenuItem.query.get(int(item_id))
        if menu_item:
            quantity = item_data.get('quantity', 1)
            available = menu_item.available_stock

            if quantity > available:
                stock_errors.append(f"{menu_item.name}: Only {available} available (you have {quantity})")
                continue

            unit_price = float(menu_item.price)
            subtotal = unit_price * quantity
            cart_total += subtotal

            cart_items.append({
                'menu_item': menu_item,
                'quantity': quantity,
                'unit_price': unit_price,
                'subtotal': subtotal,
                'special_requests': item_data.get('special_requests', '')
            })

    if stock_errors:
        for error in stock_errors:
            flash(error, 'danger')
        return redirect(url_for('customer.cart'))

    if request.method == 'POST':
        address = request.form.get('address', '')
        special_instructions = request.form.get('special_instructions', '')
        payment_method = request.form.get('payment_method', 'credit_card')

        try:
            for cart_item in cart_items:
                menu_item = cart_item['menu_item']
                if cart_item['quantity'] > menu_item.available_stock:
                    raise ValueError(f"{menu_item.name} is no longer available in requested quantity")

            order = Order(
                customer_id=current_user.id,
                total_amount=cart_total,
                status=OrderStatus.PENDING,
                delivery_address=address,
                special_instructions=special_instructions
            )
            db.session.add(order)
            db.session.flush()

            for cart_item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=cart_item['menu_item'].id,
                    quantity=cart_item['quantity'],
                    unit_price=cart_item['unit_price'],
                    special_requests=cart_item['special_requests']
                )
                db.session.add(order_item)

            payment = Payment(
                order_id=order.id,
                amount=cart_total,
                method=PaymentMethod(payment_method.upper().replace('_', ' ')),
                status=PaymentStatus.PENDING
            )
            db.session.add(payment)

            db.session.commit()

            session.pop('cart', None)
            session.modified = True

            flash('Order placed successfully!', 'success')
            return redirect(url_for('customer.order_tracking', order_id=order.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error processing order: {str(e)}', 'danger')
            return redirect(url_for('customer.checkout'))

    return render_template('cart/checkout.html',
                         cart_items=cart_items,
                         cart_total=cart_total)


@customer_bp.route('/orders')
@login_required
def orders():
    """Display order history"""
    from app.models.order import Order

    user_orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.created_at.desc()).all()

    return render_template('orders/order_tracking.html', orders=user_orders)


@customer_bp.route('/product/<int:id>')
def product_details(id):
    """Display product details page"""
    from app.models.menu_item import MenuItem

    item = MenuItem.query.get_or_404(id)

    related = MenuItem.query.filter_by(
        category=item.category,
        is_available=True
    ).filter(MenuItem.id != id).limit(4).all()

    reviews = item.reviews.order_by(Review.created_at.desc()).all() if hasattr(item.reviews, 'order_by') else item.reviews

    return render_template('products/product_details.html',
                         item=item,
                         related=related,
                         reviews=reviews)

@customer_bp.route('/order/cancel/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancel order and release stock"""
    from app.models.order import Order, OrderStatus

    order = Order.query.filter_by(id=order_id, customer_id=current_user.id).first_or_404()

    if order.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        order.status = OrderStatus.CANCELLED
        db.session.commit()
        flash('Order cancelled successfully', 'success')
    else:
        flash('Cannot cancel this order', 'warning')

    return redirect(url_for('customer.orders'))

@customer_bp.route('/product/<int:item_id>/review', methods=['POST'])
@login_required
def add_review(item_id):
    """Add a review for a product"""
    from app.models.menu_item import MenuItem
    from app.models.review import Review

    menu_item = MenuItem.query.get_or_404(item_id)

    existing = Review.query.filter_by(
        menu_item_id=item_id,
        customer_id=current_user.id
    ).first()

    if existing:
        flash('You already reviewed this item!', 'warning')
        return redirect(url_for('customer.product_details', id=item_id))

    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()

    if not rating or rating < 1 or rating > 5:
        flash('Please select a rating (1-5 stars)', 'danger')
        return redirect(url_for('customer.product_details', id=item_id))

    review = Review(
        menu_item_id=item_id,
        customer_id=current_user.id,
        rating=rating,
        comment=comment
    )

    db.session.add(review)
    db.session.commit()

    flash('Review added successfully!', 'success')
    return redirect(url_for('customer.product_details', id=item_id))
