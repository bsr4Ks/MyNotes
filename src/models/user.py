from flask_login import UserMixin
import uuid

class User(UserMixin):
    def __init__(self, username, password_hash):
        self.id = str(uuid.uuid4())
        self.username = username
        self.password_hash = password_hash
