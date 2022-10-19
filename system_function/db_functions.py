import sqlalchemy
from sqlalchemy.orm import sessionmaker
from python_project.models import create_tables, Users, Favorites, BestPhotos, Blacklist
from system_package.def_key_for_bot import get_db_name, get_db_password

def session_open():
    """
    Функция открытия сессии работы с базой данных пользователей ВК
    :return: открытую сессию
    """
    DSN = f'postgresql://postgres:{get_db_password()}@localhost:5432/{get_db_name()}'
    engine = sqlalchemy.create_engine(DSN)
    try:
        create_tables(engine)
    except:
        pass
    Session = sessionmaker(bind=engine)
    return Session()

def ban_user(id: int):
    """
    Функция удаления пользователя бота. Наложение бана.
    Доступна только администратору бота.
    При удалении пользователя удаляются все избранные им контакты.
    :param id: id пользователя ботом (id из ВКонтакте)
    """
    session = session_open()
    try:
        session.query(Users).filter(Users.vk_id == id).update({'deleted':True})
        for q in session.query(Favorites).filter(Favorites.user_id == id):
            session.query(BestPhotos).filter(BestPhotos.favorite_id == q.id).delete()
        session.query(Favorites).filter(Favorites.user_id == id).delete()
        session.add(Blacklist(user_id = id))
        session.commit()
    except:
        pass
    session.close()

def is_banned(id: int):
    """
    Функция проверяет идален ли пользователь бота из базы данных
    :param id: id пользователя ботом (id из ВКонтакте)
    :return: True, если удален и False, если нет
    """
    session = session_open()
    try:
        if session.query(Blacklist).filter(Blacklist.user_id == id).count():
            return True
    except:
        pass
    session.close()
    return False

def is_user_favorite(fav_id: int, user_id: int) ->bool:
    """
    Функция проверяет наличие у пользователя бота данного пользователя ВК в отобранных
    :param user_id: id пользователя ботом (id из ВКонтакте)
    :param fav_id: id проверяемого пользователя ВК (id из ВКонтакте)
    :return: True, если есть и False, если нет
    """
    session = session_open()
    try:
        if session.query(Favorites).filter(Favorites.user_id == user_id, Favorites.vk_id == fav_id).count():
            return True
    except:
        pass
    session.close()
    return False


def is_favorites(id: int) ->bool:
    """
    Функция есть ли у пользователя бота отобранные пользователи ВК
    :param id: id пользователя ботом (id из ВКонтакте)
    :return: True, если есть и False, если нет
    """
    session = session_open()
    try:
        if session.query(Favorites).filter(Favorites.user_id == id).count():
            return True
    except:
        pass
    session.close()
    return False

def add_user(json_: list):
    """
    Добавляет пользователей ВК и ссылки на их фото в базу данных
    :param json_: список пользователей или их фото
    """
    session = session_open()
    model = {'users': Users, 'favorites': Favorites, 'best_photos': BestPhotos}
    try:
        for item in json_:
            class_name = model[item.get('model')]
            session.add(class_name(**item.get('fields')))
        session.commit()
    except:
        pass
    session.close()

def get_users() -> list:
    """
    Функция возвращает пользователей бота из базы данных для администратора бота
    :return: список пользователей бота
    """
    list_=[]
    session = session_open()
    for q in session.query(Users).filter(Users.deleted == False).all():
        dict_ = q.get_dict()
        list_.append(dict_)
    session.commit()
    session.close()
    return list_

def get_favorites(user_id: int) -> list:
    """
    Функция возвращает пользователей ВК из базы данных, которых отобрал пользователь бота
    :param user_id: пользователей бота список отобранных пользователей которого надо вывести
    :return: список пользователей ВК из базы данных для бота
    """
    list_=[]
    session = session_open()
    for q in session.query(Favorites).filter(Favorites.user_id == user_id).all():
        best_ph = session.query(BestPhotos.photo_link).filter(BestPhotos.favorite_id == q.id).all()
        dict_ = q.get_dict()
        dict_['best_photos'] = best_ph
        list_.append(dict_)
    session.commit()
    session.close()
    return list_

def delete_favorite(fav_id: int, user_id: int):
    """
    Функция удаляет пользователя ВК из базы данных, который был отобран пользователем бота
    Может сделать только тот кому принадлежит список или администратор бота
    :param fav_id: удаляемый из БД пользователь ВК
    :param user_id: пользователей бота
    """
    session = session_open()
    id = session.query(Favorites.id).filter((Favorites.user_id == user_id) & (Favorites.vk_id == fav_id)).first()[0]
    try:
        session.query(BestPhotos).filter(BestPhotos.favorite_id == id).delete()
        session.commit()
        session.query(Favorites).filter(Favorites.id == id).delete()
        session.commit()
    except:
        pass
    session.close()

def make_json(dict_: dict, model: str) ->list:
    """
    Функция формирует по определенным правилам список пользователей или их фото для занесения их в БД
    :param dict_: словарь данных пользователя ВК
    :param model: таблица БД
    :return: список пользователей ВК или их фото для занесения в базу данных
    """
    json_ = []
    if model == "users" or model == "favorites":
        record = {}
        record['model'] = model
        record['fields'] = {}
        record['fields']['vk_id'] = dict_['id']
        record['fields']['url'] = str(dict_['url'])
        record['fields']['first_name'] = str(dict_['first_name'])
        record['fields']['last_name'] = str(dict_['last_name'])
        record['fields']['bdate'] = str(dict_['bdate'])
        record['fields']['sex'] = dict_['sex']
        record['fields']['city'] = str(dict_['city']['title'])
        if  model == "favorites":
            record['fields']['user_id'] = dict_['user_id']
            record['fields']['photo_id'] = str(dict_['photo_id'])
            record['fields']['interests'] = str(dict_['interests'])
            record['fields']['resume'] = str(dict_['resume'])
        json_.append(record)
    elif model == "best_photos":
        if dict_['best_photos']:
            session = session_open()
            id = session.query(Favorites.id).filter((Favorites.vk_id == dict_['id']) & (Favorites.user_id == dict_['user_id'])).first()[0]
            session.commit()
            session.close()
            for item in dict_['best_photos']:
                record = {}
                record['model'] = model
                record['fields'] = {}
                record['fields']['favorite_id'] = id
                record['fields']['photo_link'] = item[0]
                json_.append(record)
    return json_


# if __name__ == "__main__":

