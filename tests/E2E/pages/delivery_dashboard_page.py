class DeliveryDashboardPage:
    def __init__(self, client):
        self.client = client

    def navigate(self):
        return self.client.get("/delivery/")

    def advance_status(self, order_id):
        return self.client.post(f"/delivery/orders/{order_id}/status")
    