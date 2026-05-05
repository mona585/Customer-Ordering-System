from app.extensions import db
from datetime import datetime


class Wishlist(db.Model):
    """Wishlist model for favorite items"""
    __tablename__ = 'wishlists'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    menu_item = db.relationship('MenuItem', backref='wishlist_entries')

    def __repr__(self):
        return f'<Wishlist {self.id}>'