import os
from subprocess import Popen
from sys import platform

import appscript

SERVER_PATH = os.path.join(os.path.dirname(__file__), 'server/server_script.py')
CLIENT_PATH = os.path.join(os.path.dirname(__file__), 'client/client_script.py')
CLIENT_COUNT = 2


def mac_starter():
    """
    Функция запуска мессенджера на MacOS
    :return: None
    """
    terminal = appscript.app('Terminal')
    while True:
        choice = input('Основные команды:\n'
                       '"start" - Запустить процессы сервера и клиентов\n'
                       '"kill"  - Завершить процессы сервера и клиентов\n'
                       '"quit"  - Выйти из этого скрипта\n'
                       '>>> ')
        if choice.lower() == 'start':
            terminal.do_script(f'python3 {SERVER_PATH}')
            for i in range(CLIENT_COUNT):
                terminal.do_script(f'python3 {CLIENT_PATH} -n test{i + 1}')
        elif choice.lower() == 'kill':
            terminal.do_script('killall Terminal')
        elif choice.lower() == 'quit':
            print('Скрипт завершен.')
            return
        else:
            print(f'Неизвестная команда: "{choice}"!')


def windows_starter():
    """
    Функция запуска мессенджера на Windows
    :return: None
    """
    import subprocess
    process = []

    while True:
        action = input(
            'Выберите действие: q - выход , s - запустить сервер, k - запустить клиенты x - закрыть все окна:')
        if action == 'q':
            break
        elif action == 's':
            # Запускаем сервер!
            process.append(
                subprocess.Popen(
                    'python server.py',
                    creationflags=subprocess.CREATE_NEW_CONSOLE))
        elif action == 'k':
            print('Убедитесь, что на сервере зарегистрировано необходимо количество клиентов с паролем 123.')
            print('Первый запуск может быть достаточно долгим из-за генерации ключей!')
            clients_count = int(
                input('Введите количество тестовых клиентов для запуска: '))
            # Запускаем клиентов:
            for i in range(clients_count):
                process.append(
                    subprocess.Popen(
                        f'python client.py -n test{i + 1} -p 123',
                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        elif action == 'x':
            while process:
                process.pop().kill()


def linux_starter():
    pass


try:
    if platform.lower() == 'darwin':
        mac_starter()
    elif platform.lower() == 'windows' or 'win32':
        windows_starter()
    elif platform.lower() == 'linux' or 'linux2':
        pass
except KeyboardInterrupt:
    print('\nСкрипт завершен.')
