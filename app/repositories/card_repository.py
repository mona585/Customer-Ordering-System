from app.extensions import db
from app.models.saved_card import SavedCard


class CardRepository:
    @staticmethod
    def list_for_user(user_id: int) -> list[SavedCard]:
        return (
            SavedCard.query.filter_by(user_id=user_id)
            .order_by(SavedCard.is_default.desc(), SavedCard.id.asc())
            .all()
        )

    @staticmethod
    def get_by_id(card_id: int, user_id: int) -> SavedCard | None:
        return SavedCard.query.filter_by(id=card_id, user_id=user_id).first()

    @staticmethod
    def get_default(user_id: int) -> SavedCard | None:
        return SavedCard.query.filter_by(user_id=user_id, is_default=True).first()

    @staticmethod
    def create(card: SavedCard) -> SavedCard:
        db.session.add(card)
        db.session.flush()
        return card

    @staticmethod
    def clear_default(user_id: int) -> None:
        SavedCard.query.filter_by(user_id=user_id, is_default=True).update({"is_default": False})

    @staticmethod
    def delete(card: SavedCard) -> None:
        db.session.delete(card)

    @staticmethod
    def commit() -> bool:
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
