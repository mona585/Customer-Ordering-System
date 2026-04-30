from app import create_app
from app.extensions import db
from app.utils.seed_data import seed_menu_items, seed_test_user

app = create_app()

with app.app_context():
    seed_menu_items()
    seed_test_user()
    print("✅ Seed completed")