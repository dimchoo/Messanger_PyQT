import logging.handlers
import os
import sys

BASE_LOG_DIR_PATH = os.path.abspath(os.path.join(__file__, '../'))
SERVER_LOG_PATH = os.path.join(BASE_LOG_DIR_PATH, 'server.log')

server_logger = logging.getLogger('server_logger')

server_file_handler = logging.handlers.TimedRotatingFileHandler(SERVER_LOG_PATH, when='d', encoding='utf-8')
server_console_handler = logging.StreamHandler(sys.stderr)

server_log_formatter = logging.Formatter('%(asctime)s - %(levelname)s:\n%(message)s\n')

server_file_handler.setFormatter(server_log_formatter)
server_console_handler.setFormatter(server_log_formatter)

server_file_handler.setLevel(logging.INFO)
server_console_handler.setLevel(logging.WARNING)

server_logger.addHandler(server_file_handler)
server_logger.addHandler(server_console_handler)

server_logger.setLevel(logging.INFO)
