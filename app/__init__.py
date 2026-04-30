from flask import Flask
from app.extensions import db, migrate, login_manager, csrf


from app.extensions import login_manager
import app.models

from app.models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app(config_name='development'):
    app = Flask(__name__)

    from config import config
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # imports AFTER init (مهم جدًا)
    from app.routes.auth import auth_bp
    from app.routes.customer import customer_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(customer_bp, url_prefix='/customer')

    with app.app_context():
        db.create_all()

    return app