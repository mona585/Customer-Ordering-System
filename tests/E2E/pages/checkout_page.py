class CheckoutPage:
    def __init__(self, client):
        self.client = client

    def place_order(self, address):
        return self.client.post("/customer/checkout", data={
            "delivery_address": address,
        })