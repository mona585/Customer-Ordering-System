# app/models/review.py

from app.extensions import db
from datetime import datetime


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))  # Optional link
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Constraint: rating must be between 1 and 5
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
    
    def __repr__(self):
        return f'<Review {self.rating}⭐ by {self.customer.username if self.customer else "Unknown"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer': self.customer.username if self.customer else None,
            'menu_item': self.menu_item.name if self.menu_item else None,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }