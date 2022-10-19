import vk_api
import re
from vk_api.longpoll import VkLongPoll, VkEventType
from system_package.keyboards import Keyboard
from system_function.db_functions import add_user, make_json, get_favorites, delete_favorite, is_banned, get_users, ban_user, is_favorites, is_user_favorite
from system_package.def_key_for_bot import get_admin_password, get_group_token, get_private_token

def get_session():
    """
    Открытие сессии для работы с VK API
    :return: доступ к сессии
    """
    return vk_api.VkApi(token=get_group_token())

def sender(id: int, text: str, keyboard=None, attachment: str = ''):
    """
    Функция отправляет сообщения и инструкции пользователю бота
    и клавиатуру
    :param id: id пользователя ВК
    :param text: текст сообщения
    :param keyboard: экранные кнопки
    :param attachment: прикрепление (фото)
    """
    session = get_session()
    if keyboard:
        session.method('messages.send', {'user_id': id, 'message': text, 'attachment': attachment, 'random_id': 0, 'keyboard': keyboard.get_keyboard()})
    else:
        session.method('messages.send', {'user_id': id, 'message': text, 'attachment': attachment, 'random_id': 0})

def sender_photos(id: int, dict_: dict):
    """
    Функция отправляет фотографии пользователю бота
    :param id: id пользователя ВК
    :param dict_: словарь содержащий id фотографий
    """
    session = get_session()
    if dict_['best_photos']:
        session.method('messages.send', {'user_id': id, 'message': 'самые популярные фото:', 'random_id': 0})
        attach_str = 'photo'+ str(dict_['id']) + '_'
        for item in dict_['best_photos']:
            session.method('messages.send', {'user_id': id, 'attachment': attach_str+item[0], 'random_id': 0})

def message_find_user(dict_: dict) -> str:
    """
    Функция преобразования данных о пользователе в удобную строку
    :param dict_: словарь содержащий данные о пользователе
    :return: строка, которая выводится на экран
    """
    sex = {1: 'женский', 2: 'мужской', 0: 'не определен',}
    return f"""
            {dict_['first_name']} {dict_['last_name']}: {dict_['url']}
            дата рождения: {dict_['bdate']} 
            пол: {sex[dict_['sex']]}
            город: {dict_['city']['title']}
            интересы: {dict_['interests']}
            """
def get_user_info(id: int):
    """
    Функция сбора информации о пользователе бота
    :param id: id пользователя ВК
    :return: список необходимых параметров пользователя
    """
    session = get_session()
    user_info = session.method('users.get', {'user_ids': id, 'fields': 'sex, bdate, city'})
    user_info[0]['url'] = 'https://vk.com/id' + str(user_info[0]['id'])
    if 'sex' not in user_info[0].keys():
        user_info[0]['sex'] = 0
    if 'bdate' not in user_info[0].keys():
        user_info[0]['bdate'] = '1.1.1970'
    if 'city' not in user_info[0].keys():
        user_info[0]['city'] = {'title': 'не указан'}
    return user_info

def search_bot():
    """
    Функция отслеживания событий бота и возврата реакции на эти события
    Функция запускает поиск в интернете и в базе данных,
    возвращает анкеты пользователей ВК и анкеты уже записанных в базу данных.
    Вызывает функции добавления в БД и удаления из нее...
    """
    session = get_session()
    longpoll = VkLongPoll(session)
    age = [0, 300]
    sex = 0
    dict_sex = {'female': 1, 'male': 2, 'any gender': 0}
    city_name = ''
    offset = 0
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            id = event.user_id
            event_txt = event.text.lower()
            if is_banned(id):
                event_txt = 'banned'
            else:
                user_info = get_user_info(id)
                user_fname = user_info[0]['first_name']
                user_lname = user_info[0]['last_name']

# *************  просмотр БД и удаление выбранных пользователей: ***********************
            if event_txt == 'check database':
                ind = 0
                favorites_list = get_favorites(id)
                sender(id, message_find_user(favorites_list[ind]), attachment='photo' + favorites_list[ind]['photo_id'])
                sender_photos(id, favorites_list[ind])
                kb = Keyboard(buttons = [('Next', 'primary'), ('Delete', 'primary'), ('Stop', 'negative')], one_time=True)
                sender(id, f'{kb}', kb.keyboard)
            elif event_txt == 'next':
                if ind < len(favorites_list) - 1:
                    ind += 1
                else:
                    ind = 0
                sender(id, message_find_user(favorites_list[ind]), attachment='photo' + favorites_list[ind]['photo_id'])
                sender_photos(id, favorites_list[ind])
                kb = Keyboard(buttons = [('Prev', 'primary'), ('Next', 'primary'), ('Delete', 'primary'), ('Stop', 'negative')], one_time=True)
                sender(id, f'{kb}', kb.keyboard)
            elif event_txt == 'prev':
                if ind > 0:
                    ind -= 1
                else:
                    ind = len(favorites_list) - 1
                sender(id, message_find_user(favorites_list[ind]), attachment='photo' + favorites_list[ind]['photo_id'])
                sender_photos(id, favorites_list[ind])
                kb = Keyboard(buttons = [('Prev', 'primary'), ('Next', 'primary'), ('Delete', 'primary'), ('Stop', 'negative')], one_time=True)
                sender(id, f'{kb}', kb.keyboard)
            elif event_txt == 'delete':
                    delete_favorite(favorites_list[ind]['id'], favorites_list[ind]['user_id'])
                    favorites_list = get_favorites(id)
                    if is_favorites(id):
                        ind = 0
                        sender(id, message_find_user(favorites_list[ind]), attachment='photo' + favorites_list[ind]['photo_id'])
                        sender_photos(id, favorites_list[ind])
                        kb = Keyboard(buttons = [('Next', 'primary'), ('Delete', 'primary'), ('Stop', 'negative')], one_time=True)
                        sender(id, f'{kb}', kb.keyboard)
                    else:
                        kb = Keyboard(buttons=[('Start search', 'primary'), ('Stop', 'negative')])
                        sender(id, f'ЧИТАЙТЕ СООБЩЕНИЯ БОТА - В НИХ ПОДСКАЗКИ.\n{kb}', kb.keyboard)

# *************  определение критериев поиска пользователей ВК (пол, диапазон возраста, город) ************************
            elif event_txt == 'start search':
                add_user(make_json(user_info[0], 'users'))
                kb = Keyboard(buttons = [('Male', 'primary'), ('Female', 'primary'), ('Any gender', 'primary'), ('Stop', 'negative')], one_time=True)
                sender(id, f'Выберите пол\n{kb}', kb.keyboard)
            elif event_txt == 'male' or event_txt == 'female' or event_txt == 'any gender':
                sex = dict_sex[event_txt]
                kb = Keyboard(buttons = [('Search', 'primary'), ('Stop', 'negative')], one_time=True)
                sender(id, f'ВВЕДИТЕ ЖЕЛАЕМЫЙ ДИАПОЗОН ВОЗРАСТА И ГОРОД в формате:\n'
                           f'"age=от-до,city=название города".\n'
                           f'НАПРИМЕР: age=20-40,city=москва\n'
                           f'ИЛИ (если город неважен): age=20-40\n'
                           f'ИЛИ (если возраст неважен): city=москва\n'  
                           f'и просто отправьте сообщение боту.\n'
                           f'Если эти параметры не важны для поиска просто нажмите "Search"\n{kb}', kb.keyboard)
            elif re.search(r'age', event_txt) or re.search(r'city', event_txt):
                pat_age = r'age\s*=\s*(\d+)\s*-\s*(\d+)'
                pat_city = r'city\s*=\s*([a-zA-Zа-яА-Я-]+)'
                try:
                    age = [int(re.search(pat_age, event_txt).group(1)), int(re.search(pat_age, event_txt).group(2))]
                    age.sort()
                except:
                    pass
                try:
                    city_name = re.search(pat_city, event_txt).group(1)
                except:
                    pass
                sender(id, f'Вы выбрали для поиска:\n'
                           f'Пол: {[key for key, item in dict_sex.items() if item == sex][0]}\nДиапазон возраста: {age[0]} - {age[1]} лет\n'
                           f'Город: {city_name.lower().capitalize() if city_name else "не выбран"}\n')
                kb = Keyboard(buttons = [('Search', 'primary'), ('Stop', 'negative')], one_time=True)
                sender(id, f'{kb}', kb.keyboard)

# *************  поиск пользователей ВК в интернете по выбранным критериям и добавление в БД ******************
            elif event_txt == 'search' :
                sender(id, f'ИДЕТ ПОИСК пользователе ВКонтакте по критериям:\n'
                           f'Пол: {[key for key, item in dict_sex.items() if item == sex][0]}\nДиапазон возраста: {age[0]} - {age[1]} лет\n'
                           f'Город: {city_name.lower().capitalize() if city_name else "не выбран"}\n')
                users = search_users(sex, age, city_name, offset)
                ind = 0
                sender(id, message_find_user(users['items'][ind]), attachment='photo'+users['items'][ind]['photo_id'])
                sender_photos(id, users['items'][ind])
                offset += 10
                if is_user_favorite(int(users['items'][ind]['id']), id):
                    kb = Keyboard(buttons = [('Show next', 'primary'), ('Search', 'primary'), ('Stop', 'negative')], one_time=True)
                else:
                    kb = Keyboard(buttons = [('Show next', 'primary'), ('Add', 'primary'), ('Search', 'primary'), ('Stop', 'negative')], one_time=True)
                sender(id, f'{kb}', kb.keyboard)
            elif event_txt == 'show next':
                ind += 1
                if ind < 10:
                    sender(id, message_find_user(users['items'][ind]), attachment='photo' + users['items'][ind]['photo_id'])
                    sender_photos(id, users['items'][ind])
                    if is_user_favorite(int(users['items'][ind]['id']), id):
                        kb = Keyboard(buttons=[('Show next', 'primary'), ('Search', 'primary'), ('Stop', 'negative')], one_time=True)
                    else:
                        kb = Keyboard(buttons=[('Show next', 'primary'), ('Add', 'primary'), ('Search', 'primary'), ('Stop', 'negative')], one_time=True)
                    sender(id, f'{kb}', kb.keyboard)
                else:
                    kb = Keyboard(buttons=[('Search', 'primary'), ('Stop', 'negative')], one_time=True)
                    sender(id, f'{kb}', kb.keyboard)
            elif event_txt == 'add':
                users['items'][ind]['user_id'] = id
                users['items'][ind]['resume'] = 'резюме'
                add_user(make_json(users['items'][ind], 'favorites'))
                add_user(make_json(users['items'][ind], 'best_photos'))
                kb = Keyboard(buttons=[('Show next', 'primary'), ('Search', 'primary'), ('Stop', 'negative')])
                sender(id, f'Пользователь успешно добавлен в базу данных.\n{kb}', kb.keyboard)

# *************  начало и окончание работы с ботом *********************
            elif event_txt == 'hi' or event_txt == 'stop':
                age = [0, 300]
                sex = 0
                city_name = ''
                if is_favorites(id):
                    kb = Keyboard(buttons=[('Start search', 'primary'), ('Check database', 'primary'), ('Stop', 'negative')])
                    sender(id, f'ЧИТАЙТЕ СООБЩЕНИЯ БОТА - В НИХ ПОДСКАЗКИ.\n{kb}', kb.keyboard)
                else:
                    kb = Keyboard(buttons=[('Start search', 'primary'), ('Stop', 'negative')])
                    sender(id, f'ЧИТАЙТЕ СООБЩЕНИЯ БОТА - В НИХ ПОДСКАЗКИ.\n{kb}', kb.keyboard)

# *************  блок администратора  ***********************
            elif event_txt == ('adm stop ' + get_admin_password()):
                break
            elif event_txt == ('adm ' + get_admin_password()):
                userslist = get_users()
                if userslist:
                    item = 0
                    sender(id, message_find_user(userslist[item]))
                    kb = Keyboard(buttons = [('PrevUser', 'primary'), ('NextUser', 'primary'), ('BanUser', 'primary'), ('Stop', 'negative')])
                    sender(id, f'{kb}', kb.keyboard)
                else:
                    kb = Keyboard(buttons = [])
                    sender(id, f'Список пользователей пуст', kb.keyboard)
            elif event_txt == 'banuser':
                ban_user(userslist[item]['id'])
                userslist = get_users()
                if userslist:
                    item = 0
                    sender(id, message_find_user(userslist[item]))
                    kb = Keyboard(buttons=[('PrevUser', 'primary'), ('NextUser', 'primary'), ('BanUser', 'primary'), ('Stop', 'negative')])
                    sender(id, f'{kb}', kb.keyboard)
                else:
                    kb = Keyboard(buttons=[])
                    sender(id, f'Список пользователей пуст', kb.keyboard)
            elif event_txt == 'prevuser':
                if item:
                    item -=1
                sender(id, message_find_user(userslist[item]))
                kb = Keyboard(buttons = [('PrevUser', 'primary'), ('NextUser', 'primary'), ('BanUser', 'primary'), ('Stop', 'negative')])
                sender(id, f'{kb}', kb.keyboard)
            elif event_txt == 'nextuser':
                if item < len(userslist) - 1:
                    item +=1
                else:
                    item = 0
                sender(id, message_find_user(userslist[item]))
                kb = Keyboard(buttons = [('PrevUser', 'primary'), ('NextUser', 'primary'), ('BanUser', 'primary'), ('Stop', 'negative')])
                sender(id, f'{kb}', kb.keyboard)
# ***********************************************************

            elif event_txt == 'banned':
                kb = Keyboard(buttons=[])
                sender(id, f'Извините, но по каким-то причинам администратор\n запретил вам пользоваться ботом.', kb.keyboard)
            else:
                sender(id, f'Здравствуйте {user_fname} {user_lname},\nотправте сообщение "hi", чтобы начать работу с ботом')



def search_users(sex: int = 0, age: list = [0, 300], city_name: str = '', offset: int = 0, count: int = 10) -> dict:
    """
    Функция поиска пользователей ВК и их фото в интернете и формирования списка таковых
    :param sex: пол
    :param age: список - интервал возраста
    :param city_name: название города
    :param offset: начальная позиция поиска
    :param count: количество выводимых за один раз пользователей ВК (для работы с минимальными задержками
                    выводим по 10 пользователей)
    :return: список найденных по критериям пользователей ВК
    """
    photos_dict = {}
    private_token = get_private_token()
    session_for_users = vk_api.VkApi(token=private_token)
    vk_for_users = session_for_users.get_api()
    version = '5.131'
    try:
        cities = vk_for_users.database.getCities(access_token=private_token, q=city_name, country_id=1, count=1, v=version)
        city_id = cities['items'][0]['id']
    except:
        city_id = 0
    users = vk_for_users.users.search(access_token=private_token, sex=sex,
                             age_from=int(age[0]), age_to=int(age[1]), city=city_id, offset=offset, count=count,
                             fields="bdate, sex, city, photo_id, interests", v=version)
    for item in users['items']:
        item['url'] = 'https://vk.com/id' + str(item['id'])
        if 'sex' not in item.keys():
            item['sex'] = 0
        if 'bdate' not in item.keys():
            item['bdate'] = '1.1.1970'
        if 'city' not in item.keys():
            item['city'] = {'title':'не указан'}
        if 'photo_id' not in item.keys():
            item['photo_id'] = ''
        if 'interests' not in item.keys():
            item['interests'] = ''
        if not item['is_closed']:
            photos_info = vk_for_users.photos.getAll(owner_id=str(item['id']), access_token=private_token, extended=1)
            count = photos_info['count']
            if count >= 200:
                count = 199
            photos_info = vk_for_users.photos.getAll(owner_id=str(item['id']), access_token=private_token, extended=1, count=count)
            for i in range(count):
                photos_dict[str(photos_info['items'][i]['id'])] = photos_info['items'][i]['likes']['count']
        item['best_photos'] = list(sorted(photos_dict.items(), key=lambda x: x[1], reverse=True)[:3])
        photos_dict = {}
    # pprint(users)
    return users




