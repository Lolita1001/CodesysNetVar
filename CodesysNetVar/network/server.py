import queue
from socketserver import BaseRequestHandler, ThreadingUDPServer
import threading

from loguru import logger

from settings.settings import Settings
from codesys.nvl_parser import NvlParser


def _get_handler_with_settings(nvl_config: NvlParser, rcv_queue: queue.Queue):
    class Handler(BaseRequestHandler):
        def __init__(self, request, client_address, server,
                     nvl_config: NvlParser = nvl_config, rcv_queue: queue.Queue = rcv_queue):
            self.rcv_queue = rcv_queue
            self.nvl_config = nvl_config
            super().__init__(request, client_address, server)

        def setup(self):
            logger.debug(f'Got connection from: {self.client_address}')

        def handle(self):
            msg, sock = self.request
            logger.debug(f'It said: {msg}')
            self.rcv_queue.put((msg, sock))
            if self.nvl_config.options.acknowledge:
                sock.sendto("Got your message!".encode(), self.client_address)  # Send acknowledge  # todo acknowledge
    return Handler


def get_udp_thread_server(settings: Settings, nvl_config: NvlParser, rcv_queue: queue.Queue):
    _handler = _get_handler_with_settings(nvl_config, rcv_queue)
    _upd_server = ThreadingUDPServer((str(settings.network.ip), settings.network.port), _handler)
    udp_server_thread = threading.Thread(target=_upd_server.serve_forever)
    udp_server_thread.daemon = True
    return udp_server_thread
