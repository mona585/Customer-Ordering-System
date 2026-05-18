class NotificationsPage:
    def __init__(self, client):
        self.client = client

    def navigate(self):
        return self.client.get("/notifications")

    def get_unread_count(self):
        return self.client.get("/api/notifications/unread-count")