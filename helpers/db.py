from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Users(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    user_surname = db.Column(db.String(64), nullable=True)
    user_name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(100), nullable=True, unique=True)
    password = db.Column(db.String(20), nullable=True)
    avatar = db.Column(db.Integer, nullable=False)
    role = db.Column(db.Boolean, default=False)


class Images(db.Model):
    id_image = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(100), nullable=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'))


class Files(db.Model):
    id_file = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    id_image = db.Column(db.Integer)


class Uses(db.Model):
    id_use = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    id_image = db.Column(db.Integer, db.ForeignKey('images.id_image'))
    id_file = db.Column(db.Integer, db.ForeignKey('files.id_file'))


class Mainmenu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=True)
    url = db.Column(db.String(20), nullable=True)