import dis


class ServerMaker(type):
    """
    Метакласс для проверки соответствия сервера
    """
    def __init__(self, class_name, base_classes, class_dict):
        """
        Инициализация
        :param class_name: cls (Экземпляр метакласса Server)
        :param base_classes: tuple (Кортеж базовых классов)
        :param class_dict: dict (Словарь атрибутов и методов экземпляра метакласса)
        """
        methods = []
        attributes = []
        for func in class_dict:
            try:
                func_returns = dis.get_instructions(class_dict[func])
            except TypeError:
                pass
            else:
                for i in func_returns:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attributes:
                            attributes.append(i.argval)
        if 'connect' in methods:
            raise TypeError('Метод connect недопустимо использовать в серверном классе!')
        if not ('AF_INET' in attributes and 'SOCK_STREAM' in attributes):
            raise TypeError('Некорректная инициализация сокета.')
        super().__init__(class_name, base_classes, class_dict)

