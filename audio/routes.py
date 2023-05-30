from audio import app, db
from flask import request, send_file, current_app
from werkzeug.utils import secure_filename
from .models import User, AudioFile
from pydub import AudioSegment
from sqlalchemy.exc import IntegrityError
import os
import io


@app.route('/register', methods=['POST'])
def register():
    username: str = request.form['username']
    if username != '':
        try:
            user = User(username)
            db.session.add(user)
            db.session.flush()
            db.session.commit()
            return f'Please save your register information: {user.uuid=}, {user.token=}\n', 200
        except IntegrityError:
            return 'User exists\n', 409
    else:
        return 'Please provide correct username\n', 400


@app.route('/file', methods=['POST'])
def file():
    try:
        wav_file = request.files['file']
        user_uuid = request.form['uuid']
        user_token = request.form['token']
        if User.get_user(uuid=user_uuid, token=user_token):
            filename = secure_filename(wav_file.filename)
            file_ext: str = os.path.splitext(filename)[1]
            if filename != '' and file_ext.lower() in app.config['ALLOWED_EXTENSIONS']:
                audio_file = AudioFile(filename, wav_file.read(), user_uuid)
                db.session.add(audio_file)
                db.session.flush()
                db.session.commit()
                return f'Please save the download link for your file - ' \
                       f'http://localhost:5000/record?id={audio_file.file_uuid}&user={audio_file.user_uuid}\n', 200
            else:
                return 'Please submit correct file\n', 400
        else:
            return 'User not found\n', 404
    except KeyError:
        return 'Please provide correct data: /path/to/file, user uuid, token\n', 400


@app.route('/record', methods=['GET'])
def record():
    err_msg = 'Please provide correct file unique identifier and access token\n'
    try:
        path = f'{current_app.root_path}/{app.config["UPLOAD_FOLDER"]}/'
        file_uuid = request.args['id']
        user_uuid = request.args['user']
        wav_file: AudioFile = AudioFile.get_file(file_uuid, user_uuid)
        if wav_file:
            filename = os.path.splitext(wav_file.filename)[0] + '.mp3'
            tmp_file = f'{path}/tmp.wav'
            with open(tmp_file, 'wb') as f:
                f.write(wav_file.file)
            mp3_file = AudioSegment.from_file(tmp_file, format='wav')
            mp3_file.export(f'{path}/{filename}', format='mp3')
            return_data = io.BytesIO()
            with open(f'{path}/{filename}', 'rb') as fo:
                return_data.write(fo.read())
            # (after writing, cursor will be at last byte, so move it to start)
            return_data.seek(0)
            os.remove(f'{path}/{filename}')
            os.remove(tmp_file)
            return send_file(return_data, mimetype='audio/mpeg', download_name=filename, as_attachment=True)
        else:
            return err_msg, 400
    except KeyError:
        return err_msg, 400
