class AdminMenuPage:
    def __init__(self, client):
        self.client = client

    def navigate(self):
        return self.client.get("/admin/menu")

    def toggle_availability(self, item_id):
        return self.client.post(f"/admin/menu/{item_id}/toggle-availability")