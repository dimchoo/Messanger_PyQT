import dis


class ClientMaker(type):
    """
    Метакласс для проверки корректности клиентов
    """
    def __init__(self, class_name, base_classes, class_dict):
        """
        Инициализация
        :param class_name: cls (Экземпляр метакласса Server)
        :param base_classes: tuple (Кортеж базовых классов)
        :param class_dict: dict (Словарь атрибутов и методов экземпляра метакласса)
        """
        methods = []
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
        for command in ('accept', 'listen'):
            if command in methods:
                raise TypeError(f'Метод {command} недопустимо использовать в классе клиента!')
        if not ('get_message' in methods or 'send_message' in methods):
            raise TypeError('Отсутствуют вызовы функций: get_message или send_message!')
        super().__init__(class_name, base_classes, class_dict)
