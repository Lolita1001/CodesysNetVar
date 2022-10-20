from typing import Any, Literal
from ipaddress import IPv4Address
from pathlib import Path

from pydantic import BaseSettings, Field, FilePath


BASE_DIRECTORY = Path(__file__).parent


class Settings(BaseSettings):
    class Network(BaseSettings):
        local_ip: IPv4Address = Field('127.0.0.1')
        local_port: int = Field(1202)

        class Config:
            env_prefix = "CNV_NETWORK___"
            env_file = BASE_DIRECTORY.joinpath('.env')

    class Storage(BaseSettings):
        db_type: str | None = Field(None)
        address_or_path: IPv4Address | FilePath | None = Field(None)
        port: int = Field(5432)
        login: str = Field('user')
        password: str = Field('')
        db_name: str = Field('mydb')
        table_name_prefix: str = Field('nvl')

        @property
        def url(self) -> str:
            match self.db_type:
                case _:
                    pass
            return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

        @property
        def is_setup(self):
            return all([self.db_type, self.address_or_path])

        class Config:
            env_prefix = "CNV_STORAGE___"
            env_file = BASE_DIRECTORY.joinpath('.env')
            secrets_dir = BASE_DIRECTORY.joinpath('secrets/')

    class NVL(BaseSettings):
        paths: list[FilePath] = Field(['external/exp.gvl'])

        class Config:
            env_prefix = "CNV_NVL___"
            env_file = BASE_DIRECTORY.joinpath('.env')

    class Logger(BaseSettings):
        level_in_stdout: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'NONE'] | None = Field('DEBUG')
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
