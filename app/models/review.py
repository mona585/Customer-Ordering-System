# app/models/review.py

from app.extensions import db
from datetime import datetime


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('User', back_populates='reviews')
    
    def __repr__(self):
        return f'<Review {self.id} - {self.rating} stars>'