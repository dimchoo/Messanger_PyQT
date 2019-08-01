"""
Базовые настройки проекта и общие констаты,
основанные на протоколе JIM.
"""
import time

# 1. Константа общей кодировки проекта:

COMMON_ENCODING = 'utf-8'


# 2. Константы серверных настроек:

DEFAULT_SERVER_ADDRESS = '127.0.0.1'
DEFAULT_SERVER_PORT = 8888
DEFAULT_BIND_IP = ''
SERVER_DB = 'sqlite:///server_db.db3'


# 3. Константы ключей для словарей и JSON-оъектов:

# - Имя пользоватеоя/Название чата (str). Максимум 25 символов:
ACCOUNT_NAME = 'account_name'
# - Тип сообщения (str). Максимум 15 символов:
ACTION = 'action'
# - Необязательное сообщение/уведомление:
# ALERT = 'alert'
# - Дата запроса:
# DATE = 'date'
# - Получатель сообщения:
DESTINATION = 'destination'
# - Кодировка:
# ENCODING = 'encoding'
# - Текст ошибки (str):
ERROR = 'error'
# - Выход:
EXIT = 'exit'
# - От кого собщение:
FROM = 'from'
# - Сообщение:
MESSAGE = 'message'
# - Текст сообщения:
MESSAGE_TEXT = 'message_text'
# - Пароль пользователя:
# PASSWORD = 'password'
# - Код ответа (int). 3 цифры:
RESPONSE = 'response'
# - Отправитель сообщения:
SENDER = 'sender'
# - Статус:
# STATUS = 'status'
# - Время запроса:
TIME = 'time'
# - Кому отправить сообщение:
TO = 'to'
# - Тип:
# TYPE = 'type'
# - Данные пользователя (dict):
USER = 'user'


# 4. Константы значений:

# - Значения для ACTION:
AUTHENTICATE = 'authenticate'  # Клиентский запрос на авторизацию
JOIN = 'join'                  # Присоединиться к чату
LEAVE = 'leave'                # Покинуть чат
MSG = 'msg'                    # Простое сообщение пользователю или в чат
PRESENCE = 'presence'          # Клиентское сервисное сообщение о присутствие сервера
PROBE = 'probe'                # Серверный запрос, проверяющий доступность пользователя (online ли пользователь)
QUIT = 'quit'                  # Сообщение, сопровождающее отключение от сервера

# - Значения для USER:
DEFAULT_ACCOUNT_NAME = f'Guest{str(time.time()).split(".")[1]}'


# 5. Константы кодов ответов:

# 1xx — информационные сообщения:
BASIC_NOTICE = 100
IMPORTANT_NOTICE = 101
# 2xx — успешное завершение:
OK = 200
CREATED = 201
ACCEPTED = 202
# 4xx — ошибка на стороне клиента:
WRONG_REQUEST = 400
NOT_AUTH = 401
WRONG_AUTH = 402
FORBIDDEN = 403
NOT_FOUND = 404
CONFLICT = 409
OFFLINE = 410
# 5xx — ошибка на стороне сервера:
SERVER_ERROR = 500


# 6. Константа кортежа со всеми кодами ответов:

RESPONSE_CODES = (
    BASIC_NOTICE,
    IMPORTANT_NOTICE,
    OK,
    CREATED,
    ACCEPTED,
    WRONG_REQUEST,
    NOT_AUTH,
    WRONG_AUTH,
    FORBIDDEN,
    NOT_FOUND,
    CONFLICT,
    OFFLINE,
    SERVER_ERROR
)


# 7. Константы соответствия:

MAX_USERNAME_LEN = 25    # Максимальная длина имени пользователя
MAX_ACTION_LEN = 15      # Максимальная длина типа сообщения
RESPONSE_CODE_LEN = 3    # Единственная длина кода ответа
MAX_CONNECTIONS_LEN = 5  # Максимальная очередь подключений
MAX_PACKAGE_LEN = 1024   # Максимальная длинна сообщения в байтах


# 8. Константы словарей с ответами:

# Код 200:
RESPONSE_OK = {
    RESPONSE: OK
}

# Код 400:
RESPONSE_WRONG_REQUEST = {
    RESPONSE: WRONG_REQUEST,
    ERROR: None
}

