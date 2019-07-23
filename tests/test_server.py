# import sys
# import os
# sys.path.append(os.path.join(os.getcwd(), '..'))
import unittest
from server import presence_message_response
from jim.config import *
from client import get_time


class TestServerFunctions(unittest.TestCase):

    def test_correct_presence_message_response_return(self):
        """
        Проверка возврата удовлетворительного ответа,
        при передаче корректных данных в функцию
        presence_message_response()
        """
        self.assertEqual(presence_message_response({
            ACTION: PRESENCE,
            TIME: get_time(),
        }), {RESPONSE: OK})

    def test_action_key_is_missing(self):
        """
        Проверка возврата неудовлетворительного ответа,
        при отсутствии ключа ACTON в аргументе функции
        presence_message_response()
        """
        self.assertEqual(presence_message_response({
            'NOT AN ACTION': PRESENCE,
            TIME: get_time(),
        }), {RESPONSE: WRONG_REQUEST, ERROR: 'Неверный запрос!'})

    def test_action_value_is_not_presence(self):
        """
        Проверка возврата неудовлетворительного ответа,
        в аргументе функции presence_message_response(),
        если значение ACTON не PRESENCE
        """
        self.assertEqual(presence_message_response({
            ACTION: 'NOT A PRESENCE',
            TIME: get_time(),
        }), {RESPONSE: WRONG_REQUEST, ERROR: 'Неверный запрос!'})

    def test_time_key_is_missing(self):
        """
        Проверка возврата неудовлетворительного ответа,
        при отсутствии ключа TIME в аргументе функции
        presence_message_response()
        """
        self.assertEqual(presence_message_response({
            ACTION: PRESENCE,
            'NOT A TIME': get_time(),
        }), {RESPONSE: WRONG_REQUEST, ERROR: 'Неверный запрос!'})

    def test_time_value_is_incorrect(self):
        """
        Проверка возврата неудовлетворительного ответа,
        в аргументе функции presence_message_response(),
        если значение TIME не соответствует регулярному выражению
        """
        self.assertEqual(presence_message_response({
            ACTION: PRESENCE,
            TIME: '25:61:62',
        }), {RESPONSE: WRONG_REQUEST, ERROR: 'Неверный запрос!'})


if __name__ == '__main__':
    unittest.main()
