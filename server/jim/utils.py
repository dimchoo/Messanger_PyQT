import argparse
import json
import sys

from server.jim.errors import IncorrectDataReceivedError, NonDictInputError
from server.jim.settings import COMMON_ENCODING, DEFAULT_BIND_IP, DEFAULT_SERVER_PORT


def write_bytes(dict_message):
    """
    Функция преобразует словарь в JSON-объект
    и кодирует его в байты
    :param dict_message: dict (Словарь с данными)
    :return: bytes (Байтовое представление JSON-объекта)
    """
    if isinstance(dict_message, dict):
        byte_message = json.dumps(dict_message).encode(COMMON_ENCODING)
        return byte_message
    raise NonDictInputError


def read_bytes(byte_message):
    """
    Функция декодирует байты
    и преобразует их в словарь
    :param byte_message: bytes (Байтовое представление JSON-объекта)
    :return: dict (Словарь с данными)
    """
    if isinstance(byte_message, bytes):
        dict_message = json.loads(byte_message.decode(COMMON_ENCODING))
        if isinstance(dict_message, dict):
            return dict_message
        raise IncorrectDataReceivedError
    raise IncorrectDataReceivedError


def send_message(sock, message):
    """
    Функция отправки сообщения
    :param sock: socket (Объект сокета)
    :param message: dict (Словарь сообщения)
    :return: None
    """
    sock.send(write_bytes(message))


def get_message(sock):
    """
    Функция получения сообщения
    :param sock: socket (Объект сокета)
    :return: dict (Словарь сообщения)
    """
    return read_bytes(sock.recv(1024))


def server_arg_parser():
    """
    Парсер аргументов коммандной строки
    :return: str & int (ip-адрес и порт)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_SERVER_PORT, type=int, nargs='?')
    parser.add_argument('-a', default=DEFAULT_BIND_IP, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port
