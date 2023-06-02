from os import path, remove
from subprocess import call

from audio import db, app
from flask import current_app
from random import randint
from uuid import uuid4
from werkzeug.utils import secure_filename


class User(db.Model):
    """
    Класс наследуется от модели SQLAlchemy и содержит поля,
    которые затем будут транслироваться в базу данных,
    в таблицу хранения данных пользователей
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
    def get_user(cls, username: str = None, uuid: str = None, token: str = None):
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
    в таблицу, где будут хранится файлы
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
    def get_file(cls, file_uuid, user_id):
        """
        Метод делает запрос к базе данных по идентификатору файла
        и id пользователя, возвращает экземпляр класса с необходимым файлом,
        либо None
        :param file_uuid:
        :param user_id:
        :return:
        """
        return db.session.execute(db.select(cls).filter_by(file_uuid=file_uuid, user_id=user_id)).scalar()


class FileProcessor:
    """
    Класс обрабатывает входящие файлы. Проверяет название файла на допустимость (.wav),
    сохраняет в файловой системе в папке static, конвертирует утилитой lame
    в mp3, сохраняет данные в атрибуты класса
    """
    def __init__(self, filename, file: bytes) -> None:
        self.filename = filename
        self.file = file

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, value: str):
        filename = secure_filename(value)
        file_ext: str = path.splitext(filename)[1]
        if filename != '' and file_ext.lower() in app.config['ALLOWED_EXTENSIONS']:
            mp3_filename = f'{path.splitext(filename)[0]}.mp3'
            self._filename = mp3_filename
        else:
            raise ValueError('File format is not allowed')

    @property
    def file(self) -> bytes:
        return self._file

    @file.setter
    def file(self, raw_file: bytes) -> None:
        path_to_static: str = f'{current_app.root_path}/{app.config["UPLOAD_FOLDER"]}/'
        tmp_file: str = f'{path_to_static}tmp.wav'
        with open(tmp_file, 'wb') as f:
            f.write(raw_file)
        cmd: str = f'lame --preset insane {tmp_file} {path_to_static}{self.filename}'
        call(cmd, shell=True)
        with open(f'{path_to_static}{self.filename}', 'rb') as f:
            self._file = f.read()
        remove(f'{path_to_static}{self.filename}')
        remove(tmp_file)
