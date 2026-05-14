# app/routes/auth.py

from flask import Blueprint, render_template, request, url_for, jsonify, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.constants.roles import ROLE_CUSTOMER
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.security.rbac import get_post_login_redirect
import re
import requests
import os

auth_bp = Blueprint('auth', __name__)

FIREBASE_API_KEY = os.environ.get('FIREBASE_WEB_API_KEY')


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
    signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
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
    verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
    requests.post(verify_url, json={
        "requestType": "VERIFY_EMAIL",
        "idToken": id_token
    })

    return id_token, firebase_uid, None


def _firebase_login(email, password):
    """Sign in with Firebase and return token + uid + verified status."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
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
    lookup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}"
    lookup_resp = requests.post(lookup_url, json={"idToken": id_token})
    lookup_data = lookup_resp.json()

    email_verified = False
    if 'users' in lookup_data and len(lookup_data['users']) > 0:
        email_verified = lookup_data['users'][0].get('emailVerified', False)

    return id_token, firebase_uid, email_verified, None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(get_post_login_redirect(current_user))

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
        if not FIREBASE_API_KEY:
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

        RoleRepository.attach_role_to_user(new_user, ROLE_CUSTOMER)

        return jsonify({
            'status':   'success',
            'message':  'Account created! Please check your email to verify your account before logging in.',
            'redirect': url_for('auth.login'),
        }), 200

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(get_post_login_redirect(current_user))

    if request.method == 'POST':
        identifier = (request.form.get('identifier') or request.form.get('email', '')).strip()
        password = request.form.get('password', '')

        if not identifier or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email or username and password are required.',
            }), 400

        user = UserRepository.get_by_login_identifier(identifier)

        if not user or not user.is_active:
            return jsonify({'status': 'error', 'message': 'Invalid credentials.'}), 401

        # ----- Staff (admin / delivery / chef): Flask + password_hash only -----
        if user.uses_staff_authentication():
            if not user.password_hash or not check_password_hash(user.password_hash, password):
                return jsonify({'status': 'error', 'message': 'Invalid credentials.'}), 401

            login_user(user, remember=False)

            return jsonify({
                'status': 'success',
                'message': 'Welcome back!',
                'redirect': get_post_login_redirect(user),
            }), 200

        # ----- Customer: Firebase unchanged (uses account email) -----
        if not FIREBASE_API_KEY:
            return jsonify({'status': 'error', 'message': 'Firebase not configured.'}), 500

        _, firebase_uid, email_verified, firebase_error = _firebase_login(user.email, password)

        if firebase_error:
            return jsonify({'status': 'error', 'message': 'Invalid credentials.'}), 401

        if not email_verified:
            return jsonify({
                'status': 'error',
                'message': 'Please verify your email before logging in. Check your inbox.',
            }), 401

        if user.firebase_uid and firebase_uid != user.firebase_uid:
            return jsonify({'status': 'error', 'message': 'Invalid credentials.'}), 401

        login_user(user, remember=False)

        return jsonify({
            'status': 'success',
            'message': 'Welcome back! Entering AURA...',
            'redirect': get_post_login_redirect(user),
        }), 200

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))