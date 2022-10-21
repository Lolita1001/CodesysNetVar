import queue
from typing import TypeAlias
from pathlib import Path

from loguru import logger

from utils.loger_setup import loger_setup
from settings.settings import settings
from codesys.nvl_parser import NvlParser, NvlOptions
from network.server import get_udp_thread_server, QueueMessage
from network.parser import Rcv
from data_packer import DataPacker


loger_setup()

ListID: TypeAlias = int


class Main:
    def __init__(self) -> None:
        self.nvl_configs = self.create_nvl_configs(settings.nvl.paths)
        self.data_packers = self.create_data_packers(self.nvl_configs)
        self.mq_from_client: queue.Queue = queue.Queue(100)
        self.udp_server_thread = get_udp_thread_server(self.mq_from_client)

    @staticmethod
    def create_nvl_configs(nvl_paths: list[Path]) -> dict[ListID, NvlOptions]:
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
        logger.info("The UDP server starting")
        while True:
            data_from_client: QueueMessage = self.mq_from_client.get()
            logger.debug(
                f"Get 1 message from the queue and queue has "
                f"{self.mq_from_client.qsize()}/{self.mq_from_client.maxsize}"
            )
            logger.debug(data_from_client)
            rcv = Rcv(message=data_from_client.message, client=data_from_client.client)
            logger.debug(f"Result of parsing the message:\n{rcv.print()}")
            self.data_packers[rcv.id_list].put_data(rcv)
            self.mq_from_client.task_done()


if __name__ == "__main__":
    try:
        app = Main()
        app.run()
    except Exception as ex:
        logger.exception(ex)
