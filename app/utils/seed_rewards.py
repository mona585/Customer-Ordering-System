"""Seed test vouchers for checkout and referral testing."""

from datetime import datetime, timedelta

from app.constants.rewards import GLOBAL_PROMO_CODES
from app.models.user import User
from app.services.voucher_service import VoucherService


def seed_test_vouchers():
    """Create sample user vouchers for the test customer (idempotent)."""
    user = User.query.filter_by(email="test@aura.com").first()
    if not user:
        print("⚠️  seed_test_vouchers skipped: test@aura.com not found (run seed_test_user first)")
        return

    samples = [
        {
            "code": "TESTVIP20",
            "discount_percent": 20,
            "min_order_amount": 15,
            "days_valid": 90,
            "source": "seed",
        },
        {
            "code": "LOYAL10",
            "discount_percent": 10,
            "min_order_amount": 0,
            "days_valid": 45,
            "source": "seed",
        },
        {
            "code": "BIGORDER30",
            "discount_percent": 30,
            "min_order_amount": 50,
            "days_valid": 60,
            "source": "seed",
        },
    ]

    created = 0
    for cfg in samples:
        before = VoucherService.issue_voucher(
            user_id=user.id,
            code=cfg["code"],
            discount_percent=cfg["discount_percent"],
            min_order_amount=cfg["min_order_amount"],
            days_valid=cfg["days_valid"],
            source=cfg["source"],
        )
        if before and before.created_at >= datetime.utcnow() - timedelta(seconds=2):
            created += 1

    print(f"✅ Test vouchers ensured for {user.email} ({len(samples)} codes)")


def print_public_promo_codes():
    """Print hardcoded public promo codes for manual testing."""
    print("\n=== Public promo codes (checkout) ===")
    for code, cfg in GLOBAL_PROMO_CODES.items():
        expires = cfg.get("expires_at")
        exp_str = expires.strftime("%Y-%m-%d") if expires else "never"
        print(
            f"  {code}: {cfg['discount_percent']}% off, "
            f"min ${cfg.get('min_order', 0):.2f}, expires {exp_str}"
        )
