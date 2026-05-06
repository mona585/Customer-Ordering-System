# app/services/menu_service.py
"""Menu and product related business logic"""

from app.repositories.menu_repository import MenuRepository
from app.services.base_service import BaseService, ServiceResult
from app.models.menu_item import Category


class MenuService(BaseService):
    """Handles menu browsing, search, and product details"""

    @staticmethod
    def get_all_categories():
        """Get all menu categories with items"""
        items = MenuRepository.get_all_available()

        categories = {
            'Appetizers': [],
            'Main Course': [],
            'Desserts': [],
            'Beverages': [],
            'Sides': []
        }

        for item in items:
            categories[item.category.value].append(item)

        return ServiceResult.ok(data=categories)

    @staticmethod
    def get_category_items(category_name):
        """Get items for specific category"""
        try:
            cat_enum = Category[category_name.upper().replace(' ', '_')]
            items = MenuRepository.get_by_category(cat_enum)
            return ServiceResult.ok(data=items)
        except (KeyError, ValueError):
            return ServiceResult.fail("Invalid category")

    @staticmethod
    def search_items(query):
        """Search in name, description, ingredients, and categories"""
        if not query or not query.strip():
            return ServiceResult.fail("Empty search query")

        search_term = f'%{query.strip()}%'

        # Check if query matches a category
        matched_category = None
        query_upper = query.upper()
        for cat in Category:
            if query_upper == cat.name or query_upper == cat.value.upper():
                matched_category = cat
                break

        items = MenuRepository.search(search_term, matched_category)

        # Organize by categories
        categories = {}
        for item in items:
            cat_name = item.category.value
            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(item)

        return ServiceResult.ok(data=categories)

    @staticmethod
    def get_product_details(item_id):
        """Get full product details with related items"""
        item = MenuRepository.get_by_id(item_id)
        if not item:
            return ServiceResult.fail("Product not found")

        related = MenuRepository.get_related_items(item)

        return ServiceResult.ok(data={
            'item': item,
            'related': related
        })

    @staticmethod
    def get_product_for_api(item_id):
        """Get product data for API/JSON response"""
        item = MenuRepository.get_by_id(item_id)
        if not item:
            return ServiceResult.fail("Product not found")

        return ServiceResult.ok(data=item.to_dict())