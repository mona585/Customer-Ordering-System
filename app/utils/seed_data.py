# 13. SEED DATA FILE (seed_data.py) - Fixed

from app.extensions import db
from app.models.user import User
from app.models.menu_item import MenuItem, Category
from werkzeug.security import generate_password_hash


def seed_test_user():
    """Create a test user if none exists"""
    if not User.query.filter_by(email='test@aura.com').first():
        user = User(
            username='testuser',
            email='test@aura.com',
            password_hash=generate_password_hash('password123'),
            phone='+1 234 567 890',
            address='123 Test Street, Test City, TC 12345'
        )
        db.session.add(user)
        db.session.commit()
        print("✅ Test user created: test@aura.com / password123")


def seed_menu_items():
    """Seed menu items if table is empty"""
    if MenuItem.query.first():
        return
    
    items = [
        # Appetizers
        {
            'name': 'Truffle Arancini',
            'description': 'Crispy risotto balls infused with black truffle, served with garlic aioli.',
            'price': 14.00,
            'category': Category.APPETIZERS,
            'image_url': 'https://images.unsplash.com/photo-1541529086526-db283c563270?w=400&h=300&fit=crop',
            'preparation_time': 15,
            'calories': 380,
            'ingredients': 'Arborio rice, black truffle, parmesan, breadcrumbs, garlic aioli'
        },
        {
            'name': 'Burrata & Heirloom Tomato',
            'description': 'Creamy burrata cheese with fresh heirloom tomatoes, basil oil, and balsamic glaze.',
            'price': 16.00,
            'category': Category.APPETIZERS,
            'image_url': 'https://images.unsplash.com/photo-1529312266912-b33cf6227e2f?w=400&h=300&fit=crop',
            'preparation_time': 10,
            'calories': 320,
            'ingredients': 'Burrata, heirloom tomatoes, basil, balsamic glaze, olive oil'
        },
        {
            'name': 'Wagyu Beef Carpaccio',
            'description': 'Thinly sliced wagyu beef with truffle oil, capers, and shaved parmesan.',
            'price': 22.00,
            'category': Category.APPETIZERS,
            'image_url': 'https://images.unsplash.com/photo-1544025162-d76690b60944?w=400&h=300&fit=crop',
            'preparation_time': 12,
            'calories': 280,
            'ingredients': 'Wagyu beef, truffle oil, capers, parmesan, arugula'
        },
        
        # Main Course
        {
            'name': 'Pan-Seared Salmon',
            'description': 'Atlantic salmon with lemon butter sauce, asparagus, and herb roasted potatoes.',
            'price': 28.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=400&h=300&fit=crop',
            'preparation_time': 25,
            'calories': 580,
            'ingredients': 'Atlantic salmon, lemon, butter, asparagus, potatoes, herbs'
        },
        {
            'name': 'Truffle Mushroom Risotto',
            'description': 'Creamy arborio rice with wild mushrooms, truffle oil, and aged parmesan.',
            'price': 24.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=400&h=300&fit=crop',
            'preparation_time': 30,
            'calories': 620,
            'ingredients': 'Arborio rice, wild mushrooms, truffle oil, parmesan, white wine'
        },
        {
            'name': 'Ribeye Steak',
            'description': 'Prime ribeye with red wine reduction, garlic mashed potatoes, and grilled vegetables.',
            'price': 42.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'https://images.unsplash.com/photo-1546833998-877b37c2e5c6?w=400&h=300&fit=crop',
            'preparation_time': 35,
            'calories': 750,
            'ingredients': 'Ribeye beef, red wine, garlic, potatoes, seasonal vegetables'
        },
        {
            'name': 'Lobster Linguine',
            'description': 'Fresh pasta with lobster meat, cherry tomatoes, and white wine cream sauce.',
            'price': 36.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'https://images.unsplash.com/photo-1563379926898-05f4575a45d8?w=400&h=300&fit=crop',
            'preparation_time': 28,
            'calories': 680,
            'ingredients': 'Linguine, lobster, cherry tomatoes, cream, white wine, garlic'
        },
        
        # Desserts
        {
            'name': 'Tiramisu',
            'description': 'Classic Italian dessert with espresso-soaked ladyfingers and mascarpone cream.',
            'price': 12.00,
            'category': Category.DESSERTS,
            'image_url': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=400&h=300&fit=crop',
            'preparation_time': 10,
            'calories': 420,
            'ingredients': 'Ladyfingers, espresso, mascarpone, cocoa powder, marsala wine'
        },
        {
            'name': 'Chocolate Lava Cake',
            'description': 'Warm chocolate cake with a molten center, served with vanilla bean ice cream.',
            'price': 14.00,
            'category': Category.DESSERTS,
            'image_url': 'https://images.unsplash.com/photo-1624353365286-3f8d62daad51?w=400&h=300&fit=crop',
            'preparation_time': 20,
            'calories': 520,
            'ingredients': 'Dark chocolate, butter, eggs, flour, vanilla ice cream'
        },
        {
            'name': 'Crème Brûlée',
            'description': 'Rich vanilla custard with a caramelized sugar crust and fresh berries.',
            'price': 11.00,
            'category': Category.DESSERTS,
            'image_url': 'https://images.unsplash.com/photo-1470324161839-ce2bb6fa6bc3?w=400&h=300&fit=crop',
            'preparation_time': 15,
            'calories': 380,
            'ingredients': 'Cream, eggs, vanilla, sugar, mixed berries'
        },
        
        # Beverages
        {
            'name': 'Signature Mojito',
            'description': 'Fresh mint, lime, and premium rum with a splash of soda.',
            'price': 14.00,
            'category': Category.BEVERAGES,
            'image_url': 'https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=400&h=300&fit=crop',
            'preparation_time': 5,
            'calories': 180,
            'ingredients': 'White rum, fresh mint, lime, sugar, soda water'
        },
        {
            'name': 'Artisan Cold Brew',
            'description': '24-hour steeped cold brew coffee with oat milk and vanilla syrup.',
            'price': 7.00,
            'category': Category.BEVERAGES,
            'image_url': 'https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=300&fit=crop',
            'preparation_time': 3,
            'calories': 120,
            'ingredients': 'Cold brew coffee, oat milk, vanilla syrup, ice'
        },
        {
            'name': 'Fresh Green Juice',
            'description': 'Kale, spinach, apple, ginger, and lemon cold-pressed juice.',
            'price': 9.00,
            'category': Category.BEVERAGES,
            'image_url': 'https://images.unsplash.com/photo-1610970881699-44a5587cabec?w=400&h=300&fit=crop',
            'preparation_time': 5,
            'calories': 140,
            'ingredients': 'Kale, spinach, green apple, ginger, lemon'
        },
        
        # Sides
        {
            'name': 'Truffle Fries',
            'description': 'Crispy hand-cut fries tossed with truffle oil and parmesan.',
            'price': 10.00,
            'category': Category.SIDES,
            'image_url': 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400&h=300&fit=crop',
            'preparation_time': 15,
            'calories': 450,
            'ingredients': 'Potatoes, truffle oil, parmesan, parsley, sea salt'
        },
        {
            'name': 'Garlic Bread',
            'description': 'Sourdough with roasted garlic butter and fresh herbs.',
            'price': 8.00,
            'category': Category.SIDES,
            'image_url': 'https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?w=400&h=300&fit=crop',
            'preparation_time': 10,
            'calories': 320,
            'ingredients': 'Sourdough, garlic, butter, parsley, olive oil'
        },
        {
            'name': 'Seasonal Salad',
            'description': 'Mixed greens with cherry tomatoes, cucumber, and lemon vinaigrette.',
            'price': 9.00,
            'category': Category.SIDES,
            'image_url': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop',
            'preparation_time': 8,
            'calories': 180,
            'ingredients': 'Mixed greens, cherry tomatoes, cucumber, lemon vinaigrette'
        }
    ]
    
    for item_data in items:
        item = MenuItem(**item_data)
        db.session.add(item)
    
    db.session.commit()
    print(f"✅ Seeded {len(items)} menu items")
