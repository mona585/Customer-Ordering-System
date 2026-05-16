from datetime import datetime

from app.extensions import db
from app.models.voucher import UserVoucher


class VoucherRepository:
    @staticmethod
    def list_active_for_user(user_id: int) -> list[UserVoucher]:
        now = datetime.utcnow()
        return (
            UserVoucher.query.filter_by(user_id=user_id, is_used=False)
            .filter(UserVoucher.expires_at > now)
            .order_by(UserVoucher.expires_at.asc())
            .all()
        )

    @staticmethod
    def list_all_for_user(user_id: int) -> list[UserVoucher]:
        return UserVoucher.query.filter_by(user_id=user_id).order_by(UserVoucher.created_at.desc()).all()

    @staticmethod
    def get_by_id(voucher_id: int, user_id: int) -> UserVoucher | None:
        return UserVoucher.query.filter_by(id=voucher_id, user_id=user_id).first()

    @staticmethod
    def get_by_code(user_id: int, code: str) -> UserVoucher | None:
        return UserVoucher.query.filter_by(user_id=user_id, code=code.upper()).first()

    @staticmethod
    def create(voucher: UserVoucher) -> UserVoucher:
        db.session.add(voucher)
        db.session.flush()
        return voucher

    @staticmethod
    def commit() -> bool:
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
