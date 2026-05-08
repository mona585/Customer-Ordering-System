from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.repositories.user_repository import UserRepository

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
@login_required
def view_profile():
    return render_template('profile/profile.html', user=current_user)

@profile_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return jsonify({'status': 'error', 'message': 'Invalid request format.'}), 400

    username = request.form.get('username', '').strip()
    email    = request.form.get('email', '').strip().lower()
    phone    = request.form.get('phone', '').strip()
    address  = request.form.get('address', '').strip()
    password = request.form.get('password', '') # New password field

    if not username or not email:
        return jsonify({'status': 'error', 'message': 'Username and Email are required.'}), 400

    # 1. Check Username Duplicates
    existing_user = UserRepository.get_by_username(username)
    if existing_user and existing_user.id != current_user.id:
        return jsonify({'status': 'error', 'message': 'This username is already taken.'}), 400

    # 2. Check Email Duplicates
    existing_email = UserRepository.get_by_email(email)
    if existing_email and existing_email.id != current_user.id:
        return jsonify({'status': 'error', 'message': 'This email is already in use.'}), 400

    # 3. Check Phone Duplicates
    if phone:
        existing_phone = UserRepository.get_by_phone(phone)
        if existing_phone and existing_phone.id != current_user.id:
            return jsonify({'status': 'error', 'message': 'This phone number is already linked to another account.'}), 400

    # 4. Handle Password Update
    if password:
        if len(password) < 8:
            return jsonify({'status': 'error', 'message': 'Password must be at least 8 characters long.'}), 400
        current_user.password_hash = generate_password_hash(password)

    # 5. Update User Object
    current_user.username = username
    current_user.email = email
    current_user.phone = phone if phone else None
    current_user.address = address if address else None

    # Save to database
    UserRepository.update(current_user)

    return jsonify({
        'status': 'success',
        'message': 'Profile updated successfully!'
    }), 200