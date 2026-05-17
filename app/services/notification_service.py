from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.services.base_service import BaseService, ServiceResult


class NotificationService(BaseService):
    @staticmethod
    def notify(user_id: int, title: str, message: str, category: str = "general") -> None:
        NotificationRepository.create(
            Notification(user_id=user_id, title=title, message=message, category=category)
        )
        NotificationRepository.commit()

    @staticmethod
    def list_notifications(user_id: int) -> ServiceResult:
        items = NotificationRepository.list_for_user(user_id)
        return ServiceResult.ok(data=[n.to_dict() for n in items])

    @staticmethod
    def unread_count(user_id: int) -> ServiceResult:
        return ServiceResult.ok(data={"count": NotificationRepository.unread_count(user_id)})

    @staticmethod
    def mark_read(user_id: int, notification_id: int) -> ServiceResult:
        note = NotificationRepository.get_by_id(notification_id, user_id)
        if not note:
            return ServiceResult.fail("Notification not found")
        note.is_read = True
        NotificationRepository.commit()
        return ServiceResult.ok(message="Marked as read")

    @staticmethod
    def mark_all_read(user_id: int) -> ServiceResult:
        NotificationRepository.mark_all_read(user_id)
        NotificationRepository.commit()
        return ServiceResult.ok(message="All notifications marked as read")
