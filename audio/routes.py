from audio import app, db
from flask import request
from .models import User, AudioFile
from pydub import AudioSegment
from uuid import uuid4


@app.route('/register', methods=['POST'])
def register():
    username: str = request.json.get('username')
    if User.check_user_exists(username):
        return 'User exists', 409
    else:
        user = User(username)
        db.session.add(user)
        db.session.flush()
        db.session.commit()
        return f'Please save your register information: {user.uuid=}, {user.token=}', 200


@app.route('/file', methods=['POST'])
def file():
    wav_file = request.files['file']
    user_uuid = request.form['uuid']
    user_token = request.form['token']
    if user_token == db.session.execute(db.select(User.token).filter_by(token=user_token)).scalar() and user_uuid == db.session.execute(db.select(User.uuid).filter_by(uuid=user_uuid)).scalar():
        audio_file = AudioFile(wav_file.filename, wav_file.read(), uuid4().__str__(), user_uuid)
        db.session.add(audio_file)
        db.session.flush()
        db.session.commit()
        return 'OK', 200
    else:
        return 'User not found', 404
    # audio_file = AudioFile(wav_file.filename, wav_file.read(), 'as111dawqddd', 'asdasasd23123dqwqdcqs')
    # db.session.add(audio_file)
    # db.session.commit()
    # a = db.session.execute(db.select(AudioFile.file).filter_by(token='as111dawqddd')).scalar()
    # with open('temp_file.wav', 'wb') as f:
    #     f.write(a)
    # new_file = AudioSegment.from_file('temp_file.wav', format='wav')
    # new_file.export('/Users/antonstrokov/PycharmProjects/bewise_audio_task/kek.mp3', format='mp3')



    # print(*db.session.execute(db.select(AudioFile.file).filter_by(token='asdawqdd')))

    # print(audio)
    return 'ok'
