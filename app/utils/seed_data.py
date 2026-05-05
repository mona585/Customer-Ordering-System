# app/utils/seed_data.py

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
    
    
    items = [
        # ==================== APPETIZERS ====================
        {
            'name': 'Mozzarella Sticks',
            'description': 'Golden fried mozzarella sticks served with marinara sauce.',
            'price': 10.00,
            'category': Category.APPETIZERS,
            'image_url': 'static/images/Mozzarella Sticks.jpg',
            'stock_quantity': 25,
            'preparation_time': 12,
            'calories': 450,
            'ingredients': 'Mozzarella cheese, breadcrumbs, marinara sauce, herbs'
        },
        {
            'name': 'Buffalo Wings',
            'description': 'Crispy chicken wings tossed in spicy buffalo sauce, served with blue cheese dip.',
            'price': 14.00,
            'category': Category.APPETIZERS,
            'image_url': 'static/images/Buffalo Wings.jpg',
            'stock_quantity': 20,
            'preparation_time': 15,
            'calories': 520,
            'ingredients': 'Chicken wings, buffalo sauce, blue cheese, celery'
        },
        {
            'name': 'Loaded Nachos',
            'description': 'Tortilla chips topped with melted cheese, jalapeños, sour cream, and guacamole.',
            'price': 12.00,
            'category': Category.APPETIZERS,
            'image_url': 'static/images/Loaded Nachos.jpg',
            'stock_quantity': 18,
            'preparation_time': 10,
            'calories': 680,
            'ingredients': 'Tortilla chips, cheese, jalapeños, sour cream, guacamole'
        },
        
        # ==================== MAIN COURSE ====================
        {
            'name': 'Classic Cheeseburger',
            'description': 'Juicy beef patty with cheddar cheese, lettuce, tomato, and special sauce on a brioche bun.',
            'price': 16.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Classic Cheeseburger.jpg',
            'stock_quantity': 30,
            'preparation_time': 20,
            'calories': 850,
            'ingredients': 'Beef patty, cheddar cheese, lettuce, tomato, brioche bun'
        },
        {
            'name': 'Grilled Chicken Sandwich',
            'description': 'Marinated grilled chicken breast with avocado, bacon, and chipotle mayo.',
            'price': 15.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Grilled Chicken Sandwich.jpg',
            'stock_quantity': 22,
            'preparation_time': 18,
            'calories': 720,
            'ingredients': 'Chicken breast, avocado, bacon, chipotle mayo, ciabatta'
        },
        {
            'name': 'Margherita Pizza',
            'description': 'Classic pizza with fresh mozzarella, tomato sauce, and basil on a thin crust.',
            'price': 14.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Margherita Pizza.jpg',
            'stock_quantity': 20,
            'preparation_time': 25,
            'calories': 780,
            'ingredients': 'Mozzarella, tomato sauce, basil, olive oil, thin crust'
        },
        {
            'name': 'Pasta Carbonara',
            'description': 'Creamy Italian pasta with pancetta, egg yolk, and parmesan cheese.',
            'price': 18.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Pasta Carbonara.jpg',
            'stock_quantity': 15,
            'preparation_time': 22,
            'calories': 920,
            'ingredients': 'Spaghetti, pancetta, egg yolk, parmesan, black pepper'
        },
        {
            'name': 'Fish & Chips',
            'description': 'Beer-battered cod served with crispy fries and tartar sauce.',
            'price': 17.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Fish & Chips.jpg',
            'stock_quantity': 12,
            'preparation_time': 20,
            'calories': 980,
            'ingredients': 'Cod, beer batter, potatoes, tartar sauce, lemon'
        },
        {
            'name': 'Steak Frites',
            'description': 'Grilled sirloin steak with herb butter and crispy French fries.',
            'price': 26.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Steak Frites.jpg',
            'stock_quantity': 10,
            'preparation_time': 25,
            'calories': 1100,
            'ingredients': 'Sirloin steak, herb butter, potatoes, parsley'
        },
        
        # ==================== DESSERTS ====================
        {
            'name': 'Tiramisu',
            'description': 'Classic Italian dessert with espresso-soaked ladyfingers and mascarpone cream.',
            'price': 9.00,
            'category': Category.DESSERTS,
            'image_url': 'static/images/Tiramisu.jpg',
            'stock_quantity': 20,
            'preparation_time': 10,
            'calories': 420,
            'ingredients': 'Ladyfingers, espresso, mascarpone, cocoa powder'
        },
        {
            'name': 'Chocolate Lava Cake',
            'description': 'Warm chocolate cake with a molten center, served with vanilla ice cream.',
            'price': 11.00,
            'category': Category.DESSERTS,
            'image_url': 'static/images/Chocolate Lava Cake.jpg',
            'stock_quantity': 15,
            'preparation_time': 15,
            'calories': 580,
            'ingredients': 'Dark chocolate, butter, eggs, flour, vanilla ice cream'
        },
        {
            'name': 'New York Cheesecake',
            'description': 'Rich and creamy cheesecake with a graham cracker crust and strawberry topping.',
            'price': 10.00,
            'category': Category.DESSERTS,
            'image_url': 'static/images/New York Cheesecake.jpg',
            'stock_quantity': 18,
            'preparation_time': 12,
            'calories': 520,
            'ingredients': 'Cream cheese, graham crackers, strawberries, sugar'
        },
        
        # ==================== BEVERAGES ====================
        {
            'name': 'Fresh Lemonade',
            'description': 'Refreshing homemade lemonade with fresh mint and a hint of honey.',
            'price': 5.00,
            'category': Category.BEVERAGES,
            'image_url': 'static/images/Fresh Lemonade.jpg',
            'stock_quantity': 50,
            'preparation_time': 5,
            'calories': 120,
            'ingredients': 'Lemons, mint, honey, water, ice'
        },
        {
            'name': 'Iced Caramel Latte',
            'description': 'Smooth espresso with caramel syrup and cold milk over ice.',
            'price': 6.00,
            'category': Category.BEVERAGES,
            'image_url': 'static/images/Iced Caramel Latte.jpg',
            'stock_quantity': 45,
            'preparation_time': 5,
            'calories': 250,
            'ingredients': 'Espresso, caramel syrup, milk, ice'
        },
        {
            'name': 'Mango Smoothie',
            'description': 'Tropical mango smoothie with yogurt and a touch of honey.',
            'price': 7.00,
            'category': Category.BEVERAGES,
            'image_url': 'static/images/Mango Smoothie.jpg',
            'stock_quantity': 40,
            'preparation_time': 5,
            'calories': 280,
            'ingredients': 'Mango, yogurt, honey, ice'
        },
        
        # ==================== SIDES ====================
        {
            'name': 'Truffle Fries',
            'description': 'Crispy hand-cut fries tossed with truffle oil and parmesan.',
            'price': 8.00,
            'category': Category.SIDES,
            'image_url': 'static/images/Truffle Fries.jpg',
            'stock_quantity': 35,
            'preparation_time': 15,
            'calories': 450,
            'ingredients': 'Potatoes, truffle oil, parmesan, parsley, sea salt'
        },
        {
            'name': 'Garlic Bread',
            'description': 'Sourdough with roasted garlic butter and fresh herbs.',
            'price': 6.00,
            'category': Category.SIDES,
            'image_url': 'static/images/Garlic Bread.jpg',
            'stock_quantity': 30,
            'preparation_time': 10,
            'calories': 320,
            'ingredients': 'Sourdough, garlic, butter, parsley, olive oil'
        },
        {
            'name': 'Classic Caesar Salad',
            'description': 'Crisp romaine lettuce with Caesar dressing, croutons, and parmesan.',
            'price': 9.00,
            'category': Category.SIDES,
            'image_url': 'static/images/Classic Caesar Salad.jpg',
            'stock_quantity': 20,
            'preparation_time': 8,
            'calories': 280,
            'ingredients': 'Romaine lettuce, Caesar dressing, croutons, parmesan'
        },
        {
            'name': 'Onion Rings',
            'description': 'Crispy battered onion rings served with spicy dipping sauce.',
            'price': 7.00,
            'category': Category.SIDES,
            'image_url': 'static/images/Onion Rings.jpg',
            'stock_quantity': 25,
            'preparation_time': 12,
            'calories': 380,
            'ingredients': 'Onions, batter, spices, dipping sauce'
        }
    ]
    
    for item_data in items:
        existing = MenuItem.query.filter_by(name=item_data['name']).first()
        if existing:
            print(f"⏭️  Skipped (already exists): {item_data['name']}")
            continue
        item = MenuItem(**item_data)
        db.session.add(item)
        print(f"✅ Added: {item_data['name']}")
    db.session.commit()