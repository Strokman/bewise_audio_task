from audio import db
from random import randint
from uuid import uuid4


class User(db.Model):
    __tablename__ = 'users'

    id: int = db.Column(db.Integer(), nullable=False, primary_key=True)
    username: str = db.Column(db.String(50), nullable=False, unique=True)
    uuid: str = db.Column(db.String(100), nullable=False, unique=True)
    token: str = db.Column(db.String(36), nullable=False, unique=True)
    audiofiles = db.relationship('AudioFile', backref='owner', lazy=True)

    def __init__(self, username: str) -> None:
        self.username = username
        self.uuid = self.create_uuid()
        self.token = uuid4().__str__()

    def create_uuid(self) -> str:
        uuid = ''
        for i in range(len(self.username)):
            if i % 2 == 0:
                uuid += chr(randint(65, 90))
            else:
                uuid += chr(randint(97, 122))
        return self.username + '-' + uuid

    @classmethod
    def get_user(cls, username=None, uuid=None, token=None):
        if username:
            return cls.query.filter_by(username=username).first()
        elif uuid and token:
            return cls.query.filter_by(uuid=uuid, token=token).first()
        else:
            return False


class AudioFile(db.Model):
    __tablename__ = 'audio_files'

    id: int = db.Column(db.Integer(), nullable=False, primary_key=True)
    filename: str = db.Column(db.String(100), nullable=False)
    file = db.Column(db.LargeBinary, nullable=False)
    file_uuid: str = db.Column(db.String(36), nullable=False, unique=True)
    user_id: int = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)

    def __init__(self, filename, file, owner: User):
        self.filename = filename
        self.file = file
        self.file_uuid = uuid4().__str__()
        self.user_id = owner.id

    @classmethod
    def get_file(cls, file_uuid, user_id):
        return db.session.execute(db.select(cls).filter_by(file_uuid=file_uuid, user_id=user_id)).scalar()
