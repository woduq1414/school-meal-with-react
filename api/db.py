from flask_sqlalchemy import SQLAlchemy
from api.api import app

import os
import subprocess

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('FLASK_TEST_DB', None)
app.config['SQLALCHEMY_DATABASE_URI'] = subprocess.getstatusoutput('heroku config:get DATABASE_URL -a school-meal-with-react')[1]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
