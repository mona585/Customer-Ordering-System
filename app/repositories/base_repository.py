# app/repositories/base_repository.py
"""Base repository with common CRUD operations"""

from app.extensions import db


class BaseRepository:
    """Base class for all repositories"""

    @staticmethod
    def commit():
        """Commit session with rollback on failure"""
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def add(entity):
        db.session.add(entity)
        return entity

    @staticmethod
    def delete(entity):
        db.session.delete(entity)
