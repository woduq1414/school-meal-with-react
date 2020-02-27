from flask_sqlalchemy import SQLAlchemy
from api.api import app

host = "remotemysql.com"
user = "rUl9bXf1sF"
pw = "47x8po2HZm"
dbname = "rUl9bXf1sF"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + user + ':' + pw + '@' + host + '/' + dbname + '?charset=utf8'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app.secret_key = 'randomrandomkey'


db = SQLAlchemy(app)
