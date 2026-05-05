from app import create_app
from app.extensions import db
from app.utils.seed_data import seed_menu_items as seed_old
from app.utils.seed_data_new import seed_menu_items as seed_new

app = create_app()

with app.app_context():
    db.create_all()
    
    # Add old items first
    print("=== Adding OLD items ===")
    seed_old()
    
    # Add new items
    print("\n=== Adding NEW items ===")
    seed_new()
    
    print("\n✅ All seeding completed!")