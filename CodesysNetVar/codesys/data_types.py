import abc
import datetime
import struct


from sqlalchemy import Boolean, LargeBinary, Integer, BigInteger, Float, Date, String, ARRAY


class CType:
    def __init__(self, name: str):
        self.name = name
        self.value = None
        self.ts = None

    @abc.abstractmethod
    def put(self, value: bytes):
        pass

    def __repr__(self):
        return f'{self.ts}| {self.name} : {self.__class__.__name__} := {self.value}'


class CBool(CType):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 1
        self.sql_alchemy_type = Boolean

    def put(self, value: bytes):
        self.value = bool.from_bytes(value, 'little')
        self.ts = datetime.datetime.now()


class CByte(CType):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 1
        self.sql_alchemy_type = LargeBinary

    def put(self, value: bytes):
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

    def put(self, value: bytes):
        self.value = int.from_bytes(value, 'little')
        self.ts = datetime.datetime.now()


class CUInt(CInt):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 2
        self.sql_alchemy_type = Integer


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


class CUDInt(CInt):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 4
        self.sql_alchemy_type = Integer


class CULInt(CInt):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 8
        self.sql_alchemy_type = BigInteger


class CReal(CType):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 4
        self.sql_alchemy_type = Float

    def put(self, value: bytes):
        self.value = struct.unpack('f', value)[0]
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
        self.sql_alchemy_type = Integer

    def put(self, value: bytes):
        self.value = int.from_bytes(value, 'little')
        self.ts = datetime.datetime.now()


class CDate(CType):
    def __init__(self, name: str):
        super().__init__(name)
        self.size = 4
        self.sql_alchemy_type = Date

    def put(self, value: bytes):
        n_seconds = int.from_bytes(value, 'little')
        self.value = datetime.date.fromtimestamp(0) + datetime.timedelta(seconds=n_seconds)
        self.ts = datetime.datetime.now()


class CString(CType):
    def __init__(self, name: str, size=None):
        super().__init__(name)
        self.size = size+1
        self.sql_alchemy_type = String

    def put(self, value: bytes):
        self.value = value[:value.find(b'\x00')].decode("ascii")
        self.ts = datetime.datetime.now()


class CArray(CType):
    def __init__(self, name: str, c_type=None, count=None):
        super().__init__(name)
        self.c_type = c_type
        self.count = count
        self.size = self.c_type.size * self.count
        self.sql_alchemy_type = ARRAY(self.c_type.sql_alchemy_type)

    def put(self, value: bytes):
        start = 0
        self.value = []
        for _ in range(self.count):
            self.c_type.put(value[start:start + self.c_type.size])
            self.value.append(self.c_type.value)
            start += self.c_type.size
        self.ts = datetime.datetime.now()

