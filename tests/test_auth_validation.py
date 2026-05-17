"""Unit tests — REQ-AUTH-01, REQ-AUTH-02 registration validation."""

from app.routes.auth import _validate_phone, _validate_registration


class TestValidateRegistration:
    def test_valid_fields_return_none(self):
        assert _validate_registration("alice", "alice@example.com", "password1") is None

    def test_short_username_rejected(self):
        err = _validate_registration("ab", "alice@example.com", "password1")
        assert err is not None
        assert "username" in err.lower()

    def test_short_password_rejected(self):
        err = _validate_registration("alice", "alice@example.com", "short")
        assert err is not None
        assert "8" in err


class TestValidatePhone:
    def test_valid_e164(self):
        assert _validate_phone("+201012345678") is None

    def test_invalid_format(self):
        err = _validate_phone("01012345678")
        assert err is not None
