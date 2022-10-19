import sys

from loguru import logger

from settings.settings import settings
from codesys.nvl_parser import NvlParser


logger.remove()
if settings.logger.level_in_stdout:
    logger.add(sys.stdout, level=settings.logger.level_in_stdout)
if settings.logger.level_in_file:
    logger.add('rotation_log.log', level=settings.logger.level_in_file, rotation=settings.logger.file_rotate)
