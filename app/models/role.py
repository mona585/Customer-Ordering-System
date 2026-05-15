"""Role model and user–role association (many-to-many)."""

from __future__ import annotations

from datetime import datetime

from app.extensions import db


user_role_association = db.Table(
    "user_roles",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    users = db.relationship(
        "User",
        secondary=user_role_association,
        back_populates="roles",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Role {self.slug}>"