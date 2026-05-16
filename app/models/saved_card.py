from datetime import datetime

from app.extensions import db


class SavedCard(db.Model):
    __tablename__ = "saved_cards"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    last_four = db.Column(db.String(4), nullable=False)
    brand = db.Column(db.String(30), nullable=False)
    exp_month = db.Column(db.Integer, nullable=False)
    exp_year = db.Column(db.Integer, nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="saved_cards")

    def masked_display(self) -> str:
        return f"{self.brand} •••• {self.last_four}"

    def to_dict(self):
        return {
            "id": self.id,
            "last_four": self.last_four,
            "brand": self.brand,
            "exp_month": self.exp_month,
            "exp_year": self.exp_year,
            "is_default": self.is_default,
            "masked_display": self.masked_display(),
        }
