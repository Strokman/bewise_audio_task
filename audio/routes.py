from audio import app, db
from flask import request
from .models import User
from pydub import AudioSegment


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
    file_1 = request.files['file']
    audio = AudioSegment.from_file(file_1, format='raw', frame_rate=44100, channels=2, sample_width=2)
    audio.export('/Users/antonstrokov/PycharmProjects/bewise_audio_task/kek.mp3', format='mp3')
    print(audio)
    return 'ok'
