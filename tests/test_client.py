# import sys
# import os
# sys.path.append(os.path.join(os.getcwd(), '..'))
import unittest
from client import create_presence_message, check_server_message, get_time
from jim.config import *
from errors import *


class TestCreatePresenceMessage(unittest.TestCase):

    def test_correct_argument(self):
        """
        Проверка возврата удовлетворительного ответа,
        при передаче корректных данных в функцию
        create_presence_message()
        """
        self.assertEqual(create_presence_message('CORRECT NAME'), {
            ACTION: PRESENCE,
            TIME: get_time(),
            USER: {ACCOUNT_NAME: 'CORRECT NAME'}})

    def test_is_default_name_returns(self):
        """
        Проверка возврата имени пользователя по умолчанию,
        если функции create_presence_message() не передалн аргумент
        """
        self.assertEqual(create_presence_message(), {
            ACTION: PRESENCE,
            TIME: get_time(),
            USER: {ACCOUNT_NAME: DEFAULT_ACCOUNT_NAME}})

    def test_incorrect_argument_type(self):
        """
        Проверка исключения при неправильном типе данных,
        переданном в качестве аргумента функции
        create_presence_message()
        """
        with self.assertRaises(TypeError):
            create_presence_message(['NOT A STRING'])

    def test_too_long_argument(self):
        """
        Проверка исключения при слишком длинном имени пользователя,
        переданном в качестве аргумента функции
        create_presence_message()
        """
        with self.assertRaises(UsernameTooLongError):
            long_username = 'THIS USERNAME IS LONGER THAN MAX_USERNAME_LEN'
            create_presence_message(long_username)

    def test_is_action_return(self):
        """
        Проверка наличия ключа ACTION,
        в вернувшемся результате работы функции
        create_presence_message()
        """
        self.assertTrue(create_presence_message()[ACTION])

    def test_action_value_is_presence(self):
        """
        Проверка наличия значения PRESENCE в ключе ACTION,
        в вернувшемся результате работы функции
        create_presence_message()
        """
        self.assertEqual(create_presence_message()[ACTION], PRESENCE)

    def test_is_time_return(self):
        """
        Проверка наличия ключа TIME,
        в вернувшемся результате работы функции
        create_presence_message()
        """
        self.assertTrue(create_presence_message()[TIME])

    def test_time_value_is_in(self):
        """
        Проверка наличия значения времени в ключе ACTION,
        в вернувшемся результате работы функции
        create_presence_message()
        """
        self.assertEqual(create_presence_message()[TIME], get_time())

    def test_is_user_return(self):
        """
        Проверка наличия ключа USER,
        в вернувшемся результате работы функции
        create_presence_message()
        """
        self.assertTrue(create_presence_message()[USER])

    def test_is_account_name_in_user(self):
        """
        Проверка наличия ключа ACCOUNT_NAME в словаре ключа USER,
        в вернувшемся результате работы функции
        create_presence_message()
        """
        self.assertTrue(create_presence_message()[USER][ACCOUNT_NAME])

    def test_user_account_name_value_is_in(self):
        """
        Проверка наличия значения имени пользователя в ключе ACCOUNT_NAME,
        в вернувшемся результате работы функции
        create_presence_message()
        """
        self.assertEqual(create_presence_message()[USER][ACCOUNT_NAME], DEFAULT_ACCOUNT_NAME)


class TestCheckServerMessage(unittest.TestCase):

    def test_correct_argument(self):
        """
        Проверка возврата удовлетворительного ответа,
        при передаче корректных данных в функцию
        check_server_message()
        """
        self.assertEqual(check_server_message({RESPONSE: OK}), {RESPONSE: OK})

    def test_incorrect_argument_type(self):
        """
        Проверка исключения при неправильном типе данных,
        переданном в качестве аргумента функции
        check_server_message()
        """
        with self.assertRaises(TypeError):
            check_server_message('NOT A DICT')

    def test_response_not_in_argument(self):
        """
        Проверка исключения при отсутствии ключа RESPONSE,
        в аргументе функции check_server_message()
        """
        with self.assertRaises(MissingKeyError):
            check_server_message({'NOT A RESPONSE': OK})

    def test_response_code_incorrect_length(self):
        """
        Проверка исключения некорректной длине значения RESPONSE,
        в аргументе функции check_server_message()
        """
        with self.assertRaises(ResponseCodeLenError):
            check_server_message({RESPONSE: 1})

    def test_response_code_is_incorrect(self):
        """
        Проверка исключения при некорректном коде ответа RESPONSE,
        в аргументе функции check_server_message()
        """
        with self.assertRaises(ResponseCodeError):
            check_server_message({RESPONSE: 789})


if __name__ == '__main__':
    unittest.main()
