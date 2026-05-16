"""Rewards, vouchers, and referral configuration."""

POINTS_PER_DOLLAR = 10

TIER_THRESHOLDS = {
    "Bronze": 0,
    "Silver": 500,
    "Gold": 2000,
}

POINT_REDEMPTION_OPTIONS = [
    {"points": 500, "discount_percent": 10, "min_order": 25, "code_prefix": "PTS10"},
]

WELCOME_VOUCHER = {
    "code": "WELCOME20",
    "discount_percent": 20,
    "min_order_amount": 15,
    "days_valid": 30,
}

REFERRAL_REWARDS = {
    "referrer": {
        "code": "REFER25",
        "discount_percent": 25,
        "min_order_amount": 20,
        "days_valid": 60,
    },
    "referred": {
        "code": "FRIEND15",
        "discount_percent": 15,
        "min_order_amount": 10,
        "days_valid": 30,
    },
}

GLOBAL_PROMO_CODES = {
    "SAVE10": {"discount_percent": 10, "min_order": 0},
    "AURA20": {"discount_percent": 20, "min_order": 30},
}

DELIVERY_FEE = 5.0
TAX_RATE = 0.08
