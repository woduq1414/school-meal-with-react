from flask_sqlalchemy import SQLAlchemy
from api.api import app

import os


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('FLASK_TEST_DB', None)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
