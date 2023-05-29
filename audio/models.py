from audio import db
from datetime import datetime
from uuid import uuid4
from random import randint


class User(db.Model):
    __tablename__ = 'users'

    id: int = db.Column(db.Integer(), nullable=False, primary_key=True)
    username: str = db.Column(db.String(50), nullable=False)
    uuid: str = db.Column(db.String(50), nullable=False, unique=True)
    token: str = db.Column(db.String(36), nullable=False, unique=True)
    files = db.relationship('AudioFile', backref='users', lazy=True)

    def __init__(self, username: str) -> None:
        self.username = username
        self.uuid = self.create_uuid()
        self.token = uuid4().__str__()

    def create_uuid(self) -> str:
        uuid = ''
        for i in self.username:
            if ord(i) % 2 == 0:
                uuid += str(randint(1, 10))
            else:
                uuid += chr(ord(i) + randint(1, 15))
        return self.username + '-' + uuid

    @staticmethod
    def check_user_exists(username: str):
        return db.session.execute(db.select(User).filter_by(username=username)).scalar()


class AudioFile(db.Model):
    __tablename__ = 'audio_files'

    id: int = db.Column(db.Integer(), nullable=False, primary_key=True)
    token: str = db.Column(db.String(36), nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)