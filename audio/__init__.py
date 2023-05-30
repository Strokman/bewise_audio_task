import audio

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import getenv

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://strokman:gPdybKpr04020051@strokman.synology.me:55432/gis_shishlina"
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI')
app.config['UPLOAD_FOLDER'] = 'static'
app.config['ALLOWED_EXTENSIONS'] = ['.wav']
db = SQLAlchemy()
db.init_app(app)

from audio import routes
