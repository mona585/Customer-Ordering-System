# app/__init__.py
"""AURA Application Factory - SINGLE SOURCE OF TRUTH"""



import os
from flask import Flask

# Import extensions
from app.extensions import db, login_manager, migrate, csrf

# Import Firebase configuration (initializes on import)
import firebase_config

def create_app(config_name='development'):
    """Application factory pattern - creates and configures the Flask app"""

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

    # User loader (eager-load roles for RBAC checks)
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        uid = int(user_id)
        return db.session.execute(
            select(User).options(selectinload(User.roles)).where(User.id == uid)
        ).scalar_one_or_none()

    # Register blueprints
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.customer import customer_bp
    from app.routes.delivery import delivery_bp
    from app.routes.main import main_bp
    from app.routes.order import order_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(order_bp, url_prefix='/order')
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(delivery_bp)
    
    # Create tables if they don't exist; seed RBAC rows
    with app.app_context():
        db.create_all()
        from app.bootstrap.rbac import ensure_rbac_initialized

        ensure_rbac_initialized()

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
