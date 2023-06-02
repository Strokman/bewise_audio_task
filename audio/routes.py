import io

from audio import app, db
from .models import User, AudioFile, FileProcessor
from flask import request, send_file
from sqlalchemy.exc import IntegrityError


@app.route('/register', methods=['POST'])
def register():
    username: str = request.form['username']
    if username == '':
        return 'Please provide correct username\n', 400
    else:
        user_check = User.get_user(username)
        if user_check:
            return f'User {user_check} exists\n', 409
        else:
            user = User(username)
            db.session.add(user)
            db.session.commit()

            # try:
            #     user = User.get_user(username)
            #     db.session.add(user)
            #     db.session.commit()
            return f'Please save your register information: {user.uuid=}, {user.token=}\n', 200
            # except IntegrityError:
            #     db.session.close()

        # else:



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
    err_msg = 'Please provide correct file_uuid and user_id\n'
    try:
        file_uuid = request.args['id']
        user_id = request.args['user']
        mp3_file: AudioFile = AudioFile.get_file(file_uuid, user_id)
        if mp3_file:
            return_data = io.BytesIO()
            return_data.write(mp3_file.file)
            return_data.seek(0)
            return send_file(return_data, mimetype='audio/mpeg',
                             download_name=f'{mp3_file.owner.uuid}-{mp3_file.file_uuid}',
                             as_attachment=True)
        else:
            return err_msg, 400
    except KeyError:
        return err_msg, 400
