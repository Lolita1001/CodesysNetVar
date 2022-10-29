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
from utils.statistics import statistic

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
            self.cycle()

    @statistic.timer(total=True)
    def cycle(self) -> None:
        data_from_client: QueueMessage = self.getter_messages_from_queue()
        self.data_processing(data_from_client)
        self.mq_from_client.task_done()

    @statistic.timer("Delay of new packet from socket")
    def getter_messages_from_queue(self) -> QueueMessage:
        while True:
            try:
                data = self.mq_from_client.get(timeout=1)
                break
            except queue.Empty:
                pass
        logger.debug(
            f"Get 1 message from the queue and queue has "
            f"{self.mq_from_client.qsize()}/{self.mq_from_client.maxsize}\n" + str(data)
        )
        return data

    @statistic.timer("Time of data processing")
    def data_processing(self, data: QueueMessage) -> None:
        rcv = Rcv(message=data.message, client=data.client)
        logger.debug(f"Result of parsing the message:\n{rcv.print()}")
        self.data_packers[rcv.id_list].put_data(rcv)


if __name__ == "__main__":
    try:
        app = Main()
        app.run()
    except KeyboardInterrupt:
        logger.info("\n" + statistic.print_stat_in_table())
    except BaseException as ex:
        logger.exception(ex)
    finally:
        exit()
