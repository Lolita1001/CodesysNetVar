import sys
import queue

from loguru import logger

from settings.settings import settings
from codesys.nvl_parser import NvlParser
from network.server import get_udp_thread_server


logger.remove()
if settings.logger.level_in_stdout:
    logger.add(sys.stdout, level=settings.logger.level_in_stdout)
if settings.logger.level_in_file:
    logger.add('rotation_log.log', level=settings.logger.level_in_file, rotation=settings.logger.file_rotate)

nvl_config = NvlParser(settings.nvl.path[0])
q = queue.Queue(100)

udp_server_thread = get_udp_thread_server(settings, nvl_config, q)
udp_server_thread.start()

while True:
    # retrieve data (blocking)
    data = q.get()
    logger.debug(data)
    logger.debug(q.qsize())
    # do something with the data
    # indicate data has been consumed
    q.task_done()
