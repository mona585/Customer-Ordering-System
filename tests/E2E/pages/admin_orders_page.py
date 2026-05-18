class AdminOrdersPage:
    def __init__(self, client):
        self.client = client

    def navigate(self):
        return self.client.get("/admin/orders")

    def update_status(self, order_id, status):
        return self.client.post(f"/admin/orders/{order_id}/status", data={
            "status": status,
        })