"""Unit tests — card_validation (Luhn, expiry, CVV)."""

from app.services.card_validation import luhn_check, validate_card_submission


class TestLuhnCheck:
    def test_valid_visa_test_number(self):
        assert luhn_check("4111111111111111") is True

    def test_invalid_number_fails(self):
        assert luhn_check("4111111111111112") is False

    def test_too_short_fails(self):
        assert luhn_check("411111") is False


class TestValidateCardSubmission:
    def test_valid_submission(self):
        ok, err, month, year = validate_card_submission(
            "4111111111111111",
            "12/30",
            "123",
            "Jane Doe",
        )
        assert ok is True
        assert err is None
        assert month == 12
        assert year == 2030

    def test_cvv_must_be_three_or_four_digits(self):
        ok, err, _, _ = validate_card_submission(
            "4111111111111111",
            "12/30",
            "12",
            "Jane Doe",
        )
        assert ok is False
        assert "cvv" in err.lower()

    def test_expired_card_rejected(self):
        ok, err, _, _ = validate_card_submission(
            "4111111111111111",
            "01/20",
            "123",
            "Jane Doe",
        )
        assert ok is False
        assert "expired" in err.lower()
