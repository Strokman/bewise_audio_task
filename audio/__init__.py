import audio
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test_task.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@db:5432/test'
app.config['UPLOAD_FOLDER'] = 'static'
app.config['ALLOWED_EXTENSIONS'] = ['.wav']
db = SQLAlchemy()
db.init_app(app)

from audio import routes
