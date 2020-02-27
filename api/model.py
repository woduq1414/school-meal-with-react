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