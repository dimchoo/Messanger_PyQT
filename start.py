from sys import platform
import os
from subprocess import Popen
import appscript

SERVER_PATH = os.path.join(os.path.dirname(__file__), 'server.py')
CLIENT_PATH = os.path.join(os.path.dirname(__file__), 'client.py')
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
        if choice == 'start'.lower():
            terminal.do_script(f'python3 {SERVER_PATH}')
            for _ in range(CLIENT_COUNT):
                terminal.do_script(f'python3 {CLIENT_PATH}')
        elif choice == 'kill'.lower():
            terminal.do_script('killall Terminal')
        elif choice == 'quit'.lower():
            print('Скрипт завершен.')
            return
        else:
            print(f'Неизвестная команда: "{choice}"!')


def windows_starter():
    """
    Функция запуска мессенджера на Windows
    :return: None
    """
    from subprocess import CREATE_NEW_CONSOLE
    processes = []
    while True:
        choice = input('Основные команды:\n'
                       '"start" - Запустить процессы сервера и клиентов\n'
                       '"kill"  - Завершить процессы сервера и клиентов\n'
                       '"quit"  - Выйти из этого скрипта\n'
                       '>>> ')
        if choice == 'start'.lower():
            processes.append(Popen('python server.py', creationflags=CREATE_NEW_CONSOLE))
            for _ in range(CLIENT_COUNT):
                processes.append(Popen('python client.py', creationflags=CREATE_NEW_CONSOLE))
        elif choice == 'kill'.lower():
            while processes:
                victim = processes.pop()
                victim.kill()
        elif choice == 'quit'.lower():
            print('Скрипт завершен.')
            return
        else:
            print(f'Неизвестная команда: "{choice}"!')


def linux_starter():
    pass


try:
    if platform == 'darwin'.lower():
        mac_starter()
    elif platform == 'windows'.lower() or 'win32'.lower():
        windows_starter()
    elif platform == 'linux' or 'linux2':
        pass
except KeyboardInterrupt:
    print('\nСкрипт завершен.')
