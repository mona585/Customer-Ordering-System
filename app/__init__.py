# app/__init__.py
"""AURA Application Factory - SINGLE SOURCE OF TRUTH"""



import os

from dotenv import load_dotenv
from flask import Flask

# Import extensions
from app.extensions import db, login_manager, migrate, csrf

# Import Firebase configuration (initializes on import)
import firebase_config

def create_app(config_name='development'):
    """Application factory pattern - creates and configures the Flask app"""

    load_dotenv()

    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    app.config['WTF_CSRF_ENABLED'] = False


    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Login settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # User loader
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.customer import customer_bp
    from app.routes.order import order_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(order_bp, url_prefix='/order')
    app.register_blueprint(profile_bp)
    
    # Create tables if they don't exist
    with app.app_context():
        os.makedirs(os.path.join(os.path.dirname(app.root_path), "instance"), exist_ok=True)
        db.create_all()
        from app.bootstrap.schema_compat import ensure_users_schema_compat
        from app.bootstrap.rbac import ensure_rbac_initialized
        from app.bootstrap.dev_accounts import ensure_dev_accounts

        ensure_users_schema_compat()
        ensure_rbac_initialized()
        if app.config.get("DEBUG"):
            ensure_dev_accounts()

    @app.errorhandler(403)
    def forbidden_page(_error):
        from flask import render_template_string

        return (
            render_template_string(
                "<!doctype html><title>Forbidden</title>"
                "<h1>403 — Forbidden</h1>"
                "<p>You do not have access to this area.</p>"
                "<p><a href=\"{{ url_for('main.home') }}\">Home</a></p>"
            ),
            403,
        )

    return app
