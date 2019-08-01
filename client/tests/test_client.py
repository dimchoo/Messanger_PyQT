# import sys
# import os
# sys.path.append(os.path.join(os.getcwd(), '..'))
import unittest

from client.client_script import Client
from client.jim.errors import *
from client.jim.settings import *

client = Client()


class TestClass(unittest.TestCase):
    # тест коректного запроса
    def test_def_presence(self):
        test = client._create_presence('Guest')
        test[TIME] = client._get_time()  # время необходимо приравнять принудительно иначе тест никогда не будет пройден
        self.assertEqual(test, {ACTION: PRESENCE, TIME: client._get_time(), USER: {ACCOUNT_NAME: 'Guest'}})

    # тест корректтного разбора ответа 200
    def test_200_ans(self):
        self.assertEqual(client._process_response_answer({RESPONSE: 200}), '200 : OK')

    # тест корректного разбора 400
    def test_400_ans(self):
        self.assertRaises(ServerError, client._process_response_answer, {RESPONSE: 400, ERROR: WRONG_REQUEST})

    # тест исключения без поля RESPONSE
    def test_no_response(self):
        self.assertRaises(ReqFieldMissingError, client._process_response_answer, {ERROR: WRONG_REQUEST})


if __name__ == '__main__':
    unittest.main()
