class OrderTrackingPage:
    def __init__(self, client):
        self.client = client

    def navigate(self, order_id):
        return self.client.get(f"/order/order/{order_id}/track")