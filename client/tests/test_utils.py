import unittest

from client.jim.utils import write_bytes, read_bytes


class TestUtilsFunctions(unittest.TestCase):
    """
    Тесты функций модуля utils.py
    """

    def test_correct_write_bytes(self):
        """
        Проверка соответствия записи из словаря в байты
        """
        self.assertEqual(write_bytes({'раз': 'два'}), b'{"\\u0440\\u0430\\u0437": "\\u0434\\u0432\\u0430"}')

    def test_incorrect_write_bytes(self):
        """
        Проверка исключения при неправильном типе данных
        """
        with self.assertRaises(TypeError):
            write_bytes('incorrect type')

    def test_correct_read_bytes(self):
        """
        Проверка соответствия чтения из байт в словарь
        """
        self.assertEqual(read_bytes(b'{"\\u0440\\u0430\\u0437": "\\u0434\\u0432\\u0430"}'), {'раз': 'два'})

    def test_incorrect_read_bytes(self):
        """
        Проверка исключения при неправильном типе данных
        """
        with self.assertRaises(TypeError):
            read_bytes('incorrect type')


if __name__ == '__main__':
    unittest.main()
