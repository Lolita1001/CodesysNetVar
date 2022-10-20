import sys
import queue

from loguru import logger

from settings.settings import settings
from codesys.nvl_parser import NvlParser
from network.server import get_udp_thread_server, QueueMessage
from network.parser import Rcv
from data_packer import DataPacker


logger.remove()
if settings.logger.level_in_stdout:
    logger.add(sys.stdout, level=settings.logger.level_in_stdout)
if settings.logger.level_in_file:
    logger.add('rotation_log.log', level=settings.logger.level_in_file, rotation=settings.logger.file_rotate)

logger.debug('Run application...')

nvl_config = NvlParser(settings.nvl.path[0]).parse()

dp = DataPacker(nvl_config)

q = queue.Queue(100)

udp_server_thread = get_udp_thread_server(settings, nvl_config, q)
udp_server_thread.start()

while True:
    data: QueueMessage = q.get()
    logger.debug(data)

    rcv = Rcv(message=data.message, client=data.client)
    dp.put_data(rcv)

    q.task_done()
    logger.debug(dp)
