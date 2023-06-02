import os
import subprocess

import audio.models
from audio import db, app
from flask import current_app
from random import randint
from uuid import uuid4
from werkzeug.utils import secure_filename


class User(db.Model):
    """
    Класс наследуется от модели SQLAlchemy и содержит поля,
    которые затем будут транслироваться в базу данных,
    в таблицу __tablename__
    """
    __tablename__ = 'users'

    id: int = db.Column(db.Integer(), nullable=False, primary_key=True)
    username: str = db.Column(db.String(50), nullable=False, unique=True)
    uuid: str = db.Column(db.String(100), nullable=False, unique=True)
    token: str = db.Column(db.String(36), nullable=False, unique=True)
    audiofiles = db.relationship('AudioFile', backref='owner', lazy=True)

    def __init__(self, username: str) -> None:
        self.username = username
        self.uuid: str = self.__create_uuid()
        self.token: str = uuid4().__str__()

    def __create_uuid(self) -> str:
        """
        Метод создает уникальный идентификатор пользователя.
        Для этого он конкатенирует имя пользователя и строку,
        сформированную из случайных букв латинского алфавита
        :return: str
        """
        uuid: str = ''
        for i in range(len(self.username)):
            if i % 2 == 0:
                uuid += chr(randint(65, 90))
            else:
                uuid += chr(randint(97, 122))
        return self.username + '-' + uuid

    @classmethod
    def get_user(cls, username: str = None, uuid: str = None, token: str = None) -> audio.models.User | bool:
        """
        Метод совершает запрос к базе данных в соответствии с переданными аргументами:
        либо по имени пользователя, либо по токену и идентификатору
        :param username:
        :param uuid:
        :param token:
        :return:
        """
        if username:
            return db.session.execute(db.select(cls).filter_by(username=username)).scalar()
        elif uuid and token:
            return db.session.execute(db.select(cls).filter_by(uuid=uuid, token=token)).scalar()
        else:
            return False


class AudioFile(db.Model):
    """
    Класс наследуется от модели SQLAlchemy и содержит поля,
    которые затем будут транслироваться в базу данных,
    в таблицу __tablename__
    """
    __tablename__ = 'audio_files'

    id: int = db.Column(db.Integer(), nullable=False, primary_key=True)
    filename: str = db.Column(db.String(100), nullable=False)
    file: bytes = db.Column(db.LargeBinary, nullable=False)
    file_uuid: str = db.Column(db.String(36), nullable=False, unique=True)
    user_id: int = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)

    def __init__(self, filename: str, file: bytes, owner: User) -> None:
        self.filename: str = filename
        self.file: bytes = file
        self.file_uuid: str = uuid4().__str__()
        self.user_id: int = owner.id

    @classmethod
    def get_file(cls, file_uuid, user_id) -> audio.models.AudioFile | None:
        ""
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
