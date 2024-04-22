from flask import Flask
from db import db, Users, Images, Files, Uses
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MessageRecognizer.db'

db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
