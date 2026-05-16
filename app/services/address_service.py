from app.models.address import UserAddress
from app.repositories.address_repository import AddressRepository
from app.repositories.user_repository import UserRepository
from app.services.base_service import BaseService, ServiceResult


class AddressService(BaseService):
    @staticmethod
    def list_addresses(user_id: int) -> ServiceResult:
        addresses = AddressRepository.list_for_user(user_id)
        return ServiceResult.ok(data=[a.to_dict() for a in addresses])

    @staticmethod
    def create_address(user_id: int, label: str, street: str, city: str = "", set_default: bool = False) -> ServiceResult:
        if not street or not street.strip():
            return ServiceResult.fail("Street address is required")
        label = (label or "Home").strip()[:50]
        is_first = not AddressRepository.list_for_user(user_id)
        if is_first:
            set_default = True
        if set_default:
            AddressRepository.clear_default(user_id)
        addr = UserAddress(
            user_id=user_id,
            label=label,
            street=street.strip(),
            city=(city or "").strip(),
            is_default=set_default or is_first,
        )
        AddressRepository.create(addr)
        if addr.is_default:
            UserRepository.update(user_id, {"address": addr.formatted()})
        if AddressRepository.commit():
            return ServiceResult.ok(data=addr.to_dict(), message="Address saved")
        return ServiceResult.fail("Could not save address")

    @staticmethod
    def update_address(user_id: int, address_id: int, **fields) -> ServiceResult:
        addr = AddressRepository.get_by_id(address_id, user_id)
        if not addr:
            return ServiceResult.fail("Address not found")
        if "label" in fields and fields["label"]:
            addr.label = fields["label"].strip()[:50]
        if "street" in fields and fields["street"]:
            addr.street = fields["street"].strip()
        if "city" in fields:
            addr.city = (fields["city"] or "").strip()
        if addr.is_default:
            UserRepository.update(user_id, {"address": addr.formatted()})
        if AddressRepository.commit():
            return ServiceResult.ok(data=addr.to_dict(), message="Address updated")
        return ServiceResult.fail("Could not update address")

    @staticmethod
    def set_default(user_id: int, address_id: int) -> ServiceResult:
        addr = AddressRepository.get_by_id(address_id, user_id)
        if not addr:
            return ServiceResult.fail("Address not found")
        AddressRepository.clear_default(user_id)
        addr.is_default = True
        UserRepository.update(user_id, {"address": addr.formatted()})
        if AddressRepository.commit():
            return ServiceResult.ok(data=addr.to_dict(), message="Default address updated")
        return ServiceResult.fail("Could not set default address")

    @staticmethod
    def delete_address(user_id: int, address_id: int) -> ServiceResult:
        addr = AddressRepository.get_by_id(address_id, user_id)
        if not addr:
            return ServiceResult.fail("Address not found")
        was_default = addr.is_default
        AddressRepository.delete(addr)
        if AddressRepository.commit():
            if was_default:
                remaining = AddressRepository.list_for_user(user_id)
                if remaining:
                    AddressRepository.clear_default(user_id)
                    remaining[0].is_default = True
                    UserRepository.update(user_id, {"address": remaining[0].formatted()})
                    AddressRepository.commit()
                else:
                    UserRepository.update(user_id, {"address": None})
            return ServiceResult.ok(message="Address deleted")
        return ServiceResult.fail("Could not delete address")

    @staticmethod
    def get_default_formatted(user_id: int) -> str:
        default = AddressRepository.get_default(user_id)
        if default:
            return default.formatted()
        user = UserRepository.get_by_id(user_id)
        return (user.address or "") if user else ""
