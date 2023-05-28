from audio import db
from datetime import datetime
from uuid import uuid4
from random import randint


class User(db.Model):
    __tablename__ = 'users'

    id: int = db.Column(db.Integer(), nullable=False, primary_key=True)
    username: str = db.Column(db.String(50), nullable=False)
    uuid: str = db.Column(db.String(50), nullable=False, unique=True)
    token: str = db.Column(db.String(36), nullable=False)

    def __init__(self, username: str) -> None:
        self.username = username
        self.uuid = self.create_uuid()
        self.token = uuid4()

    def create_uuid(self) -> str:
        uuid = self.usernanem + '-'
        for i in self.username:
            if ord(i) % 2 == 0:
                uuid += str(randint(1, 10))
            else:
                uuid += chr(ord(i) + randint(1, 15))
        return uuid
