import abc
import datetime
import struct
from typing import TypeVar, Any


from sqlalchemy import Boolean, LargeBinary, Integer, BigInteger, Float, Date, String, ARRAY, Time
from sqlalchemy.types import TypeEngine

from utils.exeptions import DataWrongLen, OutOfRange

MICROS_IN_MS = 1000
MS_IN_SECOND = 1000
MS_IN_MINUTE = 60 * MS_IN_SECOND
MS_IN_HOUR = 3600 * MS_IN_SECOND


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
        modulo_h, hour = int_value % MS_IN_HOUR, int_value // MS_IN_HOUR
        modulo_m, minute = modulo_h % MS_IN_MINUTE, modulo_h // MS_IN_MINUTE
        modulo_s, second = modulo_m % MS_IN_SECOND, modulo_m // MS_IN_SECOND
        millisecond = modulo_s % MS_IN_SECOND
        microsecond = millisecond * MICROS_IN_MS
        self.value = datetime.time(hour=hour, minute=minute, second=second, microsecond=microsecond)
        self.ts = datetime.datetime.now()


class CTimeOfDay(CTime):
    def _put(self, value: bytes) -> None:
        int_value = int.from_bytes(value, "little", signed=False)
        if int_value > 86399999:
            raise OutOfRange(f"The value is out of range."
                             f"Codesys type {self.__class__.__name__} has to has values from 0 to 86399999."
                             f"Input value is {int_value}.")
        modulo_h, hour = int_value % MS_IN_HOUR, int_value // MS_IN_HOUR
        modulo_m, minute = modulo_h % MS_IN_MINUTE, modulo_h // MS_IN_MINUTE
        modulo_s, second = modulo_m % MS_IN_SECOND, modulo_m // MS_IN_SECOND
        millisecond = modulo_s % MS_IN_SECOND
        microsecond = millisecond * MICROS_IN_MS
        self.value = datetime.time(hour=hour, minute=minute, second=second, microsecond=microsecond)
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
        self.structure: list[CodesysType] = [self.c_type.__class__("_") for _ in range(self.count)]
        self.__value = [None] * self.count
        self.size = self.c_type.size * self.count
        self.sql_alchemy_type = ARRAY(self.c_type.sql_alchemy_type)

    def _put(self, value: bytes) -> None:
        start = 0
        for ctype_instance in self.structure:
            ctype_instance.put(value[start: start + ctype_instance.size])
            start += ctype_instance.size
        self.ts = datetime.datetime.now()

    @property
    def value(self) -> list[Any]:
        return [v.value for v in self.structure]

    @value.setter
    def value(self, value: list[Any]) -> None:
        self.__value = value


class CTypeDeclaration(list[CType]):
    def append(self, obj: CodesysType) -> None:
        assert issubclass(obj.__class__, CType), "Appended object is not subclass of Codesys"
        super().append(obj)  # noqa

    def get_via_name(self, name: str) -> CType | None:
        for i in self:
            if i.name == name:
                return i
        return None

    def get_elementary_type_list(self) -> list[CType]:
        elementary_types = []
        for i in self:
            elementary_types.extend(self._get_elementary_recursive(i))
        return elementary_types

    def _get_elementary_recursive(self, c_type: CodesysType) -> list[CodesysType]:
        ret_val = []
        if structure := getattr(c_type, 'structure', None):
            for i in structure:
                ret_val.extend(self._get_elementary_recursive(i))
        else:
            ret_val.append(c_type)
        return ret_val
