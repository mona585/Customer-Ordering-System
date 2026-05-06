# app/services/base_service.py
"""Base service with standardized error handling and responses"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ServiceResult:
    """Standardized service response"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    message: Optional[str] = None

    @classmethod
    def ok(cls, data=None, message=None):
        return cls(success=True, data=data, message=message)

    @classmethod
    def fail(cls, error, data=None):
        return cls(success=False, error=error, data=data)


class BaseService:
    """Base class for all services with transaction handling"""

    @staticmethod
    def _commit_or_rollback(session, on_success_msg=None):
        """Helper to commit with rollback on failure"""
        from app.extensions import db
        try:
            db.session.commit()
            return ServiceResult.ok(message=on_success_msg)
        except Exception as e:
            db.session.rollback()
            return ServiceResult.fail(f"Database error: {str(e)}")
