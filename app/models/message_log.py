from datetime import datetime
from app.extensions import db

class MessageLog(db.Model):
    __tablename__ = "message_log"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String(250), nullable=False)

    def __init__(self, message):
        self.date = datetime.now()
        self.message = message
