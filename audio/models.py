import os
import subprocess

from audio import db, app
from flask import current_app
from random import randint
from uuid import uuid4
from werkzeug.utils import secure_filename


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
            return db.session.execute(db.select(cls).filter_by(username=username)).scalar()
        elif uuid and token:
            return db.session.execute(db.select(cls).filter_by(uuid=uuid, token=token)).scalar()
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


class FileProcessor:
    def __init__(self, filename, file: bytes):
        self.filename = filename
        self.file = file

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        filename = secure_filename(value)
        file_ext: str = os.path.splitext(filename)[1]
        if filename != '' and file_ext.lower() in app.config['ALLOWED_EXTENSIONS']:
            mp3_filename = f'{os.path.splitext(filename)[0]}.mp3'
            self._filename = mp3_filename
        else:
            raise ValueError('File format is not allowed')

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, raw_file):
        path = f'{current_app.root_path}/{app.config["UPLOAD_FOLDER"]}/'
        tmp_file = f'{path}tmp.wav'
        with open(tmp_file, 'wb') as f:
            f.write(raw_file)
        cmd = f'lame --preset insane {tmp_file} {path}{self.filename}'
        subprocess.call(cmd, shell=True)
        with open(f'{path}{self.filename}', 'rb') as f:
            self._file = f.read()
        os.remove(f'{path}{self.filename}')
        os.remove(tmp_file)
