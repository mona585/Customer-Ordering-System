# app/services/wishlist_service.py
"""Wishlist business logic"""

from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.menu_repository import MenuRepository
from app.models.wishlist import Wishlist
from app.services.base_service import BaseService, ServiceResult


class WishlistService(BaseService):
    """Handles user wishlist/favorites"""

    @staticmethod
    def get_user_wishlist(customer_id):
        """Get all wishlist items for a user"""
        wishlist_items = WishlistRepository.get_by_customer(customer_id)

        items = []
        for entry in wishlist_items:
            if entry.menu_item:
                items.append({
                    'id': entry.id,
                    'menu_item': entry.menu_item,
                    'added_at': entry.created_at
                })

        return ServiceResult.ok(data=items)

    @staticmethod
    def add_to_wishlist(customer_id, item_id):
        """Add item to wishlist"""
        menu_item = MenuRepository.get_by_id(item_id)
        if not menu_item:
            return ServiceResult.fail("Item not found")

        # Check if already in wishlist
        existing = WishlistRepository.get_customer_item(customer_id, item_id)

        if existing:
            return ServiceResult.fail("Item already in wishlist")

        try:
            wishlist = Wishlist(
                customer_id=customer_id,
                menu_item_id=item_id
            )
            WishlistRepository.create(wishlist)

            return ServiceResult.ok(
                data={'wishlist_id': wishlist.id},
                message=f"{menu_item.name} added to wishlist"
            )

        except Exception as e:
            return ServiceResult.fail(f"Error adding to wishlist: {str(e)}")

    @staticmethod
    def remove_from_wishlist(customer_id, wishlist_id):
        """Remove item from wishlist"""
        entry = WishlistRepository.get_by_id(wishlist_id)

        if not entry or entry.customer_id != customer_id:
            return ServiceResult.fail("Item not found in wishlist")

        try:
            WishlistRepository.delete(entry)
            return ServiceResult.ok(message="Removed from wishlist")

        except Exception as e:
            return ServiceResult.fail(f"Error removing from wishlist: {str(e)}")

    @staticmethod
    def is_in_wishlist(customer_id, item_id):
        """Check if item is in user's wishlist"""
        exists = WishlistRepository.get_customer_item(customer_id, item_id)

        return ServiceResult.ok(data={'is_wishlisted': bool(exists)})