import audio
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from os import getenv


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test_task.db"
app.config['UPLOAD_FOLDER'] = 'static'
app.config['ALLOWED_EXTENSIONS'] = ['.wav']
db = SQLAlchemy()
db.init_app(app)

from audio import routes
