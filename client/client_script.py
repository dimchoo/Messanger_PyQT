import argparse
import json
import logging
import socket
import sys
from datetime import datetime
from threading import Thread

from client.jim.errors import IncorrectDataReceivedError, ServerError, ReqFieldMissingError
from client.jim.metaclasses import ClientMaker
from client.jim.settings import *
from client.jim.utils import get_message, send_message
from client.log.decorators import Log

logger = logging.getLogger('client_logger')
log = Log(logger)


class Client(metaclass=ClientMaker):

    @staticmethod
    def _get_time():
        """
        Метод возвращает текущее время
        :return: str (HH:MM:SS)
        """
        return datetime.now().strftime("%H:%M:%S")

    @log
    def _create_exit_message(self, account_name):
        """
        Метод, возвращающий словарь с сообщением о выходе
        :param account_name: str (Имя пользователя, который вышел)
        :return: dict (Словарь с сообщением о выходе)
        """
        return {
            ACTION: EXIT,
            TIME: self._get_time(),
            ACCOUNT_NAME: account_name
        }

    @staticmethod
    @log
    def _message_from_server(sock, my_username):
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
                    logger.info(
                        f'Получено сообщение от пользователя {message[SENDER]}:\n'
                        f'{message[MESSAGE_TEXT]}')
                else:
                    logger.error(f'Получено некорректное сообщение от сервера:\n{message}')
            except IncorrectDataReceivedError:
                logger.error('Не удалось декодировать полученное сообщение')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                logger.critical(f'Потеряно соединение с сервером')
                break

    @log
    def _create_message(self, sock, name_from, name_to, message):
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
            TIME: self._get_time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформирован словарь сообщения:\n{message_dict}')
        try:
            send_message(sock, message_dict)
            logger.info(f'Отправлено сообщение для пользователя {name_to}')
        except (
                OSError,
                ConnectionError,
                ConnectionAbortedError,
                ConnectionResetError,
                KeyboardInterrupt,
                json.JSONDecodeError
        ):
            logger.critical('Потеряно соединение с сервером.')
            exit(1)

    @staticmethod
    def _print_help():
        """
        Метод, выводящий на экран подсказки "help"
        :return: None
        """
        print('Поддерживаемые команды:')
        print('#help - Помощь')
        print('#exit - Выйти из чата')

    @log
    def _user_interactive(self, sock, name_from, name_to):
        """
        Метод интерактивной работы с клиентом
        Вывод подсказок, завершение работы скрипта и отправка сообщений
        :param sock:
        :param name_from:
        :param name_to:
        :return: None
        """
        self._print_help()
        while True:
            message = input(f'[{name_from} (Вы)]:\n')
            if message == '#help':
                self._print_help()
            elif message == '#exit':
                send_message(sock, self._create_exit_message(name_from))
                print(f'Чат завершен, {name_from} вышел')
                logger.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                self._create_message(sock, name_from, name_to, message)

    @log
    def _create_presence(self, account_name):
        """
        Метод, возвращающий словарь с сообщением о присутствии
        :param account_name: str (Имя клиента)
        :return: dict (Словарь с сообщением о присутствии)
        """
        logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
        return {
            ACTION: PRESENCE,
            TIME: self._get_time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }

    @staticmethod
    @log
    def _process_response_answer(message):
        """
        Метод разбирает ответ сервера на сообщение о присутствии,
        возращает 200 если все ОК или генерирует исключение при ошибке
        :param message:
        :return: str (Ответ если все ОК)
        """
        logger.debug(f'Разбор приветственного сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            elif message[RESPONSE] == 400:
                raise ServerError(f'400 : {message[ERROR]}')
        raise ReqFieldMissingError(RESPONSE)

    @staticmethod
    def _arg_parser():
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

            server_address, server_port = self._arg_parser()

            client_name = input('Введите ваше имя:')
            receiver_name = input('Введите имя получателя: ')

            logger.info(
                f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
                f'порт: {server_port}, имя пользователя: {client_name}')

            try:
                transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                transport.connect((server_address, server_port))
                send_message(transport, self._create_presence(client_name))
                answer = self._process_response_answer(get_message(transport))
                logger.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
                print(f'Установлено соединение с сервером...')
            except json.JSONDecodeError:
                logger.error('Не удалось декодировать полученный JSON-объект.')
                exit(1)
            except ServerError as error:
                logger.error(f'При установке соединения сервер вернул ошибку:\n{error.text}')
                exit(1)
            except ReqFieldMissingError as missing_error:
                logger.error(f'В ответе сервера отсутствует необходимое поле:\n{missing_error.missing_field}')
                exit(1)
            except (ConnectionRefusedError, ConnectionError):
                logger.critical(
                    f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                    f'конечный компьютер отверг запрос на подключение.')
                exit(1)
            else:
                receiver = Thread(target=self._message_from_server, args=(transport, client_name))
                receiver.daemon = True
                receiver.start()

                user_interface = Thread(target=self._user_interactive, args=(transport, client_name, receiver_name))
                user_interface.daemon = True
                user_interface.start()
                logger.debug('Запущены процессы...')

                while True:
                    time.sleep(1)
                    if receiver.is_alive() and user_interface.is_alive():
                        continue
                    break
        except KeyboardInterrupt:
            print(f'\nЧат завершен, клиент вышел.')


if __name__ == '__main__':
    client = Client()
    client.start()
