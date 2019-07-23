from base_classes import BaseServer
from jim.utils import server_arg_parser

listen_address, listen_port = server_arg_parser()

server = BaseServer(listen_address, listen_port)

if __name__ == '__main__':
    server.start()
