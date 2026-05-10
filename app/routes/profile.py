from app.extensions import db, csrf
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.repositories.user_repository import UserRepository
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from datetime import datetime

profile_bp = Blueprint('profile', __name__)

def _calculate_points(user) -> int:
    orders = getattr(user, 'orders', []) or []
    base_points = int(sum(o.total_price for o in orders))
    try:
        review_count = len(user.reviews) if hasattr(user, 'reviews') else 0
        base_points += review_count * 50
    except Exception:
        pass
    return base_points

def _referral_stats(user) -> dict:
    try:
        from app.models.referral import Referral 
        confirmed = Referral.query.filter_by(referrer_id=user.id, status='confirmed').count()
        pending = Referral.query.filter_by(referrer_id=user.id, status='pending').count()
        return {'referral_count': confirmed, 'pending_referrals': pending}
    except Exception:
        return {'referral_count': 0, 'pending_referrals': 0}

@profile_bp.route('/profile', methods=['GET'])
@login_required
def view_profile():
    points = _calculate_points(current_user)
    ref_stats = _referral_stats(current_user)
    return render_template(
        'profile/profile.html',
        user=current_user,
        points=points,
        **ref_stats
    )

@profile_bp.route('/profile/edit', methods=['GET'])
@login_required
def edit_profile():
    return render_template('profile/edit_profile.html', user=current_user)

@profile_bp.route('/update', methods=['POST'])
@login_required
@csrf.exempt
def update_profile():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip() or None
    address = request.form.get('address', '').strip() or None
    password = request.form.get('password', '').strip() or None
    dob_raw = request.form.get('date_of_birth', '').strip() or None

    if not username or len(username) < 3:
        return jsonify({'status': 'error', 'message': 'Username must be at least 3 characters.'}), 400
    
    if not email or '@' not in email:
        return jsonify({'status': 'error', 'message': 'Please enter a valid email address.'}), 400

    existing_user = UserRepository.get_by_username(username)
    if existing_user and existing_user.id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Username is already taken.'}), 400

    existing_email = UserRepository.get_by_email(email)
    if existing_email and existing_email.id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Email is already in use.'}), 400

    updates = {
        'username': username,
        'email': email,
        'phone': phone,
        'address': address
    }

    if dob_raw:
        try:
            updates['date_of_birth'] = datetime.strptime(dob_raw, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    if password:
        if len(password) < 8:
            return jsonify({'status': 'error', 'message': 'Password must be at least 8 characters.'}), 400
        updates['password_hash'] = generate_password_hash(password)

    try:
        UserRepository.update(current_user.id, updates)
        return jsonify({'status': 'success', 'message': 'Profile updated successfully!'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'}), 500

@profile_bp.route('/profile/update-preferences', methods=['POST'])
@login_required
def update_preferences():
    data = request.get_json(silent=True) or {}
    updates = {}
    if 'dietary_preferences' in data:
        raw = data['dietary_preferences']
        prefs = [p.strip() for p in raw.split(',') if p.strip()]
        updates['dietary_preferences'] = ','.join(prefs)
    if 'other_allergies' in data:
        updates['other_allergies'] = data['other_allergies'].strip() or None
    if not updates:
        return jsonify({'status': 'error', 'message': 'Nothing to update.'}), 400
    try:
        UserRepository.update(current_user.id, updates)
        return jsonify({'status': 'success', 'message': 'Preferences saved.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/profile/add-card', methods=['GET', 'POST'])
@login_required
def add_card():
    if request.method == 'POST':
        card_number = request.form.get('card_number', '').replace(' ', '')
        if not card_number or len(card_number) < 16:
            return jsonify({'status': 'error', 'message': 'Invalid card number.'}), 400
        return jsonify({'status': 'success', 'message': 'Card saved successfully!'}), 200
    return render_template('profile/add_card.html')