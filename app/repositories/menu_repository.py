# app/repositories/menu_repository.py
"""Menu/MenuItem data access layer"""

from app.extensions import db
from app.models.menu_item import MenuItem, Category


class MenuRepository:
    """Abstracts all MenuItem database operations"""

    @staticmethod
    def get_by_id(item_id):
        # .query.get() removed in SQLAlchemy 2.x
        return db.session.get(MenuItem, item_id)

    @staticmethod
    def list_all_for_admin():
        """All menu items (including unavailable), grouped sort by category then name."""
        return MenuItem.query.order_by(MenuItem.category, MenuItem.name).all()

    @staticmethod
    def get_all_available():
        return MenuItem.query.filter_by(is_available=True).all()

    @staticmethod
    def get_by_category(category):
        return MenuItem.query.filter_by(
            category=category,
            is_available=True
        ).all()

    @staticmethod
    def search(query_term, matched_category=None):
        """Search in name, description, ingredients"""
        text_filter = db.or_(
            MenuItem.name.ilike(query_term),
            MenuItem.description.ilike(query_term),
            MenuItem.ingredients.ilike(query_term)
        )

        if matched_category:
            final_filter = db.or_(text_filter, MenuItem.category == matched_category)
        else:
            final_filter = text_filter

        return MenuItem.query.filter_by(is_available=True).filter(final_filter).all()

    @staticmethod
    def get_related_items(item, limit=4):
        return MenuItem.query.filter_by(
            category=item.category,
            is_available=True
        ).filter(MenuItem.id != item.id).limit(limit).all()

    @staticmethod
    def save(item: MenuItem) -> MenuItem:
        db.session.add(item)
        return item

    @staticmethod
    def commit() -> bool:
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False