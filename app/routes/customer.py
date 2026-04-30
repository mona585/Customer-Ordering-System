
# Recreate the fixed customer.py from scratch (clean version)


from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required, current_user
from app.extensions import db
from datetime import datetime

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/menu')
def menu():
    """Display menu with all categories"""
    from app.models.menu_item import MenuItem, Category
    
    # Get filter from query string
    category = request.args.get('category', 'all')
    
    if category != 'all':
        try:
            cat_enum = Category(category.upper().replace('_', ' '))
            items = MenuItem.query.filter_by(
                category=cat_enum,
                is_available=True
            ).all()
        except ValueError:
            items = MenuItem.query.filter_by(is_available=True).all()
            category = 'all'
    else:
        items = MenuItem.query.filter_by(is_available=True).all()
    
    # Group by category for display
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


@customer_bp.route('/product/<int:id>')
def product_details(id):
    """Display product details page"""
    from app.models.menu_item import MenuItem
    
    item = MenuItem.query.get_or_404(id)
    
    # Get related items (same category)
    related = MenuItem.query.filter_by(
        category=item.category,
        is_available=True
    ).filter(MenuItem.id != id).limit(4).all()
    
    return render_template('products/product_details.html',
                         item=item,
                         related=related)


@customer_bp.route('/cart')
@login_required
def cart():
    """Display shopping cart"""
    # Get cart from session or create empty
    cart_data = session.get('cart', {})
    
    cart_items = []
    cart_total = 0
    
    if cart_data:
        from app.models.menu_item import MenuItem
        for item_id, item_data in cart_data.items():
            menu_item = MenuItem.query.get(int(item_id))
            if menu_item:
                quantity = item_data.get('quantity', 1)
                unit_price = float(menu_item.price)
                subtotal = unit_price * quantity
                cart_total += subtotal
                
                cart_items.append({
                    'id': f"temp_{item_id}",  # Temporary ID for cart display
                    'menu_item': menu_item,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'subtotal': subtotal,
                    'special_requests': item_data.get('special_requests', '')
                })
    
    return render_template('cart/cart.html', 
                         cart_items=cart_items,
                         cart_total=cart_total)


@customer_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Add item to cart"""
    item_id = request.form.get('item_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    special_requests = request.form.get('special_requests', '')
    
    if not item_id:
        flash('Invalid item', 'danger')
        return redirect(url_for('customer.menu'))
    
    # Initialize cart in session if not exists
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    
    # Add or update item
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
    
    flash('Item added to cart!', 'success')
    
    # Redirect back to referring page or menu
    next_page = request.args.get('next') or request.referrer
    if next_page and 'product' in next_page:
        return redirect(next_page)
    return redirect(url_for('customer.menu'))


@customer_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    """Update cart item quantity"""
    quantity = request.form.get('quantity', 0, type=int)
    
    if 'cart' in session:
        cart = session['cart']
        str_id = str(item_id)
        
        if str_id in cart:
            if quantity <= 0:
                del cart[str_id]
            else:
                cart[str_id]['quantity'] = quantity
            
            session['cart'] = cart
            session.modified = True
            flash('Cart updated', 'success')
    
    return redirect(url_for('customer.cart'))


@customer_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """Remove item from cart"""
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
    """Checkout page"""
    from app.models.order import Order, OrderStatus
    from app.models.order_item import OrderItem
    from app.models.payment import Payment, PaymentMethod, PaymentStatus
    
    # Get cart items
    cart_data = session.get('cart', {})
    
    if not cart_data:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('customer.menu'))
    
    from app.models.menu_item import MenuItem
    
    cart_items = []
    cart_total = 0
    
    for item_id, item_data in cart_data.items():
        menu_item = MenuItem.query.get(int(item_id))
        if menu_item:
            quantity = item_data.get('quantity', 1)
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
    
    if request.method == 'POST':
        # Create order
        address = request.form.get('address', '')
        special_instructions = request.form.get('special_instructions', '')
        payment_method = request.form.get('payment_method', 'credit_card')
        
        try:
            # Create order
            order = Order(
                customer_id=current_user.id,
                total_amount=cart_total,
                status=OrderStatus.PENDING,
                delivery_address=address,
                special_instructions=special_instructions
            )
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Create order items
            for cart_item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=cart_item['menu_item'].id,
                    quantity=cart_item['quantity'],
                    unit_price=cart_item['unit_price'],
                    special_requests=cart_item['special_requests']
                )
                db.session.add(order_item)
            
            # Create payment
            payment = Payment(
                order_id=order.id,
                amount=cart_total,
                method=PaymentMethod(payment_method.upper().replace('_', ' ')),
                status=PaymentStatus.PENDING
            )
            db.session.add(payment)
            
            db.session.commit()
            
            # Clear cart
            session.pop('cart', None)
            session.modified = True
            
            flash('Order placed successfully!', 'success')
            return redirect(url_for('customer.order_tracking', order_id=order.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error processing order. Please try again.', 'danger')
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


@customer_bp.route('/order/<int:order_id>')
@login_required
def order_tracking(order_id):
    """Display single order tracking"""
    from app.models.order import Order
    
    order = Order.query.filter_by(id=order_id, customer_id=current_user.id).first_or_404()
    
    return render_template('orders/order_tracking.html', order=order)

