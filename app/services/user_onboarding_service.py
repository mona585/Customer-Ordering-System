"""Post-registration setup: referral code, welcome voucher, legacy address migration."""

from app.models.address import UserAddress
from app.repositories.address_repository import AddressRepository
from app.services.referral_service import ReferralService
from app.services.voucher_service import VoucherService


class UserOnboardingService:
    @staticmethod
    def setup_new_customer(user, referral_code: str | None = None) -> None:
        ReferralService.generate_referral_code(user)
        VoucherService.grant_welcome_voucher(user.id)
        if user.address and user.address.strip():
            addr = UserAddress(
                user_id=user.id,
                label="Home",
                street=user.address.strip(),
                is_default=True,
            )
            AddressRepository.create(addr)
            AddressRepository.commit()
        if referral_code:
            ReferralService.link_on_registration(user, referral_code)
