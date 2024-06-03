import json
import os
import sqlite3
from datetime import datetime
import re
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask import Flask, g, render_template, session, request, redirect, url_for, flash, make_response, \
    send_from_directory, Response
from flask_paginate import Pagination, get_page_parameter
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from helpers.FDataBase import FDataBase
from helpers.UserLogin import UserLogin
from my_inf import run_inf

dbase = None
DATABASE = 'instance/MessageRecognizer.db'
DEBUG = True
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
MAX_CONTENT_LENGTH = 2048 * 2048
app = Flask(__name__)
app.config.from_object(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Необходимо авторизоваться'
login_manager.login_message_category = 'success'
EMAIL_PATTERN = re.compile(r'^[\w\-\\.]+@([\w-]+\.)+[\w-]{2,4}$')

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.route('/')
def main():
    user = current_user
    no_messages = request.args.get('no_m')

    return render_template("index.html", menu=dbase.getmenu(),
                           param1=session.get('messenger'), param2=session.get('image_name'), user=user, no_m=no_messages)


@app.route('/load_image', methods=['POST'])
def load_image():
    if request.method == 'POST':
        f = request.files['file']
        session['image_name'] = f.filename
        image_path = os.path.join('files', secure_filename(f.filename))
        session['image_path'] = image_path
        try:
            f.save(image_path)
        except FileNotFoundError:
            flash("Вы не выбрали фотографию", "error")
    return redirect(url_for('main'))


@app.route('/change_messenger', methods=['POST'])
def change_messenger():
    if request.method == 'POST':
        if request.form['action'] == 'button1':
            session['messenger'] = 'telegram'
        if request.form['action'] == 'button2':
            session['messenger'] = 'whatsapp'
    return redirect(url_for('main'))


def sql_transaction(date_path, image_path, image_name):
    dbase.addimage(image_path, current_user.get_id())
    image_id = dbase.getimagebyname(image_path)['id_image']
    file_path = os.path.join('results', f"{date_path}", f"{image_name.split('.')[0]}.json")
    dbase.addfile(f"{file_path}", current_user.get_id(),
                  image_id)
    file_id = dbase.getfilebyname(f"{file_path}")['id_file']
    dbase.adduserecord(date_path, file_id, current_user.get_id(), image_id)


@app.route('/run_model', methods=['POST', 'GET'])
@login_required
def run_model():
    user = current_user

    if request.method == 'POST':
        if not session.get('image_path'):
            flash("Вы не загрузили фотографию", "error")
            return render_template("index.html",
                                   menu=dbase.getmenu(),
                                   param1=session.get('messenger'),
                                   param2=session.get('image_name'), user=user)

        if not session.get('messenger'):
            flash("Вы не выбрали мессенджер", "error")
            return render_template("index.html",
                                   menu=dbase.getmenu(),
                                   param1=session.get('messenger'),
                                   param2=session.get('image_name'), user=user)
        date_path = run_inf(session.get('image_path'), session.get('messenger'))
        with open(f"results/{date_path}/{session.get('image_name').split('.')[0]}.json", 'r') as file:
            data = json.load(file)
            try:
                if data['info']:
                    return redirect(url_for('main', no_m=True))
            except KeyError:
                pass
            session['data'] = data
        sql_transaction(date_path, session.get('image_path'), session.get('image_name'))
        session.pop('messenger')
        session.pop('image_name')
        return render_template('json.html', data=data, menu=dbase.getmenu(), user=user)
    # Применяем фильтр, если указан
    if request.method == 'GET':
        data = session['data']
        filter_by_type = request.args.getlist('type')
        filter_by_changed = request.args.getlist('changed')
        filter_by_quote = request.args.getlist('quote')

        if 'own' in filter_by_type:
            data['messages'] = [message for message in data['messages'] if message['type'] == 'Исходящие']
        elif 'others' in filter_by_type:
            data['messages'] = [message for message in data['messages'] if message['type'] == 'Входящие']

        if 'changed' in filter_by_changed:
            data['messages'] = [message for message in data['messages'] if message['changed'] is True]
        elif 'not_changed' in filter_by_changed:
            data['messages'] = [message for message in data['messages'] if message['changed'] is False]

        if 'with_quote' in filter_by_quote:
            data['messages'] = [message for message in data['messages'] if message['quote'] is not None]
        elif 'without_quote' in filter_by_quote:
            data['messages'] = [message for message in data['messages'] if message['quote'] is None]

        return render_template('json.html', data=data, menu=dbase.getmenu(), user=user)


@app.route("/login", methods=["POST", "GET"])
def login():
    user = current_user
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":
        user = dbase.getuserbyemail(request.form['email'])
        if user:
            if check_password_hash(user['password'], request.form['psw']):
                userlogin = UserLogin().create(user)
                rm = True if request.form.get('remainme') else False
                login_user(userlogin, remember=rm)
                if request.args.get("next"):
                    return redirect(request.args.get("next"), code=307)
                return redirect(url_for("profile"))
            flash("Неверная пара логин/пароль", "error")
        else:
            flash("Такого пользователя не существует, необходимо зарегистрироваться", "error")

    return render_template("login.html", menu=dbase.getmenu(), user=user)


@app.route('/register', methods=['POST', 'GET'])
def register():
    user = current_user
    if request.method == 'POST':
        if not EMAIL_PATTERN.search(request.form['email']):
            flash("Неправильный email", 'error')
            return redirect(url_for('register'))
        if len(request.form['psw']) < 8:
            flash("Пароль должен быть больше восьми символов", 'error')
            return redirect(url_for('register'))
        if request.form['psw'] == request.form['psw2']:
            hashpsw = generate_password_hash(request.form['psw'])
            res = dbase.adduser(request.form['surname'], request.form['name'], request.form['email'], hashpsw)
            if res:
                flash("Вы зарегистрированы", 'success')
                return redirect(url_for('login'))
            else:
                flash('Пользователь с таким email уже зарегистрирован', 'error')
        else:
            flash('Пароли не совпадают', 'error')
    return render_template('register.html', menu=dbase.getmenu(), user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    detected = request.args.get('detected')
    selected_user = request.args.get('user')
    usages = dbase.getuserusage(current_user.get_id()) if int(current_user.get_role()) == 0 else dbase.getallusage()
    print('1111111111111111111111111111', usages)
    if start_date is None:
        start_date = ''  # Установите значение по умолчанию, если параметр не передан
    if end_date is None:
        end_date = ''  # Установите значение по умолчанию, если параметр не передан
    if detected is None:
        detected = ''  # Установите значение по умолчанию, если параметр не передан
    if start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            flash('Неверный формат даты. Введите дату в формате "гггг-мм-дд"', 'error')
            return redirect(url_for('profile'))

        usages = [usage for usage in usages if
                  start_date_obj <= datetime.strptime(usage['date_time'].split(' ')[0], '%Y-%m-%d') <= end_date_obj]
    elif start_date and end_date == '':
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            flash('Неверный формат даты. Введите дату в формате "гггг-мм-дд"', 'error')
            return redirect(url_for('profile'))

        usages = [usage for usage in usages if
                  datetime.strptime(usage['date_time'].split(' ')[0], '%Y-%m-%d') >= start_date_obj]
    elif start_date == '' and end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            flash('Неверный формат даты. Введите дату в формате "гггг-мм-дд"', 'error')
            return redirect(url_for('profile'))

        usages = [usage for usage in usages if
                  datetime.strptime(usage['date_time'].split(' ')[0], '%Y-%m-%d') <= end_date_obj]

        # Применяем фильтр по пользователю
    if selected_user:
        usages = [usage for usage in usages if usage['user_name'] == selected_user]

    page = request.args.get('page', 1, type=int)
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (len(usages) + per_page - 1) // per_page
    if type(usages) != str:
        sliced_usages = usages[start:end]
    else:
        if int(current_user.get_role()) == 0:
            return render_template('profile.html', menu=dbase.getmenu(), nouses=usages, total_pages=total_pages,
                                   page=page, start_date=start_date, end_date=end_date)
        else:
            unique_users = dbase.get_unique_users()
            return render_template('admin_profile.html', menu=dbase.getmenu(), nouses=usages,
                                   total_pages=total_pages, page=page, start_date=start_date, end_date=end_date,
                                   unique_users=unique_users, selected_user=selected_user, detected=detected)
    formatted_usages = []
    if int(current_user.get_role()) == 0:
        for i in sliced_usages:
            formatted_usage = [
                i['date_time'],
                str(i['image_name'].split('\\')[1]),
                str(i['file_name'].split('\\')[2])
            ]
            formatted_usages.append(formatted_usage)
    else:
        for i in sliced_usages:
            formatted_usage = [
                i['date_time'],
                str(i['image_name'].split('\\')[1]),
                str(i['file_name'].split('\\')[2]),
                str(i['user_name'])
            ]
            formatted_usages.append(formatted_usage)

    if int(current_user.get_role()) == 0:
        return render_template('profile.html', menu=dbase.getmenu(), uses=formatted_usages, total_pages=total_pages,
                               page=page, start_date=start_date, end_date=end_date)
    else:
        unique_users = dbase.get_unique_users()
        return render_template('admin_profile.html', menu=dbase.getmenu(), uses=formatted_usages,
                               total_pages=total_pages, page=page, start_date=start_date, end_date=end_date,
                               unique_users=unique_users, selected_user=selected_user, detected=detected)

@app.route('/check_json/', methods=['POST'])
def check_json():
    if request.method == 'POST':
        pass_file = request.files['db']
        json_file = request.files['img']

        pass_path = os.path.join('chekins', secure_filename(pass_file.filename))
        pass_file.save(pass_path)

        json_path = os.path.join('chekins', secure_filename(json_file.filename))
        json_file.save(json_path)
        detected = []
        data_time = []
        data_type = []
        # Открываем JSON файл для чтения
        with open(json_path, 'r') as json_file:
            # Загружаем данные из файла
            json_data = json.load(json_file)
            with open(pass_path, 'r', encoding="utf8") as pass_file:
                # Загружаем данные из файла
                passwords = json.load(pass_file)

                for message in json_data['messages']:
                    message_text = message.get("text")  # Получаем текст сообщения

                    if message_text is not None:
                        # Проверяем, содержится ли текст сообщения в значениях файла с паролями
                        for i in passwords.values():
                            if i in message_text.split():
                                detected.append(i)
                                if message.get('time') is not None:
                                    data_time.append(message.get('time'))
                                data_type.append(message.get('type'))

        detected_message = ""
        if not detected:
            detected_message = "Ничего не найдено"
        elif len(detected) == 1:
            detected_message = f"Пароль '{detected[0]}' обнаружен в сообщении отправленном в {data_time[0]}, и имеющим тип {data_type[0]}"
        else:
            detected_message = f"Пароли {', '.join(detected)} обнаружены в сообщениях отправленных в {', '.join(data_time)}, и имеющих тип {', '.join(data_type)}"

        return redirect(url_for('profile', detected=detected_message))

@app.route('/download_image/<filename>')
def download_image(filename):
    # Путь к каталогу, где находятся файлы для скачивания
    directory = 'files'
    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/download_file/<date_time>/<filename>')
def download_file(date_time, filename):
    # Путь к каталогу, где находятся файлы для скачивания
    directory = f'results/{date_time}'
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/userava')
@login_required
def userava():
    img = current_user.getavatar(app)
    if not img:
        return ""
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                res = dbase.updateuseravatar(file, current_user.get_id())
                if not res:
                    flash('Ошибка обновления автара', 'error')
                    return redirect(url_for('profile'))
                flash('Автар обновлен', 'success')
            except FileNotFoundError as e:
                flash('Ошибка чтения файла', 'error')
    return redirect(url_for('profile'))


@app.route('/change_model', methods=['POST'])
@login_required
def change_model():
    if request.method == 'POST':
        if request.form['action'] == 'button1':
            os.remove('src/best_tg.pth')
            model = request.files['model']
            model_path = os.path.join('src/best_tg.pth')
            model.save(model_path)
            return redirect(url_for('profile'))
        if request.form['action'] == 'button2':
            os.remove('src/best_w.pth')
            model = request.files['model']
            model_path = os.path.join('src/best_w.pth')
            model.save(model_path)
            return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(debug=True)
