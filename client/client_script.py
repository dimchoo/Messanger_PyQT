import logging
import argparse
import sys
import os

from Crypto.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox

from client.jim.settings import *
from client.jim.errors import ServerError
from client.log.decorators import Log
from client.db_client import ClientDatabase
from client.transport import ClientTransport
from client.client_gui.main_window import ClientMainWindow
from client.client_gui.start_dialog import UserNameDialog

logger = logging.getLogger('client_logger')
log = Log(logger)


@log
def arg_parser():
    """
    Парсер аргументов командной строки, возвращает кортеж из 4 элементов
    адрес сервера, порт, имя пользователя, пароль.
    Выполняет проверку на корректность номера порта.
    :return: server_address, server_port, client_name
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_SERVER_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_SERVER_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}.'
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        exit(1)

    return server_address, server_port, client_name


if __name__ == '__main__':
    server_address, server_port, client_name, client_pass = arg_parser()

    client_app = QApplication(sys.argv)

    start_dialog = UserNameDialog()
    if not client_name or not client_pass:
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_pass = start_dialog.client_passwd.text()
        else:
            exit(0)

    logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, имя пользователя: {client_name}')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    keys.publickey().export_key()
    database = ClientDatabase(client_name)
    try:
        transport = ClientTransport(
            server_port,
            server_address,
            database,
            client_name,
            client_pass,
            keys)
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, 'Ошибка сервера', error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    del start_dialog

    main_window = ClientMainWindow(database, transport, keys)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()

    transport.transport_shutdown()
    transport.join()
