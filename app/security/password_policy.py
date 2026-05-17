"""Password strength rules for registration and password changes."""

from __future__ import annotations

import re

MIN_LENGTH = 8
MAX_LENGTH = 128

_SPECIAL_RE = re.compile(r'[!@#$%^&*()_+\-=\[\]{}|;:\'",.<>?/\\`~]')

_COMMON_PASSWORDS = frozenset({
    "password",
    "password1",
    "password12",
    "password123",
    "12345678",
    "123456789",
    "1234567890",
    "qwerty",
    "qwerty123",
    "qwertyuiop",
    "admin",
    "admin123",
    "letmein",
    "welcome",
    "welcome1",
    "iloveyou",
    "monkey",
    "dragon",
    "master",
    "sunshine",
    "princess",
    "football",
    "shadow",
    "abc123",
    "11111111",
    "00000000",
    "aura",
    "aura123",
    "customer",
    "test1234",
    "changeme",
})

_SEQUENCES = (
    "0123456789",
    "9876543210",
    "abcdefghijklmnopqrstuvwxyz",
    "zyxwvutsrqponmlkjihgfedcba",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
)


def password_requirements_hint() -> str:
    return (
        "Use at least 8 characters including uppercase, lowercase, a number, "
        "and a special character (!@#$…). Avoid common passwords and your username/email."
    )


def validate_password_strength(
    password: str,
    *,
    username: str = "",
    email: str = "",
) -> str | None:
    """Return an error message, or None if the password meets policy."""
    if not password:
        return "Password is required."

    if len(password) < MIN_LENGTH:
        return f"Password must be at least {MIN_LENGTH} characters."
    if len(password) > MAX_LENGTH:
        return f"Password must be at most {MAX_LENGTH} characters."
    if re.search(r"\s", password):
        return "Password cannot contain spaces."
    if not re.search(r"[A-Z]", password):
        return "Password must include at least one uppercase letter (A–Z)."
    if not re.search(r"[a-z]", password):
        return "Password must include at least one lowercase letter (a–z)."
    if not re.search(r"\d", password):
        return "Password must include at least one number."
    if not _SPECIAL_RE.search(password):
        return "Password must include at least one special character (e.g. ! @ # $ %)."

    lowered = password.lower()
    if lowered in _COMMON_PASSWORDS:
        return "This password is too common. Choose a stronger, unique password."

    if re.search(r"(.)\1{3,}", password):
        return "Password cannot contain four or more identical characters in a row."

    if _contains_simple_sequence(lowered):
        return "Password cannot be a simple keyboard or numeric sequence."

    uname = (username or "").strip().lower()
    if len(uname) >= 3 and uname in lowered:
        return "Password cannot contain your username."

    if email:
        local = email.split("@", 1)[0].strip().lower()
        if len(local) >= 3 and local in lowered:
            return "Password cannot contain part of your email address."

    return None


def _contains_simple_sequence(lower_password: str) -> bool:
    for seq in _SEQUENCES:
        for i in range(len(seq) - 3):
            if seq[i : i + 4] in lower_password:
                return True
    return False
