from flask_sqlalchemy import SQLAlchemy
from api.api import app

import os
import subprocess
import socket
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('FLASK_TEST_DB', None)
if (socket.gethostname() == 'DESKTOP-32A6L4O'):
    app.config['SQLALCHEMY_DATABASE_URI'] = subprocess.getstatusoutput('heroku config:get DATABASE_URL -a school-meal-with-react')[1]
else:
    app.config['SQLALCHEMY_DATABASE_URI']  = os.environ.get('DATABASE_URL', None)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
