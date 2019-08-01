import logging
import socket
import select
import threading
import traceback

from server.log.decorators import Log
from server.jim.metaclasses import ServerMaker
from server.jim.descriptors import Port
from server.jim.settings import *
from server.jim.utils import send_message, get_message, server_arg_parser
from server.db_server import ServerDB

logger = logging.getLogger('server_logger')
log_ = Log(logger)


class Server(threading.Thread, metaclass=ServerMaker):
    port = Port()

    def __init__(self, address, port, database):
        """
        Инициализация
        :param address: str (IP сервера)
        :param port: int (Порт сервера)
        :param database: object (Экземпляр класса серверной бызы данных)
        """
        self.address = address
        self.port = port
        self.db = database
        self.clients = []
        self.messages = []
        self.names = {}
        super().__init__()

    def __init_socket(self):
        """
        Метод инициализации сокета
        :return: None
        """
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.address, self.port))
        transport.settimeout(0.5)
        self.sock = transport
        self.sock.listen()
        logger.info(
            f'Запущен сервер {self.address}:{self.port}...')

    def __process_message(self, message, listen_socks):
        """
        Метод адресной отправки сообщения определённому клиенту
        :param message: dict (Словарь сообщение)
        :param listen_socks: list (Зарегистрированые пользователи и слушающие сокеты)
        :return: None
        """
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            logger.info(
                f'{message[SENDER]} отправил сообщение пользователю {message[DESTINATION]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере!\n'
                f'отправка сообщения невозможна.')

    def __process_client_message(self, message, client):
        """
        Метод обрабатывающий сообщения от клиентов,
        проверяет корректность, отправляет словарь-ответ в случае необходимости
        :param message: dict (Сообщение от клиента)
        :param client: socket (Клиент)
        :return: None
        """
        logger.debug(f'Разбор сообщения от клиента:\n{message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.db.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, RESPONSE_OK)
            else:
                response = RESPONSE_WRONG_REQUEST
                response[ERROR] = f'Имя пользователя "{client}" уже занято!'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        else:
            response = RESPONSE_WRONG_REQUEST
            response[ERROR] = 'Запрос некорректен!'
            send_message(client, response)
            return

    def run(self):
        """
        Основной метод запуска серверного скрипта
        :return: None
        """
        self.__init_socket()
        print('Сервер запущен...')

        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'Установлено соедение с {client_address}')
                self.clients.append(client)

            receive_list = []
            send_list = []
            try:
                if self.clients:
                    receive_list, send_list, error_list = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if receive_list:
                for client_with_message in receive_list:
                    try:
                        self.__process_client_message(get_message(client_with_message), client_with_message)
                    except Exception:
                        logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.__process_message(message, send_list)
                except Exception:
                    logger.info(f'Связь с {message[DESTINATION]} потеряна!')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()


def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключенных пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


def start_server():
    listen_address, listen_port = server_arg_parser()
    server_db = ServerDB()

    server = Server(listen_address, listen_port, server_db)
    server.daemon = True
    server.run()

    print_help()

    while True:
        command = input('Введите комманду: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            break
        elif command == 'users':
            for user in sorted(server_db.users_list()):
                print(f'Пользователь {user[0]}, последний вход: {user[1]}')
        elif command == 'connected':
            for user in sorted(server_db.active_users_list()):
                print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif command == 'loghist':
            name = input(
                'Введите имя пользователя для просмотра истории. Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(server_db.login_history(name)):
                print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Команда не распознана.')


if __name__ == '__main__':
    start_server()
