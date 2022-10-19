import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# Класс Users (пользователь бота)
class Users(Base):
    """
    Класс Users (пользователей бота). Создает таблицу 'users' и работает с ней
    """
    __tablename__ = "users"
    vk_id = sq.Column(sq.Integer, primary_key=True)
    url = sq.Column(sq.String, nullable=False, unique=True)
    first_name = sq.Column(sq.String(length=30), nullable=False)
    last_name = sq.Column(sq.String(length=30), default='')
    bdate = sq.Column(sq.String(length=15), default='')
    sex = sq.Column(sq.Integer, default=0)
    city = sq.Column(sq.String(length=30), default='')
    deleted = sq.Column(sq.Boolean, default=False)

    def get_dict(self) -> dict:
        """
        Функция создает словарь из данных экземпляра класса Users
        :return: словарь
        """
        dict_={}
        dict_['id'] = self.vk_id
        dict_['url'] = self.url
        dict_['first_name'] = self.first_name
        dict_['last_name'] = self.last_name
        dict_['bdate'] = self.bdate
        dict_['sex'] = self.sex
        dict_['city'] = {'title': self.city}
        dict_['interests'] = ''
        return dict_


# Класс Favorites (избранные пользователем бота пользователи ВК для знакомства)
class Favorites(Base):
    """
    Класс Favorites (пользователей ВК, отобранных пользователями бота). Создает таблицу 'favorites' и работает с ней
    """
    __tablename__ = "favorites"
    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.vk_id"), nullable=False)
    bdate = sq.Column(sq.String(length=15), default='')
    url = sq.Column(sq.String, nullable=False)
    photo_id = sq.Column(sq.String)
    first_name = sq.Column(sq.String(length=30), nullable=False)
    last_name = sq.Column(sq.String(length=30), default='')
    sex = sq.Column(sq.Integer, default=0)
    city = sq.Column(sq.String(length=30), default='')
    interests = sq.Column(sq.String, default='')
    resume = sq.Column(sq.String(length=500), default='')
    user = relationship(Users, backref="favorites")

    def get_dict(self) -> dict:
        """
        Функция создает словарь из данных экземпляра класса Favorites
        :return: словарь
        """
        dict_={}
        dict_['id'] = self.vk_id
        dict_['user_id'] = self.user_id
        dict_['url'] = self.url
        dict_['first_name'] = self.first_name
        dict_['last_name'] = self.last_name
        dict_['bdate'] = self.bdate
        dict_['sex'] = self.sex
        dict_['city'] = {'title': self.city}
        dict_['photo_id'] = self.photo_id
        dict_['interests'] = self.interests
        dict_['resume'] = self.resume
        return dict_


#Класс Blacklist (пользователи исключенные из списков)
class Blacklist(Base):
    """
    Класс Blacklist (удаленных администратором пользователей бота). Создает таблицу 'blacklist' и работает с ней
    """
    __tablename__ = "blacklist"
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.vk_id"), nullable=False)
    user = relationship(Users, backref="blacklist")


#Класс BestPhotos (лучшие фото выбранных пользователей ВК)
class BestPhotos(Base):
    """
    Класс BestPhotos (лучшие по лайкам фото пользователей ВК). Создает таблицу 'best_photos' и работает с ней
    """
    __tablename__ = "best_photos"
    id = sq.Column(sq.Integer, primary_key=True)
    photo_link = sq.Column(sq.String,  nullable=False)
    favorite_id = sq.Column(sq.Integer, sq.ForeignKey("favorites.id"), nullable=False)
    favorite = relationship(Favorites, backref="best_photos")


# Функция удаления и создания таблиц БД
def create_tables(engine):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

