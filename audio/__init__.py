import audio
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import getenv


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test_task.db"
db = SQLAlchemy()
db.init_app(app)

from audio import routes
