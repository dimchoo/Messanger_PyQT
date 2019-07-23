from functools import wraps


class Log:

    def __init__(self, logger):
        self.logger = logger

    @staticmethod
    def _create_log_message(result=None, *args, **kwargs):
        """
        Функция формирования сообщения для лог-файла
        :param result: результат работы функции
        :param args: параметры по порядку
        :param kwargs: именованные параметры
        :return:
        """
        message = ''
        if args:
            message += f"\tArgs: {args};\n"
        if kwargs:
            message += f'\tKwArgs: {kwargs};\n'
        if result:
            message += f'\tResult: {result}'
        return message

    def __call__(self, function):
        """
        Функция для возможности вызова экземпляра класса, как декоратора
        :param function: декорируемая функция
        :return: новая функция
        """

        @wraps(function)
        def wrapper(*args, **kwargs):
            result = function(*args, *kwargs)
            log_message = Log._create_log_message(result, *args, *kwargs)
            self.logger.info(f'\tFunction: {wrapper.__name__};\n{log_message}')
            return result

        return wrapper
