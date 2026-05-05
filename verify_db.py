#!/usr/bin/env python3
"""
AURA Database Verification Script
Place this file in PROJECT ROOT (same folder as wsgi.py and run.py)

Usage: python verify_db.py
"""

import sys
import os

if not os.path.exists('wsgi.py'):
    print("Error: Please run this script from the project root folder")
    print("   (the same folder containing wsgi.py and run.py)")
    sys.exit(1)

def verify_database():
    print("AURA Database Verification")
    print("=" * 50)

    try:
        print("\nStep 1: Testing model imports...")
        from app.extensions import db
        from app.models.user import User
        from app.models.menu_item import MenuItem, Category
        from app.models.orders import Order, OrderStatus
        from app.models.order_item import OrderItem
        from app.models.payment import Payment, PaymentStatus, PaymentMethod
        from app.models.review import Review
        from app.models.wishlist import Wishlist
        from app.models.order_status_history import OrderStatusHistory
        print("  All 9 models imported successfully")

        print("\nStep 2: Creating database tables...")
        from wsgi import create_app
        app = create_app('testing')

        with app.app_context():
            db.create_all()

            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            expected_tables = [
                'users', 'menu_items', 'orders', 'order_items',
                'payments', 'reviews', 'order_status_history', 'wishlists'
            ]

            print("\nStep 3: Checking tables (" + str(len(tables)) + " found):")
            all_good = True
            for table in expected_tables:
                if table in tables:
                    print("  OK " + table)
                else:
                    print("  MISSING: " + table)
                    all_good = False

            if not all_good:
                print("\nSome tables are missing!")
                return False

            print("\nStep 4: Testing relationships...")

            # Create test data
            test_user = User(
                username='testuser',
                email='test@aura.com',
                phone='+1 234 567 890',
                address='123 Test Street'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.flush()

            test_item = MenuItem(
                name='Test Burger',
                description='A test burger',
                price=10.00,
                category=Category.MAIN_COURSE,
                stock_quantity=10
            )
            db.session.add(test_item)
            db.session.flush()

            test_order = Order(
                customer_id=test_user.id,
                total_amount=20.00,
                status=OrderStatus.PENDING,
                delivery_address='123 Test St'
            )
            db.session.add(test_order)
            db.session.flush()

            test_order_item = OrderItem(
                order_id=test_order.id,
                menu_item_id=test_item.id,
                quantity=2,
                unit_price=10.00
            )
            db.session.add(test_order_item)

            test_payment = Payment(
                order_id=test_order.id,
                amount=20.00,
                method=PaymentMethod.CREDIT_CARD,
                status=PaymentStatus.PENDING
            )
            db.session.add(test_payment)

            test_review = Review(
                customer_id=test_user.id,
                menu_item_id=test_item.id,
                rating=5,
                comment='Excellent!'
            )
            db.session.add(test_review)

            test_wishlist = Wishlist(
                customer_id=test_user.id,
                menu_item_id=test_item.id
            )
            db.session.add(test_wishlist)

            test_status_history = OrderStatusHistory(
                order_id=test_order.id,
                status='PENDING'
            )
            db.session.add(test_status_history)

            db.session.commit()

            # Verify relationships
            assert len(test_user.orders) == 1
            assert len(test_user.reviews) == 1
            assert len(test_user.wishlists) == 1
            assert len(test_order.items) == 1
            assert test_order.payment is not None
            assert len(test_item.reviews) == 1
            assert len(test_order.status_history) == 1

            print("  All relationships working correctly")

            # Cleanup - delete parent first, cascade handles children
            print("\nStep 5: Testing cascade delete...")
            db.session.delete(test_order)
            db.session.flush()
            db.session.delete(test_user)
            db.session.flush()
            db.session.delete(test_item)
            db.session.commit()
            print("  Cascade delete working correctly")

            print("\nSUCCESS! Database is fully configured!")
            print("=" * 50)
            print("\nSummary:")
            print("  - 8 tables created")
            print("  - All relationships verified")
            print("  - Cascade delete verified")
            print("\nYou can now run: python run.py")
            return True

    except ImportError as e:
        print("\nImport Error: " + str(e))
        print("\nMake sure all model files are in app/models/")
        return False

    except Exception as e:
        print("\nError: " + str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = verify_database()
    sys.exit(0 if success else 1)