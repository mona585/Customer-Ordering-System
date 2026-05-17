from datetime import datetime

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from app.security.password_policy import validate_password_strength

from app.extensions import csrf
from app.repositories.referral_repository import ReferralRepository
from app.repositories.user_repository import UserRepository
from app.services.address_service import AddressService
from app.services.card_service import CardService
from app.services.order_service import OrderService
from app.services.referral_service import ReferralService
from app.services.rewards_service import RewardsService

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET"])
@login_required
def view_profile():
    rewards = RewardsService.get_profile_rewards(current_user.id)
    rewards_data = rewards.data if rewards.success else {}
    ref_stats = ReferralRepository.get_by_referrer_stats(current_user.id)
    if not current_user.referral_code:
        ReferralService.generate_referral_code(current_user)

    orders_result = OrderService.get_user_orders(current_user.id)
    all_orders = (
        orders_result.data.get("all", [])
        if orders_result.success and orders_result.data
        else []
    )
    recent_orders = all_orders[:8]
    addresses = AddressService.list_addresses(current_user.id)
    cards = CardService.list_cards(current_user.id)

    default_address = AddressService.get_default_formatted(current_user.id) or (current_user.address or "")

    return render_template(
        "profile/profile.html",
        user=current_user,
        points=rewards_data.get("points", current_user.points or 0),
        tier=rewards_data.get("tier", "Bronze"),
        vouchers=rewards_data.get("vouchers", []),
        wallet_balance=rewards_data.get("wallet_balance", 0),
        referral_code=current_user.referral_code or "",
        recent_orders=recent_orders,
        order_count=len(all_orders),
        addresses=addresses.data if addresses.success else [],
        saved_cards=cards.data if cards.success else [],
        default_address=default_address,
        **ref_stats,
    )


@profile_bp.route("/profile/edit", methods=["GET"])
@login_required
def edit_profile():
    return render_template("profile/edit_profile.html", user=current_user)


@profile_bp.route("/update", methods=["POST"])
@login_required
@csrf.exempt
def update_profile():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip() or None
    address = request.form.get("address", "").strip() or None
    password = request.form.get("password", "").strip() or None
    password_confirm = request.form.get("password_confirm", "").strip()
    dob_raw = request.form.get("date_of_birth", "").strip() or None

    if not username or len(username) < 3:
        return jsonify({"status": "error", "message": "Username must be at least 3 characters."}), 400
    if not email or "@" not in email:
        return jsonify({"status": "error", "message": "Please enter a valid email address."}), 400

    existing_user = UserRepository.get_by_username(username)
    if existing_user and existing_user.id != current_user.id:
        return jsonify({"status": "error", "message": "Username is already taken."}), 400
    existing_email = UserRepository.get_by_email(email)
    if existing_email and existing_email.id != current_user.id:
        return jsonify({"status": "error", "message": "Email is already in use."}), 400

    updates = {"username": username, "email": email, "phone": phone, "address": address}
    if dob_raw:
        try:
            updates["date_of_birth"] = datetime.strptime(dob_raw, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."}), 400
    if password:
        pwd_error = validate_password_strength(
            password, username=username, email=email
        )
        if pwd_error:
            return jsonify({"status": "error", "message": pwd_error}), 400
        if password != password_confirm:
            return jsonify({"status": "error", "message": "Passwords do not match."}), 400
        updates["password_hash"] = generate_password_hash(password)

    try:
        UserRepository.update(current_user.id, updates)
        return jsonify({"status": "success", "message": "Profile updated successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500


@profile_bp.route("/profile/update-preferences", methods=["POST"])
@login_required
def update_preferences():
    data = request.get_json(silent=True) or {}
    updates = {}
    if "dietary_preferences" in data:
        raw = data["dietary_preferences"]
        prefs = [p.strip() for p in raw.split(",") if p.strip()]
        updates["dietary_preferences"] = ",".join(prefs)
    if "other_allergies" in data:
        updates["other_allergies"] = data["other_allergies"].strip() or None
    if not updates:
        return jsonify({"status": "error", "message": "Nothing to update."}), 400
    try:
        UserRepository.update(current_user.id, updates)
        return jsonify({"status": "success", "message": "Preferences saved."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@profile_bp.route("/profile/apply-voucher/<code>")
@login_required
def apply_voucher_redirect(code):
    session["checkout_voucher"] = code.upper()
    return redirect(url_for("customer.checkout", voucher=code.upper()))


def _card_payload_from_request():
    data = request.get_json(silent=True) if request.is_json else None
    if data:
        return {
            "card_number": data.get("card_number", ""),
            "expiry": data.get("expiry", ""),
            "cvv": data.get("cvv", ""),
            "cardholder_name": data.get("cardholder_name") or data.get("card_name", ""),
            "set_default": data.get("set_default") in (True, "1", 1, "true"),
        }
    return {
        "card_number": request.form.get("card_number", ""),
        "expiry": request.form.get("expiry", ""),
        "cvv": request.form.get("cvv", ""),
        "cardholder_name": request.form.get("cardholder_name") or request.form.get("card_name", ""),
        "set_default": request.form.get("set_default") in ("1", "on", "true", True),
    }


def _json_auth_guard():
    if current_user.is_authenticated:
        return None
    return jsonify({"status": "error", "message": "Please log in to continue.", "redirect": url_for("auth.login")}), 401


@profile_bp.route("/profile/add-card", methods=["GET", "POST"])
@login_required
@csrf.exempt
def add_card():
    if request.method == "POST":
        auth_err = _json_auth_guard()
        if auth_err:
            return auth_err
        payload = _card_payload_from_request()
        result = CardService.add_card(
            current_user.id,
            payload["card_number"],
            set_default=payload["set_default"],
            expiry_raw=payload["expiry"],
            cvv=payload["cvv"],
            cardholder_name=payload["cardholder_name"],
        )
        if result.success:
            return jsonify({
                "status": "success",
                "message": result.message,
                "card": result.data,
            }), 200
        return jsonify({"status": "error", "message": result.error}), 400
    next_url = request.args.get("next") or url_for("profile.view_profile") + "#payments"
    return render_template("profile/add_card.html", next_url=next_url)


# --- Address API ---
@profile_bp.route("/api/addresses", methods=["GET"])
@login_required
def api_list_addresses():
    return jsonify(AddressService.list_addresses(current_user.id).data or [])


@profile_bp.route("/api/addresses", methods=["POST"])
@login_required
@csrf.exempt
def api_create_address():
    data = request.get_json(silent=True) or request.form
    result = AddressService.create_address(
        current_user.id,
        label=data.get("label", "Home"),
        street=data.get("street", ""),
        city=data.get("city", ""),
        set_default=data.get("is_default") in (True, "true", "1", 1),
    )
    if result.success:
        return jsonify({"status": "success", "address": result.data}), 201
    return jsonify({"status": "error", "message": result.error}), 400


@profile_bp.route("/api/addresses/<int:address_id>", methods=["PUT"])
@login_required
@csrf.exempt
def api_update_address(address_id):
    data = request.get_json(silent=True) or {}
    result = AddressService.update_address(current_user.id, address_id, **data)
    if result.success:
        return jsonify({"status": "success", "address": result.data})
    return jsonify({"status": "error", "message": result.error}), 400


@profile_bp.route("/api/addresses/<int:address_id>/default", methods=["POST"])
@login_required
@csrf.exempt
def api_set_default_address(address_id):
    result = AddressService.set_default(current_user.id, address_id)
    if result.success:
        return jsonify({"status": "success", "address": result.data})
    return jsonify({"status": "error", "message": result.error}), 400


@profile_bp.route("/api/addresses/<int:address_id>", methods=["DELETE"])
@login_required
@csrf.exempt
def api_delete_address(address_id):
    result = AddressService.delete_address(current_user.id, address_id)
    if result.success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": result.error}), 400


# --- Card API ---
@profile_bp.route("/api/cards", methods=["GET"])
@login_required
def api_list_cards():
    result = CardService.list_cards(current_user.id)
    return jsonify(result.data or [])


@profile_bp.route("/api/cards", methods=["POST"])
@login_required
@csrf.exempt
def api_add_card():
    auth_err = _json_auth_guard()
    if auth_err:
        return auth_err
    payload = _card_payload_from_request()
    result = CardService.add_card(
        current_user.id,
        payload["card_number"],
        set_default=payload["set_default"],
        expiry_raw=payload["expiry"],
        cvv=payload["cvv"],
        cardholder_name=payload["cardholder_name"],
    )
    if result.success:
        return jsonify({"status": "success", "message": result.message, "card": result.data}), 201
    return jsonify({"status": "error", "message": result.error}), 400


@profile_bp.route("/api/cards/<int:card_id>/default", methods=["POST"])
@login_required
@csrf.exempt
def api_set_default_card(card_id):
    result = CardService.set_default(current_user.id, card_id)
    if result.success:
        return jsonify({"status": "success", "card": result.data})
    return jsonify({"status": "error", "message": result.error}), 400


@profile_bp.route("/api/cards/<int:card_id>", methods=["DELETE"])
@login_required
@csrf.exempt
def api_delete_card(card_id):
    result = CardService.delete_card(current_user.id, card_id)
    if result.success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": result.error}), 400


@profile_bp.route("/api/rewards/redeem", methods=["POST"])
@login_required
@csrf.exempt
def api_redeem_points():
    data = request.get_json(silent=True) or {}
    idx = data.get("option_index", 0)
    result = RewardsService.redeem_points(current_user.id, idx)
    if result.success:
        return jsonify({"status": "success", "voucher": result.data, "message": result.message})
    return jsonify({"status": "error", "message": result.error}), 400
