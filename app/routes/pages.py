"""Static informational pages linked from the site footer."""

from flask import Blueprint, abort, render_template

pages_bp = Blueprint("pages", __name__, url_prefix="/pages")

PAGE_CONTENT = {
    "delivery": {
        "title": "Delivery & Returns",
        "subtitle": "How we deliver your order and what to do if something goes wrong.",
        "sections": [
            {
                "heading": "Delivery areas & timing",
                "body": (
                    "We deliver within our service area from the restaurant. Typical delivery "
                    "times are 30–45 minutes depending on distance and order volume. You can "
                    "track your order from the order confirmation page."
                ),
            },
            {
                "heading": "Delivery fees",
                "body": (
                    "A small delivery fee may apply to your order. Free delivery may be available "
                    "when your cart reaches the minimum shown at checkout."
                ),
            },
            {
                "heading": "Returns & refunds",
                "body": (
                    "If an item is missing, incorrect, or not up to standard, contact us within "
                    "24 hours with your order number. We will review each case and offer a "
                    "replacement, credit, or refund where appropriate."
                ),
            },
        ],
    },
    "contact": {
        "title": "Contact Us",
        "subtitle": "We're here to help with orders, account questions, and feedback.",
        "sections": [
            {
                "heading": "Customer support",
                "body": "Email: support@aura-restaurant.example\nPhone: +20 100 000 0000\nHours: Daily 10:00 – 22:00",
            },
            {
                "heading": "Restaurant",
                "body": "AURA Restaurant\n123 Flavor Street\nCairo, Egypt",
            },
            {
                "heading": "Order issues",
                "body": (
                    "For active orders, include your order ID from My Orders so we can assist "
                    "you faster."
                ),
            },
        ],
    },
    "faq": {
        "title": "FAQ",
        "subtitle": "Quick answers to common questions.",
        "sections": [
            {
                "heading": "How do I place an order?",
                "body": "Browse the menu, add items to your cart, and complete checkout with your delivery address and payment method.",
            },
            {
                "heading": "Can I change or cancel an order?",
                "body": "You may cancel while the order is still pending or confirmed. After preparation starts, changes may not be possible.",
            },
            {
                "heading": "Which payment methods are accepted?",
                "body": "We accept saved credit cards and cash on delivery where available.",
            },
            {
                "heading": "How do vouchers and promo codes work?",
                "body": "Enter a promo code or select a voucher at checkout. Each offer has its own minimum order and expiry rules.",
            },
        ],
    },
    "ordering-guide": {
        "title": "Ordering Guide",
        "subtitle": "Tips for a smooth experience from menu to doorstep.",
        "sections": [
            {
                "heading": "Create an account",
                "body": "Register to save addresses, payment cards, wishlists, and order history.",
            },
            {
                "heading": "Save addresses & cards",
                "body": "Manage delivery addresses and cards from your profile for faster checkout.",
            },
            {
                "heading": "Track your order",
                "body": "Open My Orders and select an order to see live status updates.",
            },
        ],
    },
    "privacy": {
        "title": "Privacy Policy",
        "subtitle": "How we collect, use, and protect your information.",
        "sections": [
            {
                "heading": "Information we collect",
                "body": "We collect account details, order history, delivery addresses, and payment metadata needed to fulfill orders.",
            },
            {
                "heading": "How we use it",
                "body": "Data is used to process orders, improve our service, and communicate about your account or deliveries.",
            },
            {
                "heading": "Your choices",
                "body": "You may update profile information at any time. Contact us to request account deletion where applicable.",
            },
        ],
    },
    "terms": {
        "title": "Terms of Service",
        "subtitle": "Terms for using the AURA ordering platform.",
        "sections": [
            {
                "heading": "Using the service",
                "body": "You agree to provide accurate information and use the platform only for lawful personal orders.",
            },
            {
                "heading": "Pricing & availability",
                "body": "Menu items, prices, and availability may change. Confirmed orders are subject to stock at preparation time.",
            },
            {
                "heading": "Liability",
                "body": "Our liability is limited to the value of the affected order except where law requires otherwise.",
            },
        ],
    },
    "cookies": {
        "title": "Cookie Policy",
        "subtitle": "How cookies and similar technologies are used on this site.",
        "sections": [
            {
                "heading": "Essential cookies",
                "body": "Required for login sessions, cart state, and security (including CSRF protection).",
            },
            {
                "heading": "Preferences",
                "body": "We store your theme preference (light/dark) in local storage on your device.",
            },
            {
                "heading": "Managing cookies",
                "body": "You can clear cookies via your browser settings. Some features may not work without essential cookies.",
            },
        ],
    },
}


@pages_bp.route("/<slug>")
def info_page(slug: str):
    page = PAGE_CONTENT.get(slug)
    if not page:
        abort(404)
    return render_template("pages/info.html", slug=slug, page=page)
