from datetime import datetime

from app.extensions import db


class UserAddress(db.Model):
    __tablename__ = "user_addresses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    label = db.Column(db.String(50), nullable=False, default="Home")
    street = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100))
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="addresses")

    def formatted(self) -> str:
        parts = [self.street]
        if self.city:
            parts.append(self.city)
        return ", ".join(parts)

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "street": self.street,
            "city": self.city or "",
            "is_default": self.is_default,
            "formatted": self.formatted(),
        }
