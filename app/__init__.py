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

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import jsonify, redirect, request, url_for

        wants_json = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            or 'application/json' in (request.headers.get('Accept') or '')
        )
        if wants_json:
            return jsonify({'status': 'error', 'message': 'Please log in to continue.'}), 401
        return redirect(url_for('auth.login', next=request.url))

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
    from app.routes.order import order_bp, api_order_bp
    from app.routes.profile import profile_bp
    from app.routes.notifications import notifications_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(order_bp, url_prefix='/order')
    app.register_blueprint(api_order_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(delivery_bp)
    app.register_blueprint(pages_bp)

    # Ensure SQLite database directory exists
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite:///") and not db_uri.endswith(":memory:"):
        db_path = db_uri.replace("sqlite:///", "", 1)
        if db_path and not os.path.isabs(db_path):
            db_path = os.path.join(app.root_path, "..", db_path)
        db_dir = os.path.dirname(os.path.abspath(db_path))
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    # Create tables if they don't exist; seed RBAC rows
    with app.app_context():
        os.makedirs(os.path.join(os.path.dirname(app.root_path), "instance"), exist_ok=True)
        db.create_all()

        from app.bootstrap.schema_compat import ensure_users_schema_compat

        ensure_users_schema_compat()

        from app.bootstrap.rewards_compat import ensure_rewards_compat

        ensure_rewards_compat()

        from app.bootstrap.rbac import ensure_rbac_initialized

        ensure_rbac_initialized()

        from app.bootstrap.seed import ensure_startup_seed

        ensure_startup_seed(config_name)

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
    @app.errorhandler(500)
    def internal_error(error):
        import traceback
        from flask import jsonify
        return jsonify({
            'status': 'error',
            'message': str(error),
            'traceback': traceback.format_exc()
        }), 500


    return app
