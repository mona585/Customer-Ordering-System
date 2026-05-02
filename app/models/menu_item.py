from enum import Enum
from app.extensions import db


class Category(Enum):
    APPETIZERS = "Appetizers"
    MAIN_COURSE = "Main Course"
    DESSERTS = "Desserts"
    BEVERAGES = "Beverages"
    SIDES = "Sides"


class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.Enum(Category), nullable=False)
    image_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    stock_quantity = db.Column(db.Integer, default=10)  # ← NEW: Available stock
    preparation_time = db.Column(db.Integer, default=15)
    calories = db.Column(db.Integer)
    ingredients = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='menu_item', lazy=True)
    reviews = db.relationship('Review', backref='menu_item', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MenuItem {self.name}>'
    
    @property
    def available_stock(self):
        """Calculate actual available stock (total - pending)"""
        from app.models.orders import Order, OrderStatus
        from app.models.order_item import OrderItem
        
        # Get pending quantities (in carts or pending orders)
        pending = db.session.query(db.func.sum(OrderItem.quantity)).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            OrderItem.menu_item_id == self.id,
            Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED])
        ).scalar() or 0
        
        return max(0, self.stock_quantity - pending)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'category': self.category.value,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'stock_quantity': self.stock_quantity,
            'available_stock': self.available_stock,
            'preparation_time': self.preparation_time,
            'calories': self.calories,
            'ingredients': self.ingredients,
            'average_rating': self.average_rating,
            'review_count': len(self.reviews)
        }
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)