import sys
from server.log.log_config import server_logger
from client.log.config import client_logger
import logging
import socket
# sys.path.append('../')

# метод определения модуля, источника запуска.
if sys.argv[0].find('client_logger') == -1:
    # если не клиент то сервер!
    logger = logging.getLogger('server_logger')
else:
    # ну, раз не сервер, то клиент
    logger = logging.getLogger('client_logger')


# Функция логирования вызовов других функций
def log(func_to_log):
    def log_saver(*args, **kwargs):
        logger.debug(
            f'Была вызвана функция {func_to_log.__name__} c параметрами {args}, {kwargs}. '
            f'Вызов из модуля {func_to_log.__module__}')
        ret = func_to_log(*args, **kwargs)
        return ret

    return log_saver


# Функция проверки, что клиент авторизован на сервере
# Проверяет, что передаваемый объект сокета находится в списке клиентов. Если его там нет закрывает сокет
def login_required(func):
    def checker(*args, **kwargs):
        # Если первый аргумент - экземпляр MessageProcessor
        # А сокет в остальных аргументах
        # Импортить необходимо тут, иначе ошибка рекурсивного импорта.
        from server.core import MessageProcessor
        from server.jim.settings import ACTION, PRESENCE
        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    # Проверяем, что данный сокет есть в списке names класса MessageProcessor
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            # Теперь надо проверить, что передаваемые аргументы не presence сообщение
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            # Если не не авторизован и не сообщение начала авторизации, то вызываем исключение.
            if not found:
                raise TypeError

        return func(*args, **kwargs)

    return checker
