from app.extensions import db
from app.models.referral import Referral
from app.models.user import User


class ReferralRepository:
    @staticmethod
    def get_by_referred(referred_id: int) -> Referral | None:
        return Referral.query.filter_by(referred_id=referred_id).first()

    @staticmethod
    def get_by_referrer_stats(referrer_id: int) -> dict:
        confirmed = Referral.query.filter_by(referrer_id=referrer_id, status="confirmed").count()
        pending = Referral.query.filter_by(referrer_id=referrer_id, status="pending").count()
        return {"referral_count": confirmed, "pending_referrals": pending}

    @staticmethod
    def find_user_by_referral_code(code: str) -> User | None:
        if not code:
            return None
        return User.query.filter_by(referral_code=code.strip().upper()).first()

    @staticmethod
    def create(referral: Referral) -> Referral:
        db.session.add(referral)
        db.session.flush()
        return referral

    @staticmethod
    def commit() -> bool:
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
