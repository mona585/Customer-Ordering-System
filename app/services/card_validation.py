"""Client-side-style card checks before tokenized storage (demo; no full PAN stored)."""

from __future__ import annotations

from datetime import datetime


def luhn_check(card_number: str) -> bool:
    digits = [int(c) for c in card_number if c.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse = digits[::-1]
    for i, d in enumerate(reverse):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def parse_expiry(expiry_raw: str) -> tuple[int, int] | None:
    """Parse MM/YY or MM/YYYY."""
    raw = (expiry_raw or "").strip().replace(" ", "")
    if "/" not in raw:
        return None
    parts = raw.split("/", 1)
    if len(parts) != 2:
        return None
    try:
        month = int(parts[0])
        year_part = int(parts[1])
    except ValueError:
        return None
    if not (1 <= month <= 12):
        return None
    if year_part < 100:
        year = 2000 + year_part
    else:
        year = year_part
    return month, year


def validate_card_submission(
    card_number: str,
    expiry_raw: str,
    cvv: str,
    cardholder_name: str,
) -> tuple[bool, str | None, int | None, int | None]:
    name = (cardholder_name or "").strip()
    if len(name) < 2:
        return False, "Cardholder name is required.", None, None

    digits = "".join(c for c in (card_number or "") if c.isdigit())
    if len(digits) < 13:
        return False, "Invalid card number.", None, None
    if not luhn_check(digits):
        return False, "Card number failed verification. Check the digits and try again.", None, None

    parsed = parse_expiry(expiry_raw)
    if not parsed:
        return False, "Invalid expiry date. Use MM/YY format.", None, None
    exp_month, exp_year = parsed

    now = datetime.utcnow()
    if exp_year < now.year or (exp_year == now.year and exp_month < now.month):
        return False, "This card has expired.", None, None

    cvv_digits = "".join(c for c in (cvv or "") if c.isdigit())
    if len(cvv_digits) not in (3, 4):
        return False, "Invalid CVV. Enter 3 or 4 digits.", None, None

    return True, None, exp_month, exp_year
