from typing import TypeAlias, Any

from sqlalchemy import Table, Column, Integer, MetaData, create_engine, DateTime
from sqlalchemy.orm import mapper, create_session
from sqlalchemy.sql import func
from loguru import logger

from settings.settings import settings
from codesys.data_types import CodesysType, CTypeDeclaration

if settings.storage.is_setup:
    engine = create_engine(settings.storage.url, echo=settings.logger.level_in_stdout == "DEBUG")
    metadata = MetaData(bind=engine)
    session = create_session(bind=engine, autocommit=False, autoflush=True)

ListID: TypeAlias = int


def create_table_and_orm_class(list_id: ListID, c_types_declarations: CTypeDeclaration) -> Any:  # todo how define type?
    if settings.storage.db_type is None:
        return None

    class Record:
        def __getitem__(self, item: str) -> Any:
            return getattr(self, item)

        def __setitem__(self, item: str, value: Any) -> None:
            return setattr(self, item, value)

        def update_value(self, c_object: CodesysType) -> None:
            return setattr(self, c_object.name, c_object.value)

        def write_to_db(self) -> None:
            session.add(self)
            session.commit()
            logger.debug(f"Write to DB is done")
            logger.debug({param: value for param, value in self.__dict__.items() if param[0] != "_"})

    t = Table(
        f"{settings.storage.table_name_prefix}_{list_id}",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("ts", DateTime(timezone=True), default=func.now()),
        *(Column(c_type.name, c_type.sql_alchemy_type) for c_type in c_types_declarations),
    )
    metadata.create_all(tables=[t])
    logger.info("Created " + t.__repr__())
    mapper(Record, t)
    return Record
