# app/auth/auth.py

from flask import Blueprint, render_template, request, url_for, jsonify, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
import re

auth_bp = Blueprint('auth', __name__)


def _is_ajax() -> bool:
    """True when the request was sent via fetch() with the AJAX header."""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _validate_phone(phone: str) -> str | None:
    """Validates international E.164 phone number format (e.g., +201012345678)"""
    if not phone:
        return None  # Phone is optional

    # Regex breakdown:
    # ^\+       -> Must start with a '+'
    # [1-9]\d{6,14}$ -> Followed by a non-zero digit, and 6 to 14 total numbers (Standard Int. limits)
    if not re.match(r'^\+[1-9]\d{6,14}$', phone):
        return 'Invalid phone number format. Please select a valid country code.'
    
    return None

def _validate_registration(username, email, password, phone='') -> str | None:
    if not username or not email or not password:
        return 'All fields are required.'
    if len(username) < 3:
        return 'Username must be at least 3 characters.'
    if '@' not in email or '.' not in email.split('@')[-1]:
        return 'Please enter a valid email address.'
    if len(password) < 8:
        return 'Password must be at least 8 characters.'
    # Phone is optional but validated if provided
    phone_error = _validate_phone(phone)
    if phone_error:
        return phone_error
    return None



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone    = request.form.get('phone', '').strip()
        address  = request.form.get('address', '').strip()

        # Pass phone into validation now
        error = _validate_registration(username, email, password, phone)
        if error:
            return jsonify({'status': 'error', 'message': error}), 400

        if UserRepository.get_by_email(email):
            return jsonify({'status': 'error', 'message': 'Email already registered.'}), 400
        if UserRepository.get_by_username(username):
            return jsonify({'status': 'error', 'message': 'Username is already taken.'}), 400
        # Only check uniqueness if a phone was actually provided
        if phone and UserRepository.get_by_phone(phone):
            return jsonify({'status': 'error', 'message': 'This phone number is already registered.'}), 400
        
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone or None,
            address=address or None,
        )
        UserRepository.create(new_user)

        return jsonify({
            'status':   'success',
            'message':  'Account created! Redirecting to sign in...',
            'redirect': url_for('auth.login'),
        }), 200

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Already logged in — no reason to show the login page
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Email and password are required.'}), 400

        user = UserRepository.get_by_email(email)

        # Single generic message — don't reveal whether the email exists
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({
                'status':  'error',
                'message': 'Invalid email or password.',
            }), 401

        login_user(user, remember=False)

        return jsonify({
            'status':   'success',
            'message':  'Welcome back! Entering AURA...',
            'redirect': url_for('main.home'),
        }), 200

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))