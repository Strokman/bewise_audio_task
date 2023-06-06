from audio import app, db
from io import BytesIO
from .models import AudioFile, FileProcessor, InvalidAPIUsage, User
from flask import jsonify, request, send_file, Response
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import NotFound


@app.route('/api/register', methods=['POST'])
def register() -> tuple[dict, int]:
    """
    Принимает данные из формы в виде строки с именем пользователя.
    Проверяет, есть ли в базе такой пользователь, если да - возвращает ответ
    с указаением на существование пользователя, также проверяет, не является ли имя пустой строкой.
    В случае успешных проверок - регистрирует нового юзера и возвращает регистрационные данные в формате json.
    :return:
    """
    username: str = request.form['username']
    if username == '':
        raise InvalidAPIUsage('Please provide correct username', status_code=400)
    else:
        user_check: User = User.get_user(username)
        if user_check:
            raise InvalidAPIUsage(f'User {user_check.username} exists', status_code=409)
        else:
            user: User = User(username)
            db.session.add(user)
            db.session.commit()
            return user.as_dict(), 200


@app.route('/api/file', methods=['POST'])
def file() -> tuple[Response, int]:
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
                return jsonify(
                    dict(link=f'{request.host_url}api/record?id={audio_file.file_uuid}&user={audio_file.user_id}')), 200
            except ValueError as e:
                raise InvalidAPIUsage(f'Please submit correct file - {e}', 415)
        else:
            raise InvalidAPIUsage('User not found', 404)
    except KeyError:
        raise InvalidAPIUsage('Please provide correct data: /path/to/file, user uuid, token', 400)


@app.route('/api/record', methods=['GET'])
def record() -> Response | tuple[str, int]:
    """
    Принимает данные из ссылки, если они корректны - запрашивает файл из БД
    и передает его пользователю в байтовом виде (чтобы не сохранять лишний раз
    файл в файловой системе)
    :return:
    """
    err_msg: str = 'Please provide correct link with file_uuid and user_id'
    try:
        file_uuid: str = request.args['id']
        user_id: str = request.args['user']
    except KeyError:
        raise InvalidAPIUsage(err_msg, 400)
    mp3_file: AudioFile = AudioFile.get_file(file_uuid, user_id)
    if mp3_file:
        return_data: BytesIO = BytesIO()
        return_data.write(mp3_file.file)
        return_data.seek(0)
        return send_file(return_data, mimetype='audio/mpeg',
                         download_name=f'{mp3_file.owner.uuid}-{mp3_file.file_uuid}',
                         as_attachment=True)
    else:
        raise InvalidAPIUsage(err_msg, 400)


@app.errorhandler(404)
def resource_not_found(e: NotFound) -> tuple[Response, int]:
    print(type(e))
    return jsonify(error=str(e), description='Please use correct route - http://host:port/api/<route>'), 404


@app.errorhandler(InvalidAPIUsage)
def resource_not_found(e: InvalidAPIUsage) -> tuple[Response, int]:
    return jsonify(e.to_dict()), e.status_code
