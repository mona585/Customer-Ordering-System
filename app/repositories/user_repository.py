# app/repositories/user_repository.py

from sqlalchemy.orm import selectinload

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
    def get_by_login_identifier(identifier: str) -> User | None:
        """
        Resolve a User from a single login field (email or username).
        Emails are normalized to lower-case; usernames match as stored (case-sensitive).
        """
        raw = (identifier or "").strip()
        if not raw:
            return None
        if "@" in raw:
            return UserRepository.get_by_email(raw.lower())
        return UserRepository.get_by_username(raw)

    @staticmethod
    def get_by_phone(phone: str) -> User | None:
        return User.query.filter_by(phone=phone).first()
    
    @staticmethod
    def create(user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user_id: int, updates: dict) -> User | None:
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
        return user

    @staticmethod
    def delete(user: User) -> None:
        db.session.delete(user)
        db.session.commit()