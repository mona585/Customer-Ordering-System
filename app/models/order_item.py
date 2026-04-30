# app/models/order_item.py

from app.extensions import db


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)  # Price at time of order
    special_requests = db.Column(db.Text)  # "No onions", "Extra cheese"
    
    def __repr__(self):
        return f'<OrderItem {self.menu_item.name if self.menu_item else "Unknown"} x{self.quantity}>'
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return float(self.unit_price) * self.quantity
    
    def to_dict(self):
        return {
            'id': self.id,
            'menu_item': self.menu_item.to_dict() if self.menu_item else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'subtotal': self.subtotal,
            'special_requests': self.special_requests
        }