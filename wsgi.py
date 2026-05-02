
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_name='development'):
    app = Flask(__name__,
                template_folder='app/templates',
                static_folder='app/static')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Login settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.customer import customer_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    
    # Create tables and seed data
    with app.app_context():
        db.create_all()
        
        # Seed data if empty
        from app.models.menu_item import MenuItem, Category
        if not MenuItem.query.first():
            from app.utils.seed_data import seed_menu_items, seed_test_user
            seed_menu_items()
            seed_test_user()
            print("✅ Database seeded")
    
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))


# Run the app
if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
