from app.extensions import db
from app.models.address import UserAddress


class AddressRepository:
    @staticmethod
    def list_for_user(user_id: int) -> list[UserAddress]:
        return (
            UserAddress.query.filter_by(user_id=user_id)
            .order_by(UserAddress.is_default.desc(), UserAddress.id.asc())
            .all()
        )

    @staticmethod
    def get_by_id(address_id: int, user_id: int) -> UserAddress | None:
        return UserAddress.query.filter_by(id=address_id, user_id=user_id).first()

    @staticmethod
    def get_default(user_id: int) -> UserAddress | None:
        return UserAddress.query.filter_by(user_id=user_id, is_default=True).first()

    @staticmethod
    def create(address: UserAddress) -> UserAddress:
        db.session.add(address)
        db.session.flush()
        return address

    @staticmethod
    def clear_default(user_id: int) -> None:
        UserAddress.query.filter_by(user_id=user_id, is_default=True).update({"is_default": False})

    @staticmethod
    def delete(address: UserAddress) -> None:
        db.session.delete(address)

    @staticmethod
    def commit() -> bool:
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
