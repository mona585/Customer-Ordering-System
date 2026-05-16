from flask import Blueprint, render_template
from flask_login import current_user

from app.services.menu_service import MenuService
from app.services.wishlist_service import WishlistService

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    result = MenuService.get_all_categories()
    categories = result.data if result.success else {}

    wishlist_ids = set()
    if current_user.is_authenticated:
        try:
            wishlist_result = WishlistService.get_user_wishlist(current_user.id)
            if wishlist_result.success:
                wishlist_ids = {entry['menu_item'].id for entry in wishlist_result.data}
        except Exception:
            pass

    return render_template(
        'products/home.html',
        categories=categories,
        active_category='all',
        wishlist_ids=wishlist_ids,
    )