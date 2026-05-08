# app/repositories/wishlist_repository.py
"""Wishlist data access layer"""

from app.extensions import db
from app.models.wishlist import Wishlist


class WishlistRepository:
    """Abstracts all Wishlist database operations"""

    @staticmethod
    def get_by_id(wishlist_id):
        # .query.get() is removed in SQLAlchemy 2.x — use db.session.get() instead
        return db.session.get(Wishlist, wishlist_id)

    @staticmethod
    def get_by_customer(customer_id):
        return Wishlist.query.filter_by(customer_id=customer_id).all()

    @staticmethod
    def get_customer_item(customer_id, item_id):
        return Wishlist.query.filter_by(
            customer_id=customer_id,
            menu_item_id=item_id
        ).first()

    @staticmethod
    def create(wishlist):
        db.session.add(wishlist)
        db.session.commit()
        return wishlist

    @staticmethod
    def delete(wishlist):
        db.session.delete(wishlist)
        db.session.commit()