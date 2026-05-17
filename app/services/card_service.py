from datetime import datetime

from app.models.saved_card import SavedCard
from app.repositories.card_repository import CardRepository
from app.services.base_service import BaseService, ServiceResult
from app.services.card_validation import luhn_check, parse_expiry, validate_card_submission

def _detect_brand(card_number: str) -> str:
    if card_number.startswith("4"):
        return "Visa"
    if card_number.startswith(("51", "52", "53", "54", "55")) or card_number.startswith("2"):
        return "Mastercard"
    if card_number.startswith(("34", "37")):
        return "Amex"
    return "Card"


class CardService(BaseService):
    @staticmethod
    def list_cards(user_id: int) -> ServiceResult:
        cards = CardRepository.list_for_user(user_id)
        return ServiceResult.ok(data=[c.to_dict() for c in cards])

    @staticmethod
    def add_card(
        user_id: int,
        card_number: str,
        exp_month: int | None = None,
        exp_year: int | None = None,
        set_default: bool = False,
        expiry_raw: str | None = None,
        cvv: str | None = None,
        cardholder_name: str | None = None,
    ) -> ServiceResult:
        if expiry_raw is not None:
            ok, err, exp_month, exp_year = validate_card_submission(
                card_number, expiry_raw, cvv or "", cardholder_name or ""
            )
            if not ok:
                return ServiceResult.fail(err)
        else:
            if not (cardholder_name or "").strip():
                return ServiceResult.fail("Cardholder name is required.")
            digits = "".join(c for c in (card_number or "") if c.isdigit())
            if not luhn_check(digits):
                return ServiceResult.fail("Invalid card number.")
            if exp_month is None or exp_year is None:
                return ServiceResult.fail("Expiration date is required.")
            now = datetime.utcnow()
            if exp_year < now.year or (exp_year == now.year and exp_month < now.month):
                return ServiceResult.fail("This card has expired.")

        digits = "".join(c for c in (card_number or "") if c.isdigit())
        if not (1 <= exp_month <= 12):
            return ServiceResult.fail("Invalid expiration month")
        is_first = not CardRepository.list_for_user(user_id)
        if is_first:
            set_default = True
        if set_default:
            CardRepository.clear_default(user_id)

        card = SavedCard(
            user_id=user_id,
            last_four=digits[-4:],
            brand=_detect_brand(digits),
            exp_month=exp_month,
            exp_year=exp_year,
            is_default=set_default or is_first,
        )
        CardRepository.create(card)
        if CardRepository.commit():
            return ServiceResult.ok(data=card.to_dict(), message="Card saved securely")
        return ServiceResult.fail("Could not save card")

    @staticmethod
    def set_default(user_id: int, card_id: int) -> ServiceResult:
        card = CardRepository.get_by_id(card_id, user_id)
        if not card:
            return ServiceResult.fail("Card not found")
        CardRepository.clear_default(user_id)
        card.is_default = True
        if CardRepository.commit():
            return ServiceResult.ok(data=card.to_dict(), message="Default card updated")
        return ServiceResult.fail("Could not update default card")

    @staticmethod
    def get_card_for_user(user_id: int, card_id: int) -> SavedCard | None:
        return CardRepository.get_by_id(card_id, user_id)

    @staticmethod
    def delete_card(user_id: int, card_id: int) -> ServiceResult:
        card = CardRepository.get_by_id(card_id, user_id)
        if not card:
            return ServiceResult.fail("Card not found")
        was_default = card.is_default
        CardRepository.delete(card)
        if CardRepository.commit():
            if was_default:
                remaining = CardRepository.list_for_user(user_id)
                if remaining:
                    CardRepository.clear_default(user_id)
                    remaining[0].is_default = True
                    CardRepository.commit()
            return ServiceResult.ok(message="Card removed")
        return ServiceResult.fail("Could not remove card")
