import uuid

class User:
    def __init__(self, username, password_hash):
        self.id = str(uuid.uuid4())
        self.username = username
        self.password_hash = password_hash
