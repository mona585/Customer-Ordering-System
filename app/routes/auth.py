# app/routes/auth.py

from flask import Blueprint, current_app, render_template, request, url_for, jsonify, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
import re
import requests
import os

auth_bp = Blueprint('auth', __name__)


def _firebase_api_key() -> str | None:
    """Read API key at request time so .env / app config is always applied."""
    return current_app.config.get('FIREBASE_WEB_API_KEY') or os.environ.get('FIREBASE_WEB_API_KEY')


def _validate_phone(phone: str) -> str | None:
    if not phone:
        return None
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
    phone_error = _validate_phone(phone)
    if phone_error:
        return phone_error
    return None


def _firebase_register(email, password):
    """Create user in Firebase and send verification email."""
    # Step 1: Create user in Firebase
    api_key = _firebase_api_key()
    if not api_key:
        return None, None, 'Firebase not configured.'
    signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    resp = requests.post(signup_url, json={
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    data = resp.json()

    if 'error' in data:
        msg = data['error'].get('message', 'Registration failed.')
        # Make Firebase error messages user-friendly
        if msg == 'EMAIL_EXISTS':
            return None, None, 'Email already registered.'
        if msg == 'WEAK_PASSWORD : Password should be at least 6 characters':
            return None, None, 'Password must be at least 8 characters.'
        return None, None, msg

    id_token = data['idToken']
    firebase_uid = data['localId']

    # Step 2: Send verification email
    verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
    requests.post(verify_url, json={
        "requestType": "VERIFY_EMAIL",
        "idToken": id_token
    })

    return id_token, firebase_uid, None


def _firebase_login(email, password):
    """Sign in with Firebase and return token + uid + verified status."""
    api_key = _firebase_api_key()
    if not api_key:
        return None, None, False, 'Firebase not configured.'
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    resp = requests.post(url, json={
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    data = resp.json()

    if 'error' in data:
        return None, None, False, 'Invalid email or password.'

    id_token = data['idToken']
    firebase_uid = data['localId']

    # Check if email is verified
    lookup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
    lookup_resp = requests.post(lookup_url, json={"idToken": id_token})
    lookup_data = lookup_resp.json()

    email_verified = False
    if 'users' in lookup_data and len(lookup_data['users']) > 0:
        email_verified = lookup_data['users'][0].get('emailVerified', False)

    return id_token, firebase_uid, email_verified, None


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

        # Validate inputs
        error = _validate_registration(username, email, password, phone)
        if error:
            return jsonify({'status': 'error', 'message': error}), 400

        # Check username uniqueness in SQLite
        if UserRepository.get_by_username(username):
            return jsonify({'status': 'error', 'message': 'Username is already taken.'}), 400

        # Check email uniqueness in SQLite
        if UserRepository.get_by_email(email):
            return jsonify({'status': 'error', 'message': 'Email already registered.'}), 400

        if phone and UserRepository.get_by_phone(phone):
             return jsonify({'status': 'error', 'message': 'This phone number is already registered.'}), 400

        # Register in Firebase + send verification email
        if not _firebase_api_key():
            return jsonify({'status': 'error', 'message': 'Firebase not configured.'}), 500

        _, firebase_uid, firebase_error = _firebase_register(email, password)
        if firebase_error:
            return jsonify({'status': 'error', 'message': firebase_error}), 400

        # Save user in SQLite (unverified for now — no login yet)
        new_user = User(
            username=username,
            email=email,
            firebase_uid=firebase_uid,
            password_hash=generate_password_hash(password),
            phone=phone or None,
            address=address or None,
        )
        UserRepository.create(new_user)

        return jsonify({
            'status':   'success',
            'message':  'Account created! Please check your email to verify your account before logging in.',
            'redirect': url_for('auth.login'),
        }), 200

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Email and password are required.'}), 400

        user = UserRepository.get_by_login_identifier(identifier)

        # Treat NULL is_active as active (legacy rows before column backfill).
        if not user or user.is_active is False:
            return jsonify({'status': 'error', 'message': 'Invalid credentials.'}), 401

        # ----- Staff (admin / delivery / chef): Flask + password_hash only -----
        # Also treat local-only accounts (no Firebase UID) with a staff role as staff.
        if user.uses_staff_authentication() or (
            user.firebase_uid is None
            and user.password_hash
            and any(user.has_role(s) for s in ("admin", "delivery", "chef"))
        ):
            if not user.password_hash or not check_password_hash(user.password_hash, password):
                return jsonify({'status': 'error', 'message': 'Invalid credentials.'}), 401

            login_user(user, remember=False)

            return jsonify({
                'status': 'success',
                'message': 'Welcome back!',
                'redirect': get_post_login_redirect(user),
            }), 200

        # ----- Customer: Firebase (or local hash if no Firebase UID on file) -----
        if user.firebase_uid is None and user.password_hash:
            if check_password_hash(user.password_hash, password):
                login_user(user, remember=False)
                return jsonify({
                    'status': 'success',
                    'message': 'Welcome back! Entering AURA...',
                    'redirect': get_post_login_redirect(user),
                }), 200
            return jsonify({'status': 'error', 'message': 'Invalid credentials.'}), 401

        if not _firebase_api_key():
            return jsonify({'status': 'error', 'message': 'Firebase not configured.'}), 500

        # Verify with Firebase
        _, firebase_uid, email_verified, firebase_error = _firebase_login(email, password)

        if firebase_error:
            return jsonify({'status': 'error', 'message': firebase_error}), 401

        # Block login if email not verified
        if not email_verified:
            return jsonify({
                'status':  'error',
                'message': 'Please verify your email before logging in. Check your inbox.',
            }), 401

        # Get user from SQLite
        user = UserRepository.get_by_email(email)
        if not user:
            return jsonify({'status': 'error', 'message': 'Account not found.'}), 404

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