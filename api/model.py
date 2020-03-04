from api.api import db


class Board(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    postSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    userId = db.Column(db.String(20), nullable=False)
    userNickname = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(3000), nullable=False)
    postDate = db.Column(db.DateTime, nullable=False)
    hit = db.Column(db.Integer, nullable=False)


class User(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    userSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    id = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(20), nullable=False)


class Meals(db.Model):

    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    seq = db.Column(db.Integer, primary_key=True, nullable=False)
    schoolCode = db.Column(db.String(15), nullable=False)
    schoolName = db.Column(db.String(25), nullable=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    meals = db.Column(db.JSON, nullable=False)
    ukey = db.Column(db.String(50), unique=True)
    insertDate = db.Column(db.DateTime, nullable=False)


class Schools(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    schoolSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    schoolType = db.Column(db.String(10), nullable=False)
    schoolCode = db.Column(db.String(15), nullable=False, unique=True)
    schoolName = db.Column(db.String(25), nullable=False)
    schoolRegion = db.Column(db.String(10), nullable=False)
    schoolAddress = db.Column(db.String(40), nullable=False)
    insertDate = db.Column(db.DateTime, nullable=False)
