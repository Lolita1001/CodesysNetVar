from typing import Any, Literal
from ipaddress import IPv4Address
from pathlib import Path

from pydantic import BaseSettings, Field, FilePath
from loguru import logger

BASE_DIRECTORY = Path(__file__).parent


class AdvancedSettings(BaseSettings):
    class Config:
        env_file = BASE_DIRECTORY.joinpath('.env')
        secrets_dir = BASE_DIRECTORY.joinpath('secrets/')


class Network(AdvancedSettings):
    local_ip: IPv4Address = Field('127.0.0.1')
    local_port: int = Field(1202)

    class Config:
        env_prefix = "CNV_NETWORK___"


class Storage(AdvancedSettings):
    db_type: str | None = Field(None)
    ip_or_path: IPv4Address | FilePath | None = Field(None)
    port: int = Field(5432)
    login: str = Field('user')
    password: str = Field('')
    db_name: str = Field('mydb')
    table_name_prefix: str = Field('nvl')

    @property
    def url(self) -> str:
        match self.db_type:
            case 'postgresql':
                return f'postgresql://{self.login}:{self.password}@{self.ip_or_path}:{self.port}/{self.db_name}'
            case 'sqlite3':
                return f'sqlite://{self.ip_or_path}'

    @property
    def is_setup(self) -> bool:
        return True if self.ip_or_path and self.db_type else False

    class Config:
        env_prefix = "CNV_STORAGE___"


class NVL(AdvancedSettings):
    paths: list[FilePath] = Field(['external/exp.gvl'])

    class Config:
        env_prefix = "CNV_NVL___"


class Logger(AdvancedSettings):
    level_in_stdout: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] | None = Field('DEBUG')
    level_in_file: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] | None = Field(None)
    file_rotate: Any = Field('1 MB')  # not validate

    class Config:
        env_prefix = "CNV_LOGGER___"


class Settings(BaseSettings):
    network = Network()
    storage = Storage()
    nvl = NVL()
    logger = Logger()


logger.info("Start get env parameters")
settings = Settings()
logger.info("List of env variables:")
logger.info(settings.network.dict())
logger.info(settings.storage.dict(exclude={'password'}))
logger.info(settings.nvl.dict())
logger.info(settings.logger.dict())
