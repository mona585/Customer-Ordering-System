# app/routes/auth.py

from flask import Blueprint, current_app, render_template, request, url_for, jsonify, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.constants.roles import ROLE_CUSTOMER
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.security.rbac import get_post_login_redirect
from app.security.password_policy import password_requirements_hint, validate_password_strength
import re
import requests
import os
import urllib3

# Demo only: suppress InsecureRequestWarning when verify=False (Windows Store Python SSL).
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

auth_bp = Blueprint('auth', __name__)


def _firebase_api_key() -> str | None:
    return current_app.config.get('FIREBASE_WEB_API_KEY') or os.environ.get('FIREBASE_WEB_API_KEY')


def _validate_phone(phone: str) -> str | None:
    if not phone:
        return None
    if not re.match(r'^\+[1-9]\d{6,14}$', phone):
        return 'Invalid phone number format. Please select a valid country code.'
    return None


def _validate_registration(
    username,
    email,
    password,
    phone='',
    password_confirm='',
) -> str | None:
    if not username or not email or not password:
        return 'All fields are required.'
    if len(username) < 3:
        return 'Username must be at least 3 characters.'
    if '@' not in email or '.' not in email.split('@')[-1]:
        return 'Please enter a valid email address.'
    pwd_error = validate_password_strength(password, username=username, email=email)
    if pwd_error:
        return pwd_error
    if password != (password_confirm or ''):
        return 'Passwords do not match.'
    phone_error = _validate_phone(phone)
    if phone_error:
        return phone_error
    return None


def _firebase_register(email, password):
    """Create user in Firebase and send verification email."""
    api_key = _firebase_api_key()
    if not api_key:
        return None, None, 'Firebase not configured.'
    signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    verify_ssl = False  # Windows Store Python SSL; see _firebase_login
    try:
        resp = requests.post(
            signup_url,
            json={
                "email": email,
                "password": password,
                "returnSecureToken": True,
            },
            verify=verify_ssl,
            timeout=30,
        )
        data = resp.json()
    except requests.exceptions.SSLError:
        current_app.logger.exception('[register] Firebase SSL error during sign-up')
        return None, None, 'Registration is temporarily unavailable. Please try again in a moment.'
    except requests.exceptions.RequestException:
        current_app.logger.exception('[register] Firebase network error during sign-up')
        return None, None, 'Could not reach the registration service. Check your connection and try again.'
    except ValueError:
        current_app.logger.exception('[register] Firebase returned invalid JSON during sign-up')
        return None, None, 'Registration failed. Please try again.'

    if 'error' in data:
        msg = data['error'].get('message', 'Registration failed.')
        if msg == 'EMAIL_EXISTS':
            return None, None, 'Email already registered.'
        if 'WEAK_PASSWORD' in msg:
            return None, None, password_requirements_hint()
        return None, None, msg

    id_token = data['idToken']
    firebase_uid = data['localId']

    verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
    try:
        requests.post(
            verify_url,
            json={"requestType": "VERIFY_EMAIL", "idToken": id_token},
            verify=verify_ssl,
            timeout=30,
        )
    except requests.exceptions.RequestException:
        current_app.logger.warning('[register] Could not send verification email for %s', email)

    return id_token, firebase_uid, None


def _firebase_login(email, password):
    """Sign in with Firebase and return token + uid + verified status."""
    api_key = _firebase_api_key()
    if not api_key:
        return None, None, False, 'Firebase not configured.'

    # Demo only (temporary): Microsoft Store Python on Windows often fails SSL verification
    # against identitytoolkit.googleapis.com (CERTIFICATE_VERIFY_FAILED). Remove verify=False
    # after installing proper CA certs or using a standard Python build for production.
    verify_ssl = False

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    try:
        resp = requests.post(
            url,
            json={
                "email": email,
                "password": password,
                "returnSecureToken": True,
            },
            verify=verify_ssl,
            timeout=30,
        )
        data = resp.json()
    except requests.exceptions.SSLError:
        current_app.logger.exception('[login] Firebase SSL error during sign-in')
        return None, None, False, 'Sign-in is temporarily unavailable. Please try again in a moment.'
    except requests.exceptions.RequestException:
        current_app.logger.exception('[login] Firebase network error during sign-in')
        return None, None, False, 'Could not reach the sign-in service. Check your connection and try again.'
    except ValueError:
        current_app.logger.exception('[login] Firebase returned invalid JSON during sign-in')
        return None, None, False, 'Sign-in failed. Please try again.'

    if 'error' in data:
        return None, None, False, 'Invalid email or password.'

    id_token = data.get('idToken')
    firebase_uid = data.get('localId')
    if not id_token or not firebase_uid:
        current_app.logger.error('[login] Firebase sign-in response missing idToken or localId')
        return None, None, False, 'Sign-in failed. Please try again.'

    lookup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
    try:
        lookup_resp = requests.post(
            lookup_url,
            json={"idToken": id_token},
            verify=verify_ssl,
            timeout=30,
        )
        lookup_data = lookup_resp.json()
    except requests.exceptions.SSLError:
        current_app.logger.exception('[login] Firebase SSL error during email lookup')
        return None, None, False, 'Sign-in is temporarily unavailable. Please try again in a moment.'
    except requests.exceptions.RequestException:
        current_app.logger.exception('[login] Firebase network error during email lookup')
        return None, None, False, 'Could not reach the sign-in service. Check your connection and try again.'
    except ValueError:
        current_app.logger.exception('[login] Firebase returned invalid JSON during email lookup')
        return None, None, False, 'Sign-in failed. Please try again.'

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
        password_confirm = request.form.get('password_confirm', '')
        phone    = request.form.get('phone', '').strip()
        address  = request.form.get('address', '').strip()
        referral_code = request.form.get('referral_code', '').strip()
        dob_raw = request.form.get('date_of_birth', '').strip()

        error = _validate_registration(
            username, email, password, phone, password_confirm
        )
        if error:
            return jsonify({'status': 'error', 'message': error}), 400

        if UserRepository.get_by_username(username):
            return jsonify({'status': 'error', 'message': 'Username is already taken.'}), 400

        if UserRepository.get_by_email(email):
            return jsonify({'status': 'error', 'message': 'Email already registered.'}), 400

        if phone and UserRepository.get_by_phone(phone):
            return jsonify({'status': 'error', 'message': 'This phone number is already registered.'}), 400

        if referral_code:
            from app.services.referral_service import ReferralService
            referrer = ReferralService.get_by_referral_code(referral_code)
            if not referrer:
                return jsonify({'status': 'error', 'message': 'Invalid referral code.'}), 400

        if not _firebase_api_key():
            return jsonify({'status': 'error', 'message': 'Firebase not configured.'}), 500

        _, firebase_uid, firebase_error = _firebase_register(email, password)
        if firebase_error:
            return jsonify({'status': 'error', 'message': firebase_error}), 400

        # ── Save to SQLite immediately after Firebase success ──────────
        # If this fails, we catch it and return an error so the user knows
        try:
            new_user = User(
                username=username,
                email=email,
                firebase_uid=firebase_uid,
                password_hash=generate_password_hash(password),
                phone=phone or None,
                address=address or None,
            )
            if dob_raw:
                try:
                    from datetime import datetime as dt
                    new_user.date_of_birth = dt.strptime(dob_raw, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'status': 'error', 'message': 'Invalid date of birth. Use YYYY-MM-DD.'}), 400
            UserRepository.create(new_user)
            RoleRepository.attach_role_to_user(new_user, ROLE_CUSTOMER)
            try:
                from app.services.user_onboarding_service import UserOnboardingService
                UserOnboardingService.setup_new_customer(new_user, referral_code or None)
            except Exception as onboarding_err:
                current_app.logger.warning(
                    "[register] Onboarding partial failure for %s: %s", email, onboarding_err
                )
        except Exception as e:
            # Firebase account was created but SQLite failed — log it
            current_app.logger.error(
                f"[register] SQLite save failed for {email} (firebase_uid={firebase_uid}): {e}"
            )
            return jsonify({
                'status': 'error',
                'message': 'Account creation failed. Please contact support.'
            }), 500

        if current_app.config.get('SKIP_FIREBASE_EMAIL_VERIFICATION'):
            success_message = 'Account created! You can sign in now.'
        else:
            success_message = (
                'Account created! Please check your email to verify your account before logging in.'
            )
        return jsonify({
            'status':   'success',
            'message':  success_message,
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

        # ── Find user in SQLite ────────────────────────────────────────
        user = UserRepository.get_by_login_identifier(identifier)

        # ── Resolve the email to authenticate with Firebase ───────────
        if user:
            login_email = user.email
        elif '@' in identifier:
            # User exists in Firebase but not SQLite — we'll handle below
            login_email = identifier.lower()
        else:
            # Username not found anywhere — can't resolve to email
            return jsonify({'status': 'error', 'message': 'Invalid credentials.'}), 401

        # ── Staff: local password check only, no Firebase ─────────────
        if user and user.uses_staff_authentication():
            if not user.is_active:
                return jsonify({'status': 'error', 'message': 'Invalid credentials.'}), 401
            if not user.password_hash or not check_password_hash(user.password_hash, password):
                return jsonify({'status': 'error', 'message': 'Invalid credentials.'}), 401
            login_user(user, remember=False)
            return jsonify({
                'status': 'success',
                'message': 'Welcome back!',
                'redirect': get_post_login_redirect(user),
            }), 200

        # ── Customer: Firebase authentication ─────────────────────────
        if not _firebase_api_key():
            return jsonify({'status': 'error', 'message': 'Firebase not configured.'}), 500

        _, firebase_uid, email_verified, firebase_error = _firebase_login(login_email, password)

        if firebase_error:
            status = 503 if 'unavailable' in firebase_error.lower() or 'connection' in firebase_error.lower() else 401
            return jsonify({'status': 'error', 'message': firebase_error}), status

        skip_verify = current_app.config.get('SKIP_FIREBASE_EMAIL_VERIFICATION', False)
        if not email_verified and not skip_verify:
            return jsonify({
                'status': 'error',
                'message': 'Please verify your email before logging in. Check your inbox.',
            }), 401

        # ── Auto-sync: create SQLite record if missing ─────────────────
        # This fixes anyone who registered before this patch,
        # or whose SQLite record was lost for any reason.
        if not user:
            base_username = login_email.split('@')[0]
            username = base_username
            counter = 1
            while UserRepository.get_by_username(username):
                username = f"{base_username}{counter}"
                counter += 1

            try:
                user = User(
                    username=username,
                    email=login_email,
                    firebase_uid=firebase_uid,
                    is_active=True,
                )
                UserRepository.create(user)
                RoleRepository.attach_role_to_user(user, ROLE_CUSTOMER)
                current_app.logger.info(
                    f"[login] Auto-synced Firebase user {login_email} into SQLite."
                )
            except Exception as e:
                current_app.logger.error(f"[login] Auto-sync failed for {login_email}: {e}")
                return jsonify({'status': 'error', 'message': 'Login failed. Please try again.'}), 500

        # ── Sync firebase_uid if it was missing ───────────────────────
        if not user.firebase_uid:
            user.firebase_uid = firebase_uid
            from app.extensions import db
            db.session.commit()

        # ── UID mismatch = someone tampered with data ──────────────────
        if user.firebase_uid != firebase_uid:
            return jsonify({'status': 'error', 'message': 'Invalid credentials.'}), 401

        if not user.is_active:
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