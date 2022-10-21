import sys

import logging
from loguru import logger

from settings.settings import settings


def loger_setup() -> None:
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    logger.remove()
    if settings.logger.level_in_stdout:
        logger.add(sys.stdout, level=settings.logger.level_in_stdout)
    if settings.logger.level_in_file:
        logger.add('rotation_log.log', level=settings.logger.level_in_file, rotation=settings.logger.file_rotate)
