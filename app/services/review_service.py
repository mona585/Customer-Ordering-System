# app/services/review_service.py
"""Review business logic"""

from app.repositories.review_repository import ReviewRepository
from app.repositories.menu_repository import MenuRepository
from app.models.review import Review
from app.services.base_service import BaseService, ServiceResult


class ReviewService(BaseService):
    """Handles product reviews"""

    @staticmethod
    def get_product_reviews(item_id):
        """Get reviews for a product"""
        item = MenuRepository.get_by_id(item_id)
        if not item:
            return ServiceResult.fail("Product not found")

        reviews = ReviewRepository.get_by_product(item_id)

        return ServiceResult.ok(data={
            'reviews': reviews,
            'count': len(reviews),
            'average': item.average_rating
        })

    @staticmethod
    def can_user_review(item_id, customer_id):
        """Check if user can review this item"""
        existing = ReviewRepository.get_customer_product_review(customer_id, item_id)

        if existing:
            return ServiceResult.fail("You already reviewed this item!", data={'can_review': False})

        return ServiceResult.ok(data={'can_review': True})

    @staticmethod
    def add_review(item_id, customer_id, rating, comment=''):
        """Add a new review"""
        menu_item = MenuRepository.get_by_id(item_id)
        if not menu_item:
            return ServiceResult.fail("Product not found")

        # Check if already reviewed
        check = ReviewService.can_user_review(item_id, customer_id)
        if not check.success:
            return check

        # Validate rating
        if not rating or rating < 1 or rating > 5:
            return ServiceResult.fail("Please select a rating (1-5 stars)")

        try:
            review = Review(
                menu_item_id=item_id,
                customer_id=customer_id,
                rating=rating,
                comment=comment.strip()
            )
            ReviewRepository.create(review)

            return ServiceResult.ok(message="Review added successfully!")

        except Exception as e:
            return ServiceResult.fail(f"Error adding review: {str(e)}")