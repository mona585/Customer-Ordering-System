class LoginPage:
    def __init__(self, client):
        self.client = client

    def login(self, identifier, password):
        return self.client.post("/auth/login", data={
            "identifier": identifier,
            "password": password,
        })