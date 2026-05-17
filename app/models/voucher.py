from datetime import datetime

from app.extensions import db


class UserVoucher(db.Model):
    __tablename__ = "user_vouchers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code = db.Column(db.String(32), nullable=False)
    discount_percent = db.Column(db.Integer, nullable=False)
    min_order_amount = db.Column(db.Numeric(10, 2), default=0)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    source = db.Column(db.String(50), default="manual")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="vouchers")

    def is_active(self) -> bool:
        if self.is_used:
            return False
        return datetime.utcnow() < self.expires_at

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "discount_percent": self.discount_percent,
            "min_order_amount": float(self.min_order_amount or 0),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_used": self.is_used,
            "source": self.source,
            "is_active": self.is_active(),
        }
