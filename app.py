from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os
from data_models import db, User, Movie, UserMovies

# Set the app up and establish db connection
current_directory = os.getcwd()
database_path = os.path.join(current_directory, 'data', 'talkies.sqlite')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{database_path}'

db.init_app(app)

# with app.app_context():
#    db.create_all()