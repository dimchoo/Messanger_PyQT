import logging.handlers
import os
import sys

BASE_LOG_DIR_PATH = os.path.abspath(os.path.join(__file__, '../'))
CLIENT_LOG_PATH = os.path.join(BASE_LOG_DIR_PATH, 'client.log')

client_logger = logging.getLogger('client_logger')

client_file_handler = logging.FileHandler(CLIENT_LOG_PATH, encoding='utf-8')
client_console_handler = logging.StreamHandler(sys.stderr)

client_log_formatter = logging.Formatter('%(asctime)s - %(levelname)s:\n%(message)s\n')

client_file_handler.setFormatter(client_log_formatter)
client_console_handler.setFormatter(client_log_formatter)

client_file_handler.setLevel(logging.INFO)
client_console_handler.setLevel(logging.WARNING)

client_logger.addHandler(client_file_handler)
client_logger.addHandler(client_console_handler)

client_logger.setLevel(logging.INFO)
