import pytest
from db import Users, Images, Files, Uses


def test_new_user():
    """
    Дано: модель бд Users
    Когда: создание нового пользователя
    Проверяется: поля модели заполняются корректно
    """
    user = Users(user_name="Денис", user_surname="Вавилов",
                 email="denchik2001@gmail.com", password="FlaskIsAwesome", avatar=1)
    assert user.user_name == "Денис"
    assert user.user_surname == "Вавилов"
    assert user.email == "denchik2001@gmail.com"
    assert user.password == "FlaskIsAwesome"


def test_new_image():
    """
    Дано: модель бд Images
    Когда: добавление в бд информации об изображении
    Проверяется: поля модели заполняются корректно
    """
    image = Images(image_name="котик.png", id_user=1)
    assert image.image_name == "котик.png"
    assert image.id_user == 1


def test_new_file():
    """
    Дано: модель бд Files
    Когда: добавление в бд информации о файле
    Проверяется: поля модели заполняются корректно
    """
    files = Files(file_name="котик.zip", id_user=1, id_image=1)
    assert files.file_name == "котик.zip"
    assert files.id_user == 1
    assert files.id_image == 1


def test_new_use():
    """
    Дано: модель бд Uses
    Когда: создание нового использования
    Проверяется: поля модели заполняются корректно
    """
    use = Uses(id_user=1, id_image=1, id_file=1)
    assert use.id_user == 1
    assert use.id_image == 1
    assert use.id_file == 1