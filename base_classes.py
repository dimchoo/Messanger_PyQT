import sys
import json
from datetime import datetime
import time
import socket
from errors import *
from jim.config import *
from jim.utils import send_message, get_message
import logging
import log.log_configs.client_log_config
from log.decorators import Log
from multiprocessing import Process
from threading import Thread
import argparse
import select
from metaclasses import ServerMaker, ClientMaker
from descriptors import Port

server_logger = logging.getLogger('server_logger')
log_server = Log(server_logger)

client_logger = logging.getLogger('client_logger')
log_client = Log(client_logger)


class BaseServer(metaclass=ServerMaker):
    port = Port()

    def __init__(self, address, port):
        """
        Инициализация
        :param address: str (IP сервера)
        :param port: int (Порт сервера)
        """
        self.address = address
        self.port = port
        self.clients = []
        self.messages = []
        self.names = {}

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
        server_logger.info(
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
            server_logger.info(
                f'{message[SENDER]} отправил сообщение пользователю {message[DESTINATION]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            server_logger.error(
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
        server_logger.debug(f'Разбор сообщения от клиента:\n{message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
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

    def start(self):
        """
        Основной метод запуска серверного скрипта
        :return: None
        """
        self.__init_socket()
        print('Сервер запущен...')
        try:
            while True:
                try:
                    client, client_address = self.sock.accept()
                except OSError:
                    pass
                else:
                    server_logger.info(f'Установлено соедение с {client_address}')
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
                            server_logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                            self.clients.remove(client_with_message)

                for message in self.messages:
                    try:
                        self.__process_message(message, send_list)
                    except Exception:
                        server_logger.info(f'Связь с {message[DESTINATION]} потеряна!')
                        self.clients.remove(self.names[message[DESTINATION]])
                        del self.names[message[DESTINATION]]
                self.messages.clear()
        except KeyboardInterrupt:
            server_logger.info('Сервер остановлен.')
            print('Сервер остановлен!')


class BaseClient(metaclass=ClientMaker):

    @staticmethod
    def __get_time():
        """
        Метод возвращает текущее время
        :return: str (HH:MM:SS)
        """
        return datetime.now().strftime("%H:%M:%S")

    @log_client
    def __create_exit_message(self, account_name):
        """
        Метод, возвращающий словарь с сообщением о выходе
        :param account_name: str (Имя пользователя, который вышел)
        :return: dict (Словарь с сообщением о выходе)
        """
        return {
            ACTION: EXIT,
            TIME: self.__get_time(),
            ACCOUNT_NAME: account_name
        }

    @staticmethod
    @log_client
    def __message_from_server(sock, my_username):
        """
        Метод-обработчик сообщений других пользователей, поступающих от сервера
        :param sock: socket (Сокет с сообщением)
        :param my_username: str (Имя клиента, для которого сообщение)
        :return: None
        """
        while True:
            try:
                message = get_message(sock)
                if ACTION in message \
                        and message[ACTION] == MESSAGE \
                        and SENDER in message \
                        and DESTINATION in message \
                        and MESSAGE_TEXT in message \
                        and message[DESTINATION] == my_username:
                    print(f'[Сообщение от "{message[SENDER]}"]:\n'
                          f'{message[MESSAGE_TEXT]}')
                    client_logger.info(
                        f'Получено сообщение от пользователя {message[SENDER]}:\n'
                        f'{message[MESSAGE_TEXT]}')
                else:
                    client_logger.error(f'Получено некорректное сообщение от сервера:\n{message}')
            except IncorrectDataReceivedError:
                client_logger.error('Не удалось декодировать полученное сообщение')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                client_logger.critical(f'Потеряно соединение с сервером')
                break

    @log_client
    def __create_message(self, sock, name_from, name_to, message):
        """
        Метод создающий словарь с сообщением
        :param sock: socket (Клиентский сокет)
        :param name_from: str (Имя отправителя)
        :param name_to: str (Имя получателя)
        :param message: str (Сообщение)
        :return: None
        """
        message_dict = {
            ACTION: MESSAGE,
            SENDER: name_from,
            DESTINATION: name_to,
            TIME: self.__get_time(),
            MESSAGE_TEXT: message
        }
        client_logger.debug(f'Сформирован словарь сообщения:\n{message_dict}')
        try:
            send_message(sock, message_dict)
            client_logger.info(f'Отправлено сообщение для пользователя {name_to}')
        except (
                OSError,
                ConnectionError,
                ConnectionAbortedError,
                ConnectionResetError,
                KeyboardInterrupt,
                json.JSONDecodeError
        ):
            client_logger.critical('Потеряно соединение с сервером.')
            exit(1)

    @staticmethod
    def __print_help():
        """
        Метод, выводящий на экран подсказки "help"
        :return: None
        """
        print('Поддерживаемые команды:')
        print('#help - Помощь')
        print('#exit - Выйти из чата')

    @log_client
    def __user_interactive(self, sock, name_from, name_to):
        """
        Метод интерактивной работы с клиентом
        Вывод подсказок, завершение работы скрипта и отправка сообщений
        :param sock:
        :param name_from:
        :param name_to:
        :return: None
        """
        self.__print_help()
        while True:
            message = input(f'[{name_from} (Вы)]:\n')
            if message == '#help':
                self.__print_help()
            elif message == '#exit':
                send_message(sock, self.__create_exit_message(name_from))
                print(f'Чат завершен, {name_from} вышел')
                client_logger.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                self.__create_message(sock, name_from, name_to, message)

    @log_client
    def __create_presence(self, account_name):
        """
        Метод, возвращающий словарь с сообщением о присутствии
        :param account_name: str (Имя клиента)
        :return: dict (Словарь с сообщением о присутствии)
        """
        client_logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
        return {
            ACTION: PRESENCE,
            TIME: self.__get_time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }

    @staticmethod
    @log_client
    def __process_response_answer(message):
        """
        Метод разбирает ответ сервера на сообщение о присутствии,
        возращает 200 если все ОК или генерирует исключение при ошибке
        :param message:
        :return: str (Ответ если все ОК)
        """
        client_logger.debug(f'Разбор приветственного сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            elif message[RESPONSE] == 400:
                raise ServerError(f'400 : {message[ERROR]}')
        raise ReqFieldMissingError(RESPONSE)

    @staticmethod
    def __arg_parser():
        """
        Метод парсит аргументы коммандной строки
        :return: адрес и порт сервера
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('addr', default=DEFAULT_SERVER_ADDRESS, nargs='?')
        parser.add_argument('port', default=DEFAULT_SERVER_PORT, type=int, nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        server_address = namespace.addr
        server_port = namespace.port

        return server_address, server_port

    def start(self):
        """
        Метод старта клиентского модуля
        :return: None
        """
        try:
            print('Консольный месседжер запущен...')

            server_address, server_port = self.__arg_parser()

            client_name = input('Введите ваше имя:')
            receiver_name = input('Введите имя получателя: ')

            client_logger.info(
                f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
                f'порт: {server_port}, имя пользователя: {client_name}')

            try:
                transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                transport.connect((server_address, server_port))
                send_message(transport, self.__create_presence(client_name))
                answer = self.__process_response_answer(get_message(transport))
                client_logger.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
                print(f'Установлено соединение с сервером...')
            except json.JSONDecodeError:
                client_logger.error('Не удалось декодировать полученный JSON-объект.')
                exit(1)
            except ServerError as error:
                client_logger.error(f'При установке соединения сервер вернул ошибку:\n{error.text}')
                exit(1)
            except ReqFieldMissingError as missing_error:
                client_logger.error(f'В ответе сервера отсутствует необходимое поле:\n{missing_error.missing_field}')
                exit(1)
            except (ConnectionRefusedError, ConnectionError):
                client_logger.critical(
                    f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                    f'конечный компьютер отверг запрос на подключение.')
                exit(1)
            else:
                receiver = Thread(target=self.__message_from_server, args=(transport, client_name))
                receiver.daemon = True
                receiver.start()

                user_interface = Thread(target=self.__user_interactive, args=(transport, client_name, receiver_name))
                user_interface.daemon = True
                user_interface.start()
                client_logger.debug('Запущены процессы')

                while True:
                    time.sleep(1)
                    if receiver.is_alive() and user_interface.is_alive():
                        continue
                    break
        except KeyboardInterrupt:
            print(f'Чат завершен, клиент вышел')
