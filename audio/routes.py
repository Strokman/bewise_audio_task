import io
import os
import subprocess

from audio import app, db
from .models import User, AudioFile, FileProcessor
from flask import request, send_file, current_app
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename


@app.route('/register', methods=['POST'])
def register():
    username: str = request.form['username']
    if username != '':
        try:
            user = User(username)
            db.session.add(user)
            db.session.commit()
            return f'Please save your register information: {user.uuid=}, {user.token=}\n', 200
        except IntegrityError:
            db.session.close()
            return 'User exists\n', 409
    else:
        return 'Please provide correct username\n', 400


@app.route('/file', methods=['POST'])
def file():
    try:
        user_uuid = request.form['uuid']
        user_token = request.form['token']
        user = User.get_user(uuid=user_uuid, token=user_token)
        if user:
            try:
                wav_file = request.files['file']
                processed_file = FileProcessor(wav_file.filename, wav_file.read())
                audio_file = AudioFile(processed_file.filename, processed_file.file, user)
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
def record():
    err_msg = 'Please provide correct file unique identifier and user id\n'
    try:
        # path = f'{current_app.root_path}/{app.config["UPLOAD_FOLDER"]}/'
        file_uuid = request.args['id']
        user_id = request.args['user']
        wav_file: AudioFile = AudioFile.get_file(file_uuid, user_id)
        if wav_file:
            # filename = os.path.splitext(wav_file.filename)[0] + '.mp3'
            # tmp_file = f'{path}tmp.wav'
            # with open(tmp_file, 'wb') as f:
            #     f.write(wav_file.file)
            # cmd = f'lame --preset insane {tmp_file} {path}{filename}'
            # subprocess.call(cmd, shell=True)
            return_data = io.BytesIO()
            # with open(f'{path}{filename}', 'rb') as fo:
            return_data.write(wav_file.file)
            return_data.seek(0)
            # os.remove(f'{path}{filename}')
            # os.remove(tmp_file)
            return send_file(return_data, mimetype='audio/mpeg', download_name=wav_file.filename, as_attachment=True)
        else:
            return err_msg, 400
    except KeyError:
        return err_msg, 400
