import abc
import datetime
import struct
from typing import TypeVar, Any


from sqlalchemy import Boolean, LargeBinary, Integer, BigInteger, Float, Date, String, ARRAY, Time
from sqlalchemy.types import TypeEngine

from utils.exeptions import DataWrongLen


class CType:
    def __init__(self, name: str):
        self.name = name
        self.size: int = 0
        self.value: Any = None
        self.sql_alchemy_type: TypeEngine | None = None
        self.ts: datetime.datetime | None = None

    def put(self, value: bytes) -> None:
        if len(value) != self.size:
            raise DataWrongLen(f"The data has different length for this Data type. "
                               f"Codesys type {self.__class__.__name__} has to has {self.size} bytes. "
                               f"Input value had {len(value)} bytes.")
        self._put(value)

    @abc.abstractmethod
    def _put(self, value: bytes) -> None:
        pass

    def clear(self) -> None:
        self.value = None
        self.ts = None

    def __repr__(self) -> str:
        return f"{self.ts}| {self.name} : {self.__class__.__name__} := {self.value}"


CodesysType = TypeVar("CodesysType", bound=CType)


class CBool(CType):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 1
        self.sql_alchemy_type = Boolean

    def _put(self, value: bytes) -> None:
        self.value = bool.from_bytes(value, "little")
        self.ts = datetime.datetime.now()


class CByte(CType):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 1
        self.sql_alchemy_type = LargeBinary

    def _put(self, value: bytes) -> None:
        self.value = value
        self.ts = datetime.datetime.now()


class CWord(CByte):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 2
        self.sql_alchemy_type = LargeBinary


class CDWord(CByte):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 4
        self.sql_alchemy_type = LargeBinary


class CLWord(CByte):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 8
        self.sql_alchemy_type = LargeBinary


class CInt(CType):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 2
        self.sql_alchemy_type = Integer

    def _put(self, value: bytes) -> None:
        self.value = int.from_bytes(value, "little", signed=True)
        self.ts = datetime.datetime.now()


class CUInt(CInt):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 2
        self.sql_alchemy_type = Integer

    def _put(self, value: bytes) -> None:
        self.value = int.from_bytes(value, "little", signed=False)
        self.ts = datetime.datetime.now()


class CDInt(CInt):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 4
        self.sql_alchemy_type = Integer


class CLInt(CInt):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 8
        self.sql_alchemy_type = BigInteger


class CUDInt(CUInt):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 4
        self.sql_alchemy_type = Integer


class CULInt(CUInt):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 8
        self.sql_alchemy_type = BigInteger


class CReal(CType):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 4
        self.sql_alchemy_type = Float

    def _put(self, value: bytes) -> None:
        self.value = struct.unpack("f", value)[0]
        self.ts = datetime.datetime.now()


class CLReal(CReal):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 8
        self.sql_alchemy_type = Float


class CTime(CType):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 4
        self.sql_alchemy_type = Time

    def _put(self, value: bytes) -> None:
        int_value = int.from_bytes(value, "little")
        hour = int_value // 3600
        minute = (int_value - hour * 3600) // 60
        second = int_value % 60
        self.value = datetime.time(hour=hour, minute=minute, second=second)
        self.ts = datetime.datetime.now()


class CDate(CType):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 4
        self.sql_alchemy_type = Date

    def _put(self, value: bytes) -> None:
        n_seconds = int.from_bytes(value, "little")
        self.value = datetime.date.fromtimestamp(0) + datetime.timedelta(seconds=n_seconds)
        self.ts = datetime.datetime.now()


class CString(CType):
    def __init__(self, name: str, size: int):
        super().__init__(name)
        self.size = size + 1
        self.sql_alchemy_type = String

    def _put(self, value: bytes) -> None:
        self.value = value[: value.find(b"\x00")].decode("ascii")
        self.ts = datetime.datetime.now()


class CArray(CType):
    def __init__(self, name: str, c_type: CodesysType, count: int):
        super().__init__(name)
        self.c_type = c_type
        self.count = count
        self.size = self.c_type.size * self.count
        self.sql_alchemy_type = ARRAY(self.c_type.sql_alchemy_type)

    def _put(self, value: bytes) -> None:
        start = 0
        self.value = []
        for _ in range(self.count):
            self.c_type.put(value[start: start + self.c_type.size])
            self.value.append(self.c_type.value)
            start += self.c_type.size
        self.ts = datetime.datetime.now()


class CTypeDeclaration(list[CType]):
    def append(self, obj: CodesysType) -> None:
        assert issubclass(obj.__class__, CType), "Appended object is not subclass of Codesys"
        super().append(obj)  # noqa

    def get_via_name(self, name: str) -> CType | None:
        for i in self:
            if i.name == name:
                return i
        return None
