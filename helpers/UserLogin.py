import os

from flask import url_for
from flask_login import UserMixin


class UserLogin(UserMixin):
    def __init__(self):
        self.__user = None

    def fromDB(self, user_id, db):
        self.__user = db.getuser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id_user'])

    def get_role(self):
        return str(self.__user['role'])

    def getname(self):
        return self.__user['user_name'] if self.__user else 'Без имени'

    def getsurname(self):
        return self.__user['user_surname'] if self.__user else 'Без фамилии'

    def getemail(self):
        return self.__user['email'] if self.__user else 'Без email'

    def getavatar(self, app):
        img = None
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print('Не найден файл ' + str(e))
        else:
            with app.open_resource(app.root_path + '\\' + f"{self.__user['avatar']}", "rb") as f:
                print(f)
                img = f.read()

        return img

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext == 'png' or ext == 'PNG':
            return True
        return False

