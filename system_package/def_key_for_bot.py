import json

def get_group_token():
    """
    Функция извлечения токена для группы в ВК
    :return: токен группы
    """
    with open('system_package/key.json') as f:
        d = json.load(f)
    group_token = d['group_token']
    return group_token

def get_private_token():
    """
    Функция извлечения токена администратора бота для работы с API ВК
    :return: токен администратора
    """
    with open('system_package/key.json') as f:
        d = json.load(f)
    private_token = d['private_token']
    return private_token

def get_db_name():
    """
    Функция извлечения названия базы данных
    :return: название БД
    """
    with open('system_package/key.json') as f:
        d = json.load(f)
    db_name = d['db_name']
    return db_name

def get_db_password():
    """
    Функция извлечения пароля от базы данных
    :return: пароль БД
    """
    with open('system_package/key.json') as f:
        d = json.load(f)
    db_password = d['db_password']
    return db_password

def get_admin_password():
    """
    Функция извлечения пароля администратора бота
    :return: пароль администратора бота
    """
    with open('system_package/key.json') as f:
        d = json.load(f)
    admin_password = d['admin_password']
    return admin_password

