# app/repositories/review_repository.py
"""Review data access layer"""

from app.extensions import db
from app.models.review import Review


class ReviewRepository:
    """Abstracts all Review database operations"""

    @staticmethod
    def get_by_id(review_id):
        return Review.query.get(review_id)

    @staticmethod
    def get_by_product(item_id):
        return Review.query.filter_by(menu_item_id=item_id)\
                          .order_by(Review.created_at.desc()).all()

    @staticmethod
    def get_by_customer(customer_id):
        return Review.query.filter_by(customer_id=customer_id).all()

    @staticmethod
    def get_customer_product_review(customer_id, item_id):
        return Review.query.filter_by(
            customer_id=customer_id,
            menu_item_id=item_id
        ).first()

    @staticmethod
    def create(review):
        db.session.add(review)
        db.session.commit()
        return review

    @staticmethod
    def delete(review):
        db.session.delete(review)
        db.session.commit()
