import datetime

from server.jim.settings import *
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker


class ServerDB:
    """
    Класс - серверная база данных
    """

    class AllUsers:
        """
        Класс - отображение таблицы всех пользователей
        Экземпляр этого класса = запись в таблице AllUsers
        """

        def __init__(self, username):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.id = None

    class ActiveUsers:
        """
        Класс - отображение таблицы активных пользователей:
        Экземпляр этого класса = запись в таблице ActiveUsers
        """

        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    class LoginHistory:
        """
        Класс - отображение таблицы истории входов
        Экземпляр этого класса = запись в таблице LoginHistory
        """

        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    def __init__(self):
        """
        Инициализация базы данных
        """
        self.db_engine = create_engine(SERVER_DB, echo=False, pool_recycle=7200)
        self.metadata = MetaData()

        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime)
                            )

        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id'), unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )

        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('name', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip', String),
                                   Column('port', String)
                                   )

        self.metadata.create_all(self.db_engine)

        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)

        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        """
        Метод выполняющийся при входе пользователя, записывает в базу факт входа
        :param username: str (Имя пользователя)
        :param ip_address: str (IP пользователя)
        :param port: int (Порт пользователя)
        :return: None
        """
        rez = self.session.query(self.AllUsers).filter_by(name=username)

        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)
        self.session.commit()

    def user_logout(self, username):
        """
        Метод фиксирующий отключение пользователя
        :param username: str (Имя пользователя)
        :return: None
        """
        user = self.session.query(self.AllUsers).filter_by(name=username).first()

        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def users_list(self):
        """
        Метод возвращает список известных пользователей,
        cо временем последнего входа
        :return: list (Список кортежей известных пользователей)
        """
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
        )
        return query.all()

    def active_users_list(self):
        """
        Метод возвращает список активных пользователей
        :return: list (Список кортежей активных пользователей)
        """
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    # Функция возвращающая историю входов по пользователю или всем пользователям
    def login_history(self, username=None):
        """
        Метод возвращает историю входов по пользователю или всем пользователям
        :param username: str (Имя пользователя)
        :return: list (Список кортежей истории входов одноного или всех пользователей)
        """
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        if username is not None:
            query = query.filter(self.AllUsers.name == username)
        return query.all()


# Отладка
if __name__ == '__main__':
    test_db = ServerDB()

    # выполняем 'подключение' пользователя
    test_db.user_login('test_client_1', '111.111.1.1', 1111)
    test_db.user_login('test_client_2', '222.222.2.2', 2222)
    # выводим список кортежей - активных пользователей
    print(test_db.active_users_list())

    # выполянем 'отключение' пользователя
    test_db.user_logout('test_client_1')
    # выводим список активных пользователей
    print(test_db.active_users_list())

    # запрашиваем историю входов по пользователю
    test_db.login_history('test_client_1')
    # выводим список известных пользователей
    print(test_db.users_list())
