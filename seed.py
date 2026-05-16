# seed.py
"""Database seeding script - Run: python seed.py"""

from app import create_app
from app.extensions import db
from app.utils.seed_data import seed_dev_staff_accounts, seed_test_user, seed_menu_items as seed_old
from app.utils.seed_data_new import seed_menu_items as seed_new
from app.utils.seed_rewards import print_public_promo_codes, seed_test_vouchers

app = create_app('development')

with app.app_context():
    db.create_all()

    print("=== Users / RBAC (test customer + optional dev staff) ===")
    seed_test_user()
    seed_dev_staff_accounts()

    print("\n=== Adding OLD items ===")
    seed_old()  # ✅ uncommented

    print("\n=== Adding NEW items ===")
    seed_new()

    print("\n=== Rewards / vouchers ===")
    seed_test_vouchers()
    print_public_promo_codes()

    print("\n✅ All seeding completed!")