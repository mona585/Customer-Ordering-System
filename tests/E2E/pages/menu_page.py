class MenuPage:
    def __init__(self, client):
        self.client = client

    def navigate(self):
        return self.client.get("/customer/menu")