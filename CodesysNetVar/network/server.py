from typing import Any
import queue
from socketserver import BaseRequestHandler, ThreadingUDPServer
import threading
from dataclasses import dataclass

from loguru import logger

from settings.settings import settings


@dataclass
class QueueMessage:
    client: tuple[str, int]
    message: bytes


def _get_handler_with_settings(mq_from_client: queue.Queue) -> Any:  # todo how define type?
    class Handler(BaseRequestHandler):
        def __init__(self, request,  # type: ignore
                     client_address,  # type: ignore
                     server,  # type: ignore
                     _mq_from_client: queue.Queue = mq_from_client):
            self.mq_from_client = _mq_from_client
            super().__init__(request, client_address, server)

        def handle(self) -> None:
            msg, sock = self.request
            logger.debug(f"Client {self.client_address} said: {msg}")
            qm = QueueMessage(client=self.client_address, message=msg)
            self.mq_from_client.put(qm)
            logger.debug(f"Queue has {self.mq_from_client.qsize()}/{self.mq_from_client.maxsize} messages")
            # if False:
            #     sock.sendto("Got your message!".encode(), self.client_address)  # Send acknowledge  # todo acknowledge

    return Handler


def get_udp_thread_server(mq_from_client: queue.Queue) -> threading.Thread:
    _handler = _get_handler_with_settings(mq_from_client)
    _upd_server = ThreadingUDPServer((str(settings.network.local_ip), settings.network.local_port), _handler)
    logger.info(f"Create UDP server on {settings.network.local_ip}:{settings.network.local_port}")
    udp_server_thread = threading.Thread(target=_upd_server.serve_forever)
    udp_server_thread.daemon = True
    return udp_server_thread
