import queue
from socketserver import BaseRequestHandler, ThreadingUDPServer
import threading
from dataclasses import dataclass

from loguru import logger

from settings.settings import Settings
from codesys.nvl_parser import NvlOptions


@dataclass
class QueueMessage:
    client: tuple[str, int]
    message: bytes


def _get_handler_with_settings(nvl_options: NvlOptions, rcv_queue: queue.Queue):
    class Handler(BaseRequestHandler):
        def __init__(self, request, client_address, server,
                     _nvl_options: NvlOptions = nvl_options, _rcv_queue: queue.Queue = rcv_queue):
            self.rcv_queue = _rcv_queue
            self.nvl_options = _nvl_options
            super().__init__(request, client_address, server)

        def handle(self):
            msg, sock = self.request
            logger.debug(f'Client {self.client_address} said: {msg}')
            qm = QueueMessage(client=self.client_address, message=msg)
            self.rcv_queue.put(qm)
            if self.nvl_options.acknowledge:
                sock.sendto("Got your message!".encode(), self.client_address)  # Send acknowledge  # todo acknowledge
    return Handler


def get_udp_thread_server(settings: Settings, nvl_config: NvlOptions, rcv_queue: queue.Queue):
    _handler = _get_handler_with_settings(nvl_config, rcv_queue)
    _upd_server = ThreadingUDPServer((str(settings.network.ip), settings.network.port), _handler)
    udp_server_thread = threading.Thread(target=_upd_server.serve_forever)
    udp_server_thread.daemon = True
    return udp_server_thread
