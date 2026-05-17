"""Password policy — sequence detection."""

from app.security.password_policy import validate_password_strength


def test_aura_password_allowed():
    assert validate_password_strength("Aura@12345", username="demo", email="demo@test.com") is None


def test_long_numeric_sequence_rejected():
    err = validate_password_strength("Aura@123456", username="demo", email="demo@test.com")
    assert err is not None
    assert "sequence" in err.lower()
