from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(72), nullable=False) # bcrypt hash length
    created_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.created_on = datetime.now()

    def __str__(self):
        return self.name
