import sys
import queue
from typing import TypeAlias

from loguru import logger

from settings.settings import settings
from codesys.nvl_parser import NvlParser, NvlOptions
from network.server import get_udp_thread_server, QueueMessage
from network.parser import Rcv
from data_packer import DataPacker


logger.remove()
if settings.logger.level_in_stdout:
    logger.add(sys.stdout, level=settings.logger.level_in_stdout)
if settings.logger.level_in_file:
    logger.add('rotation_log.log', level=settings.logger.level_in_file, rotation=settings.logger.file_rotate)

logger.debug('Run application...')


ListID: TypeAlias = int


class Main:
    def __init__(self):
        self.nvl_configs = self.create_nvl_configs(settings.nvl.paths)
        self.data_packers = self.create_data_packers(self.nvl_configs)
        self.mq_from_client = queue.Queue(100)
        self.udp_server_thread = get_udp_thread_server(self.mq_from_client)

    @staticmethod
    def create_nvl_configs(nvl_paths) -> dict[ListID, NvlOptions]:
        nvl_configs = {}
        for path in nvl_paths:
            nvl_config = NvlParser(path).parse()
            nvl_configs[nvl_config.list_id] = nvl_config
        return nvl_configs

    @staticmethod
    def create_data_packers(nvl_configs: dict[ListID, NvlOptions]) -> dict[ListID, DataPacker]:
        data_packers = {}
        for list_id, config in nvl_configs.items():
            dp = DataPacker(config)
            data_packers[list_id] = dp
        return data_packers

    def run(self) -> None:
        self.udp_server_thread.start()
        while True:
            data_from_client: QueueMessage = self.mq_from_client.get()
            logger.debug(data_from_client)
            rcv = Rcv(message=data_from_client.message, client=data_from_client.client)
            self.data_packers[rcv.id_list].put_data(rcv)
            self.mq_from_client.task_done()


if __name__ == '__main__':
    app = Main()
    app.run()
