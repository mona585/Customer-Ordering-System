class CartPage:
    def __init__(self, client):
        self.client = client

    def add_item(self, item_id, quantity=1):
        return self.client.post("/customer/api/cart/add", json={
            "item_id": item_id,
            "quantity": quantity,
        })

    def apply_promo(self, code):
        return self.client.post("/customer/cart", data={
            "promo_code": code,
        })