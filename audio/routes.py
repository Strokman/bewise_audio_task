from audio import app, db
from io import BytesIO
from .models import User, AudioFile, FileProcessor
from flask import request, send_file, Response
from werkzeug.datastructures import FileStorage


@app.route('/register', methods=['POST'])
def register() -> tuple[str, int]:
    """
    Принимает данные из формы в виде строки с именем пользователя.
    Проверяет, есть ли в базе такой пользователь, если да - возвращает ответ
    с указаением на существование пользователя, также проверяет, не является ли имя пустой строкой.
    В случае успешных проверок - регистрирует нового юзера и возвращает регистрационные данные.
    :return:
    """
    username: str = request.form['username']
    if username == '':
        return 'Please provide correct username\n', 400
    else:
        user_check: User = User.get_user(username)
        if user_check:
            return f'User {user_check.username} exists\n', 409
        else:
            user: User = User(username)
            db.session.add(user)
            db.session.commit()
            return f'Please save your register information: {user.uuid=}, {user.token=}\n', 200


@app.route('/file', methods=['POST'])
def file() -> tuple[str, int]:
    """
    В формах принимает файл, уникальный идентификатор пользователя и
    токен доступа. Проверяет, корректные ли данные были переданы в формах,
    затем проверяет корректность данных (есть ли соответствующий пользователь),
    после чего обрабатывает файл, сохраняет в базе и выдает ссылку на скачивание
    :return:
    """
    try:
        user_uuid: str = request.form['uuid']
        user_token: str = request.form['token']
        user: User = User.get_user(uuid=user_uuid, token=user_token)
        if user:
            try:
                wav_file: FileStorage = request.files['file']
                processed_file: FileProcessor = FileProcessor(wav_file.filename, wav_file.read())
                audio_file: AudioFile = AudioFile(processed_file.filename, processed_file.file, user)
                db.session.add(audio_file)
                db.session.commit()
                return f'Please save the download link for your file - ' \
                       f'{request.host_url}record?id={audio_file.file_uuid}&user={audio_file.user_id}\n', 200
            except ValueError as e:
                return f'Please submit correct file - {e}\n', 400
        else:
            return 'User not found\n', 404
    except KeyError:
        return 'Please provide correct data: /path/to/file, user uuid, token\n', 400


@app.route('/record', methods=['GET'])
def record() -> Response | tuple[str, int]:
    """
    Принимает данные из ссылки, если они корректны - запрашивает файл из БД
    и передает его пользователю в байтовом виде (чтобы не сохранять лишний раз
    файл в файловой системе)
    :return:
    """
    err_msg: str = 'Please provide correct file_uuid and user_id\n'
    try:
        file_uuid: str = request.args['id']
        user_id: str = request.args['user']
        mp3_file: AudioFile = AudioFile.get_file(file_uuid, user_id)
        if mp3_file:
            return_data: BytesIO = BytesIO()
            return_data.write(mp3_file.file)
            return_data.seek(0)
            return send_file(return_data, mimetype='audio/mpeg',
                             download_name=f'{mp3_file.owner.uuid}-{mp3_file.file_uuid}',
                             as_attachment=True)
        else:
            return err_msg, 400
    except KeyError:
        return err_msg, 400
