# app/repositories/user_repository.py

from app.extensions import db
from app.models.user import User


class UserRepository:

    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        # User.query.get() is removed in SQLAlchemy 2.0 — use db.session.get() instead
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_email(email: str) -> User | None:
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_username(username: str) -> User | None:
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_phone(phone: str) -> User | None:
        return User.query.filter_by(phone=phone).first()
    
    @staticmethod
    def create(user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user: User) -> User:
        db.session.commit()
        return user

    @staticmethod
    def delete(user: User) -> None:
        db.session.delete(user)
        db.session.commit()