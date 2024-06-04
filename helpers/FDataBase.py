import os
import sqlite3
import time, math, re
from flask import url_for
from werkzeug.utils import secure_filename


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getmenu(self):
        try:
            self.__cur.execute(f"SELECT * FROM mainmenu")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

    def adduser(self, surname, name, email, hashpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                return False
            self.__cur.execute("INSERT INTO users(id_user, user_surname, user_name, email, password) "
                               "VALUES(NULL, ?,?,?,?)", (surname, name, email, hashpsw))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка" + str(e))
            return False

        return True

    def getuser(self, id_user):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id_user = {id_user} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def getuserbyemail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def updateuseravatar(self, avatar, id_user):
        if not avatar:
            return False
        try:
            save_path = os.path.join('avatars', secure_filename(avatar.filename))
            avatar.save(save_path)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id_user = ?", (save_path, id_user))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка sqlite ' + str(e))
            return False
        return True

    def addimage(self, image_name, user_id):
        self.__cur.execute(f"SELECT COUNT() as `count` FROM images "
                           f"WHERE image_name LIKE '{image_name}' and id_user LIKE '{user_id}'")
        res = self.__cur.fetchone()
        if res['count'] > 0:
            return True
        try:
            self.__cur.execute("INSERT INTO images(id_image, image_name, id_user) "
                               "VALUES(NULL, ?,?)", (image_name, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка image" + str(e))
            return False

        return True

    def getimagebyname(self, image_name):
        try:
            self.__cur.execute(f"SELECT * FROM images WHERE image_name = '{image_name}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Изображение не найдено")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def addfile(self, file_name, user_id, image_id):
        try:
            self.__cur.execute("INSERT INTO files(id_file, file_name, id_user, id_image) "
                               "VALUES(NULL, ?,?,?)", (file_name, user_id, image_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка file" + str(e))
            return False

        return True

    def getfilebyname(self, file_name):
        try:
            self.__cur.execute(f"SELECT * FROM files WHERE file_name = '{file_name}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Файл не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def adduserecord(self, datetime, id_file, user_id, image_id):
        try:
            self.__cur.execute("INSERT INTO uses(id_use, date_time, id_file, id_user, id_image) "
                               "VALUES(NULL, ?,?,?,?)", (datetime, id_file, user_id, image_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка file" + str(e))
            return False

        return True

    def getuserusage(self, user_id):
        try:
            self.__cur.execute("""
                SELECT i.image_name, f.file_name, u.date_time 
                FROM uses u 
                INNER JOIN images i ON u.id_image = i.id_image 
                INNER JOIN files f ON u.id_file = f.id_file 
                WHERE u.id_user = ?
            """, (user_id,))
            res = self.__cur.fetchall()
            if not res:
                res = "Вы еще не использовали модель"
                return res
            return res
        except sqlite3.Error as e:
            print("Ошибка file " + str(e))

        return False

    def getallusage(self):
        try:
            self.__cur.execute(f"SELECT us.user_name, i.image_name, f.file_name, u.date_time FROM uses u "
                               f"INNER JOIN users us ON u.id_user = us.id_user "
                               f"INNER JOIN images i ON u.id_image = i.id_image "
                               f"INNER JOIN files f ON u.id_file = f.id_file")
            res = self.__cur.fetchall()

            if not res:
                res = "Модель еще не была использована"
                return res
            return res
        except sqlite3.Error as e:
            print("Ошибка file " + str(e))

        return False

    def get_unique_users(self):
        try:
            self.__cur.execute(f"SELECT DISTINCT us.user_name FROM uses u "
                               f"INNER JOIN users us ON u.id_user = us.id_user ")
            users = self.__cur.fetchall()
            return [user[0] for user in users]
        except sqlite3.Error as e:
            print("Ошибка " + str(e))
        return False


