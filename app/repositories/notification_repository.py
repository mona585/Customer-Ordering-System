from app.extensions import db
from app.models.notification import Notification


class NotificationRepository:
    @staticmethod
    def list_for_user(user_id: int, limit: int = 50) -> list[Notification]:
        return (
            Notification.query.filter_by(user_id=user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def unread_count(user_id: int) -> int:
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def get_by_id(notification_id: int, user_id: int) -> Notification | None:
        return Notification.query.filter_by(id=notification_id, user_id=user_id).first()

    @staticmethod
    def create(notification: Notification) -> Notification:
        db.session.add(notification)
        db.session.flush()
        return notification

    @staticmethod
    def mark_all_read(user_id: int) -> None:
        Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})

    @staticmethod
    def commit() -> bool:
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
