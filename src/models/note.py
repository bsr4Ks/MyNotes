import datetime
import uuid

class Note:
    def __init__(self, user, title, content, oid=None):
        self.id = str(uuid.uuid4())
        self.user = user
        self.title = title
        self.content = content
        self.created_at = datetime.datetime.now()

    def __str__(self):
        return f"id:{self.id}, title:{self.title}, content:{self.content} created_at:{self.created_at}"