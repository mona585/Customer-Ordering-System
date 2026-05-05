# app/utils/seed_data_new.py
# Adds NEW items to existing data (does not delete old items)

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
    """Add NEW menu items that don't already exist (by name)"""

    items = [
        # ==================== APPETIZERS (6 new) ====================
        {
            'name': 'Hummus Trio',
            'description': 'Three flavors of hummus: roasted red pepper, classic, and pesto, served with warm pita.',
            'price': 9.50,
            'category': Category.APPETIZERS,
            'image_url': 'static/images/Hummus Trio.jpg',
            'stock_quantity': 30,
            'preparation_time': 8,
            'calories': 340,
            'ingredients': 'Chickpeas, tahini, red pepper, basil pesto, olive oil, pita bread'
        },
        {
            'name': 'Stuffed Mushrooms',
            'description': 'Portobello mushrooms stuffed with herbed cream cheese and baked until golden.',
            'price': 10.50,
            'category': Category.APPETIZERS,
            'image_url': 'static/images/Stuffed Mushrooms.jpg',
            'stock_quantity': 24,
            'preparation_time': 14,
            'calories': 290,
            'ingredients': 'Portobello mushrooms, cream cheese, herbs, breadcrumbs, parmesan'
        },
        {
            'name': 'Shrimp Cocktail',
            'description': 'Chilled jumbo shrimp served with tangy cocktail sauce and lemon wedges.',
            'price': 16.00,
            'category': Category.APPETIZERS,
            'image_url': 'static/images/Shrimp Cocktail.jpg',
            'stock_quantity': 18,
            'preparation_time': 10,
            'calories': 220,
            'ingredients': 'Jumbo shrimp, cocktail sauce, lemon, horseradish'
        },
        {
            'name': 'Caprese Skewers',
            'description': 'Fresh mozzarella, cherry tomatoes, and basil drizzled with balsamic glaze on skewers.',
            'price': 8.50,
            'category': Category.APPETIZERS,
            'image_url': 'static/images/Caprese Skewers.jpg',
            'stock_quantity': 28,
            'preparation_time': 7,
            'calories': 260,
            'ingredients': 'Mozzarella balls, cherry tomatoes, fresh basil, balsamic glaze, olive oil'
        },
        {
            'name': 'Falafel Bites',
            'description': 'Crispy falafel balls served with tahini sauce and pickled vegetables.',
            'price': 9.00,
            'category': Category.APPETIZERS,
            'image_url': 'static/images/Falafel Bites.jpg',
            'stock_quantity': 32,
            'preparation_time': 11,
            'calories': 380,
            'ingredients': 'Chickpeas, parsley, cumin, coriander, tahini, pickles'
        },
        {
            'name': 'Edamame',
            'description': 'Steamed edamame pods tossed with sea salt and chili flakes.',
            'price': 6.50,
            'category': Category.APPETIZERS,
            'image_url': 'static/images/Edamame.jpg',
            'stock_quantity': 40,
            'preparation_time': 6,
            'calories': 180,
            'ingredients': 'Edamame pods, sea salt, chili flakes'
        },

        # ==================== MAIN COURSE (8 new) ====================
        {
            'name': 'Beef Tacos',
            'description': 'Three soft corn tortillas with seasoned ground beef, salsa, cilantro, and lime.',
            'price': 15.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Beef Tacos.jpg',
            'stock_quantity': 25,
            'preparation_time': 16,
            'calories': 720,
            'ingredients': 'Ground beef, corn tortillas, salsa, cilantro, lime, onion'
        },
        {
            'name': 'Pad Thai',
            'description': 'Stir-fried rice noodles with shrimp, tofu, bean sprouts, peanuts, and tamarind sauce.',
            'price': 17.50,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Pad Thai.jpg',
            'stock_quantity': 20,
            'preparation_time': 18,
            'calories': 850,
            'ingredients': 'Rice noodles, shrimp, tofu, bean sprouts, peanuts, tamarind, egg'
        },
        {
            'name': 'Mushroom Risotto',
            'description': 'Creamy arborio rice with wild mushrooms, truffle oil, and parmesan shavings.',
            'price': 20.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Mushroom Risotto.jpg',
            'stock_quantity': 15,
            'preparation_time': 24,
            'calories': 780,
            'ingredients': 'Arborio rice, wild mushrooms, truffle oil, parmesan, white wine, butter'
        },
        {
            'name': 'Chicken Tikka Masala',
            'description': 'Tandoori chicken in rich tomato and cream sauce, served with basmati rice and naan.',
            'price': 19.50,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Chicken Tikka Masala.jpg',
            'stock_quantity': 18,
            'preparation_time': 22,
            'calories': 920,
            'ingredients': 'Chicken, yogurt, tomato, cream, garam masala, basmati rice, naan'
        },
        {
            'name': 'Beef Wellington',
            'description': 'Tender beef fillet wrapped in mushroom duxelles and puff pastry, served with red wine jus.',
            'price': 32.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Beef Wellington.jpg',
            'stock_quantity': 8,
            'preparation_time': 35,
            'calories': 1100,
            'ingredients': 'Beef fillet, mushrooms, puff pastry, prosciutto, red wine, thyme'
        },
        {
            'name': 'Seafood Paella',
            'description': 'Spanish saffron rice with mussels, shrimp, calamari, and chorizo.',
            'price': 25.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Seafood Paella.jpg',
            'stock_quantity': 12,
            'preparation_time': 28,
            'calories': 950,
            'ingredients': 'Bomba rice, mussels, shrimp, calamari, chorizo, saffron, bell peppers'
        },
        {
            'name': 'Vegan Buddha Bowl',
            'description': 'Nutrient-packed bowl with quinoa, roasted chickpeas, avocado, kale, and tahini dressing.',
            'price': 14.50,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Vegan Buddha Bowl.jpg',
            'stock_quantity': 20,
            'preparation_time': 15,
            'calories': 550,
            'ingredients': 'Quinoa, chickpeas, avocado, kale, sweet potato, tahini, lemon'
        },
        {
            'name': 'Duck Confit',
            'description': 'Slow-cooked duck leg with crispy skin, served with cherry sauce and roasted potatoes.',
            'price': 27.00,
            'category': Category.MAIN_COURSE,
            'image_url': 'static/images/Duck Confit.jpg',
            'stock_quantity': 10,
            'preparation_time': 30,
            'calories': 1050,
            'ingredients': 'Duck leg, duck fat, cherries, red wine, rosemary, potatoes'
        },

        # ==================== DESSERTS (6 new) ====================
        {
            'name': 'Panna Cotta',
            'description': 'Silky Italian vanilla custard with raspberry coulis and fresh mint.',
            'price': 9.50,
            'category': Category.DESSERTS,
            'image_url': 'static/images/Panna Cotta.jpg',
            'stock_quantity': 18,
            'preparation_time': 8,
            'calories': 320,
            'ingredients': 'Heavy cream, gelatin, vanilla, sugar, raspberries, mint'
        },
        {
            'name': 'Baklava',
            'description': 'Layers of flaky phyllo pastry filled with chopped walnuts and sweet honey syrup.',
            'price': 8.50,
            'category': Category.DESSERTS,
            'image_url': 'static/images/Baklava.jpg',
            'stock_quantity': 22,
            'preparation_time': 10,
            'calories': 480,
            'ingredients': 'Phyllo dough, walnuts, honey, butter, cinnamon, sugar'
        },
        {
            'name': 'Key Lime Pie',
            'description': 'Tangy key lime filling in a graham cracker crust with whipped cream topping.',
            'price': 9.00,
            'category': Category.DESSERTS,
            'image_url': 'static/images/Key Lime Pie.jpg',
            'stock_quantity': 16,
            'preparation_time': 9,
            'calories': 420,
            'ingredients': 'Key lime juice, condensed milk, graham crackers, butter, whipped cream'
        },
        {
            'name': 'Churros',
            'description': 'Crispy fried dough sticks dusted with cinnamon sugar, served with thick chocolate dip.',
            'price': 7.50,
            'category': Category.DESSERTS,
            'image_url': 'static/images/Churros.jpg',
            'stock_quantity': 30,
            'preparation_time': 12,
            'calories': 450,
            'ingredients': 'Flour, water, cinnamon, sugar, dark chocolate, heavy cream'
        },
        {
            'name': 'Lemon Tart',
            'description': 'Zesty lemon curd in a buttery shortcrust pastry with torched meringue peaks.',
            'price': 9.50,
            'category': Category.DESSERTS,
            'image_url': 'static/images/Lemon Tart.jpg',
            'stock_quantity': 15,
            'preparation_time': 10,
            'calories': 380,
            'ingredients': 'Lemons, eggs, butter, flour, sugar, meringue'
        },
        {
            'name': 'Affogato',
            'description': 'Vanilla gelato drowned in a shot of hot espresso, topped with crushed amaretti cookies.',
            'price': 7.00,
            'category': Category.DESSERTS,
            'image_url': 'static/images/Affogato.jpg',
            'stock_quantity': 25,
            'preparation_time': 4,
            'calories': 280,
            'ingredients': 'Vanilla gelato, espresso, amaretti cookies'
        },

        # ==================== BEVERAGES (6 new) ====================
        {
            'name': 'Thai Iced Tea',
            'description': 'Sweet and creamy Thai tea brewed with star anise and cardamom, served over ice.',
            'price': 5.50,
            'category': Category.BEVERAGES,
            'image_url': 'static/images/Thai Iced Tea.jpg',
            'stock_quantity': 40,
            'preparation_time': 5,
            'calories': 200,
            'ingredients': 'Black tea, star anise, cardamom, condensed milk, sugar, ice'
        },
        {
            'name': 'Virgin Mojito',
            'description': 'Refreshing mint and lime mocktail with soda water and a splash of cranberry.',
            'price': 5.00,
            'category': Category.BEVERAGES,
            'image_url': 'static/images/Virgin Mojito.jpg',
            'stock_quantity': 45,
            'preparation_time': 5,
            'calories': 110,
            'ingredients': 'Mint, lime, soda water, cranberry juice, sugar, ice'
        },
        {
            'name': 'Turmeric Latte',
            'description': 'Golden milk with turmeric, ginger, cinnamon, and honey, steamed to perfection.',
            'price': 5.50,
            'category': Category.BEVERAGES,
            'image_url': 'static/images/Turmeric Latte.jpg',
            'stock_quantity': 35,
            'preparation_time': 6,
            'calories': 150,
            'ingredients': 'Turmeric, ginger, cinnamon, honey, milk, black pepper'
        },
        {
            'name': 'Peach Iced Tea',
            'description': 'Freshly brewed black tea infused with ripe peach slices and a hint of mint.',
            'price': 4.50,
            'category': Category.BEVERAGES,
            'image_url': 'static/images/Peach Iced Tea.jpg',
            'stock_quantity': 40,
            'preparation_time': 5,
            'calories': 90,
            'ingredients': 'Black tea, fresh peaches, mint, honey, ice'
        },
        {
            'name': 'Coconut Water',
            'description': 'Fresh young coconut water served straight from the shell with a straw.',
            'price': 4.00,
            'category': Category.BEVERAGES,
            'image_url': 'static/images/Coconut Water.jpg',
            'stock_quantity': 50,
            'preparation_time': 3,
            'calories': 45,
            'ingredients': 'Fresh coconut water'
        },
        {
            'name': 'Espresso Tonic',
            'description': 'Bold espresso poured over tonic water with a twist of orange peel and ice.',
            'price': 6.00,
            'category': Category.BEVERAGES,
            'image_url': 'static/images/Espresso Tonic.jpg',
            'stock_quantity': 30,
            'preparation_time': 4,
            'calories': 60,
            'ingredients': 'Espresso, tonic water, orange peel, ice'
        },

        # ==================== SIDES (4 new) ====================
        {
            'name': 'Coleslaw',
            'description': 'Crunchy cabbage and carrot slaw with tangy mayo dressing and a hint of apple.',
            'price': 5.00,
            'category': Category.SIDES,
            'image_url': 'static/images/Coleslaw.jpg',
            'stock_quantity': 35,
            'preparation_time': 7,
            'calories': 180,
            'ingredients': 'Cabbage, carrots, mayo, apple cider vinegar, apple, celery seed'
        },
        {
            'name': 'Mashed Potatoes',
            'description': 'Creamy buttery mashed potatoes with roasted garlic and chives.',
            'price': 6.50,
            'category': Category.SIDES,
            'image_url': 'static/images/Mashed Potatoes.jpg',
            'stock_quantity': 30,
            'preparation_time': 12,
            'calories': 320,
            'ingredients': 'Potatoes, butter, cream, roasted garlic, chives, salt'
        },
        {
            'name': 'Roasted Brussels Sprouts',
            'description': 'Caramelized Brussels sprouts with balsamic glaze and crispy bacon bits.',
            'price': 7.50,
            'category': Category.SIDES,
            'image_url': 'static/images/Roasted Brussels Sprouts.jpg',
            'stock_quantity': 25,
            'preparation_time': 18,
            'calories': 240,
            'ingredients': 'Brussels sprouts, balsamic glaze, bacon, olive oil, black pepper'
        },
        {
            'name': 'Cornbread',
            'description': 'Sweet and moist cornbread baked in a cast iron skillet, served warm with honey butter.',
            'price': 5.50,
            'category': Category.SIDES,
            'image_url': 'static/images/Cornbread.jpg',
            'stock_quantity': 28,
            'preparation_time': 15,
            'calories': 290,
            'ingredients': 'Cornmeal, buttermilk, eggs, honey, butter, baking powder'
        },
    ]

    added_count = 0
    skipped_count = 0

    for item_data in items:
        # Check if item with this name already exists
        existing = MenuItem.query.filter_by(name=item_data['name']).first()
        if existing:
            print(f"⏭️  Skipped (already exists): {item_data['name']}")
            skipped_count += 1
            continue

        item = MenuItem(**item_data)
        db.session.add(item)
        added_count += 1
        print(f"✅ Added: {item_data['name']}")

    db.session.commit()
    print(f"\n📊 Summary: {added_count} added, {skipped_count} skipped")
    print(f"✅ Total items in database: {MenuItem.query.count()}")