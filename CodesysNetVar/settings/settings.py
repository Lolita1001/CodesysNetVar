from typing import Any, Literal
from ipaddress import IPv4Address
from pathlib import Path

from pydantic import BaseSettings, Field, FilePath


BASE_DIRECTORY = Path(__file__).parent


class Settings(BaseSettings):
    class Network(BaseSettings):
        ip: IPv4Address = Field('127.0.0.1', env="LOCAL_IP")
        port: int = Field(1202, env="LOCAL_PORT")

        class Config:
            env_prefix = "CNV_NETWORK___"
            env_file = BASE_DIRECTORY.joinpath('.env')

    class Storage(BaseSettings):
        db_type: str = Field('sqlite3')
        address_or_path: IPv4Address | FilePath = Field('/db.sqlite')
        port: int = Field(5432)
        login: str = Field('user')
        password: str
        db_name: str = Field('mydb')
        table_name_prefix: str = Field('nvl')

        class Config:
            env_prefix = "CNV_STORAGE___"
            env_file = BASE_DIRECTORY.joinpath('.env')
            secrets_dir = BASE_DIRECTORY.joinpath('secrets/')

    class NVL(BaseSettings):
        path: list[FilePath]

        class Config:
            env_prefix = "CNV_NVL___"
            env_file = BASE_DIRECTORY.joinpath('.env')

    class Logger(BaseSettings):
        level_in_stdout: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'NONE'] | None = Field(None)
        level_in_file: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'NONE'] | None = Field(None)
        file_rotate: Any = Field('1 MB')  # not validate

        class Config:
            env_prefix = "CNV_LOGGER___"
            env_file = BASE_DIRECTORY.joinpath('.env')

    network = Network()
    storage = Storage()
    nvl = NVL()
    logger = Logger()


settings = Settings()
