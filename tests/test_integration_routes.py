"""Integration tests — Flask test client (selected routes)."""

import json


class TestPublicRoutes:
    def test_pages_delivery_slug(self, client):
        response = client.get("/pages/delivery")
        assert response.status_code == 200
        assert b"Delivery" in response.data

    def test_pages_unknown_slug_404(self, client):
        response = client.get("/pages/not-a-real-slug")
        assert response.status_code == 404


class TestCheckoutValidateApi:
    def test_checkout_validate_requires_login(self, client):
        response = client.post(
            "/customer/api/checkout/validate",
            data=json.dumps({"promo_code": "SAVE10"}),
            content_type="application/json",
        )
        assert response.status_code in (302, 401)
