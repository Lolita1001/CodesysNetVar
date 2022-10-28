import struct
import string
import math
import datetime

import pytest

from hypothesis import given, strategies as st

from codesys.data_types import (
    CBool,
    CByte,
    CWord,
    CDWord,
    CLWord,
    CInt,
    CUInt,
    CDInt,
    CLInt,
    CUDInt,
    CULInt,
    CReal,
    CLReal,
    CTime,
    CDate,
    CString,
    CArray,
)
from utils.exeptions import DataWrongLen


@given(st.binary(min_size=1, max_size=1))
def test_dt_bool(value: bytes):
    c_bool = CBool("some_name")
    c_bool.put(value)
    if value == b"\x00" or value == b"":
        assert not c_bool.value
    else:
        assert c_bool.value


@given(st.binary().filter(lambda x: len(x) != 1))
def test_dt_bool_wrong_len(value: bytes):
    c_bool = CBool("some_name")
    with pytest.raises(DataWrongLen):
        c_bool.put(value)


@given(st.binary(min_size=1, max_size=1))
def test_dt_byte(value: bytes):
    c_byte = CByte("some_name")
    c_byte.put(value)
    assert c_byte.value == value


@given(st.binary().filter(lambda x: len(x) != 1))
def test_dt_byte_wrong_len(value: bytes):
    c_byte = CByte("some_name")
    with pytest.raises(DataWrongLen):
        c_byte.put(value)


@given(st.binary(min_size=2, max_size=2))
def test_dt_word(value: bytes):
    c_word = CWord("some_name")
    c_word.put(value)
    assert c_word.value == value


@given(st.binary().filter(lambda x: len(x) != 2))
def test_dt_word_wrong_len(value: bytes):
    c_word = CWord("some_name")
    with pytest.raises(DataWrongLen):
        c_word.put(value)


@given(st.binary(min_size=4, max_size=4))
def test_dt_dword(value: bytes):
    c_dword = CDWord("some_name")
    c_dword.put(value)
    assert c_dword.value == value


@given(st.binary().filter(lambda x: len(x) != 4))
def test_dt_dword_wrong_len(value: bytes):
    c_dword = CDWord("some_name")
    with pytest.raises(DataWrongLen):
        c_dword.put(value)


@given(st.binary(min_size=8, max_size=8))
def test_dt_lword(value: bytes):
    c_lword = CLWord("some_name")
    c_lword.put(value)
    assert c_lword.value == value


@given(st.binary().filter(lambda x: len(x) != 8))
def test_dt_lword_wrong_len(value: bytes):
    c_lword = CLWord("some_name")
    with pytest.raises(DataWrongLen):
        c_lword.put(value)


@given(st.integers(min_value=-32768, max_value=32767))
def test_dt_int(value: int):
    c_int = CInt("some_name")
    binary_val = value.to_bytes(c_int.size, "little", signed=True)
    c_int.put(binary_val)
    assert c_int.value == value


@given(st.binary().filter(lambda x: len(x) != 2))
def test_dt_int_wrong_len(value: bytes):
    c_int = CInt("some_name")
    with pytest.raises(DataWrongLen):
        c_int.put(value)


@given(st.integers(min_value=0, max_value=65535))
def test_dt_uint(value: int):
    c_uint = CUInt("some_name")
    binary_val = value.to_bytes(c_uint.size, "little", signed=False)
    c_uint.put(binary_val)
    assert c_uint.value == value


@given(st.binary().filter(lambda x: len(x) != 2))
def test_dt_uint_wrong_len(value: bytes):
    c_uint = CUInt("some_name")
    with pytest.raises(DataWrongLen):
        c_uint.put(value)


@given(st.integers(min_value=-2147483648, max_value=2147483647))
def test_dt_dint(value: int):
    c_dint = CDInt("some_name")
    binary_val = value.to_bytes(c_dint.size, "little", signed=True)
    c_dint.put(binary_val)
    assert c_dint.value == value


@given(st.binary().filter(lambda x: len(x) != 4))
def test_dt_dint_wrong_len(value: bytes):
    c_dint = CDInt("some_name")
    with pytest.raises(DataWrongLen):
        c_dint.put(value)


@given(st.integers(min_value=0, max_value=4294967295))
def test_dt_udint(value: int):
    c_udint = CUDInt("some_name")
    binary_val = value.to_bytes(c_udint.size, "little", signed=False)
    c_udint.put(binary_val)
    assert c_udint.value == value


@given(st.binary().filter(lambda x: len(x) != 4))
def test_dt_dint_wrong_len(value: bytes):
    c_udint = CUDInt("some_name")
    with pytest.raises(DataWrongLen):
        c_udint.put(value)


@pytest.mark.skip("Test has failed")
@given(st.integers())
def test_dt_lint(value: int):
    c_lint = CLInt("some_name")
    binary_val = value.to_bytes(c_lint.size, "little", signed=True)
    c_lint.put(binary_val)
    assert c_lint.value == value


@given(st.binary().filter(lambda x: len(x) != 8))
def test_dt_lint_wrong_len(value: bytes):
    c_lint = CLInt("some_name")
    with pytest.raises(DataWrongLen):
        c_lint.put(value)


@pytest.mark.skip("Test has failed")
@given(st.integers(min_value=0))
def test_dt_ulint(value: int):
    c_ulint = CULInt("some_name")
    binary_val = value.to_bytes(c_ulint.size, "little", signed=True)
    c_ulint.put(binary_val)
    assert c_ulint.value == value


@given(st.binary().filter(lambda x: len(x) != 8))
def test_dt_ulint_wrong_len(value: bytes):
    c_ulint = CULInt("some_name")
    with pytest.raises(DataWrongLen):
        c_ulint.put(value)


@given(st.floats(width=32))
def test_dt_real(value: float):
    c_real = CReal("some_name")
    binary_val = bytearray(struct.pack("f", value))
    c_real.put(binary_val)
    if math.isnan(value):
        assert math.isnan(c_real.value)
    else:
        assert c_real.value == value


@given(st.binary().filter(lambda x: len(x) != 4))
def test_dt_real_wrong_len(value: bytes):
    c_real = CReal("some_name")
    with pytest.raises(DataWrongLen):
        c_real.put(value)


@pytest.mark.skip("Test has failed")
@given(st.floats(width=64))
def test_dt_lreal(value: float):
    c_lreal = CLReal("some_name")
    binary_val = bytearray(struct.pack("f", value))
    c_lreal.put(binary_val)
    if math.isnan(value):
        assert math.isnan(c_lreal.value)
    else:
        assert c_lreal.value == value


@given(st.binary().filter(lambda x: len(x) != 8))
def test_dt_lreal_wrong_len(value: bytes):
    c_lreal = CLReal("some_name")
    with pytest.raises(DataWrongLen):
        c_lreal.put(value)


@given(st.times(), st.integers(min_value=0, max_value=999))
def test_dt_time(value: datetime.time, milliseconds: int):
    # CTime don't have microseconds.
    # CTime it's count of millisecond since of day.
    value = value.replace(microsecond=milliseconds * 1000)
    int_value = value.hour * 3600 + value.minute * 60 + value.second  # seconds
    int_value = int_value * 1000 + milliseconds  # milliseconds
    c_time = CTime("some_name")
    binary_val = int_value.to_bytes(c_time.size, "little", signed=False)
    c_time.put(binary_val)
    assert c_time.value == value


@given(st.binary().filter(lambda x: len(x) != 4))
def test_dt_time_wrong_len(value: bytes):
    c_time = CTime("some_name")
    with pytest.raises(DataWrongLen):
        c_time.put(value)


@given(
    st.dates(min_value=datetime.date(year=1970, month=1, day=1), max_value=datetime.date(year=2106, month=2, day=7))
)
def test_dt_date(value: datetime.date):
    delta = value - datetime.date(year=1970, month=1, day=1)
    int_value = int(delta.total_seconds())
    c_date = CDate("some_name")
    binary_val = int_value.to_bytes(c_date.size, "little", signed=False)
    c_date.put(binary_val)
    assert c_date.value == value


@given(st.binary().filter(lambda x: len(x) != 4))
def test_dt_date_wrong_len(value: bytes):
    c_date = CDate("some_name")
    with pytest.raises(DataWrongLen):
        c_date.put(value)


@given(st.text(alphabet=string.ascii_letters, min_size=1), st.text(alphabet=string.ascii_letters, min_size=1))
def test_dt_string(value: str, garbage_str: str):
    binary_val = value.encode() + b"\x00" + garbage_str.encode()  # symbol end of string in some place
    c_string = CString("some_name", len(binary_val) - 1)
    c_string.put(binary_val)
    assert c_string.value == value


@given(st.binary(min_size=1))
def test_dt_string_wrong_len(value: bytes):
    c_string = CString("some_name", size=len(value))
    with pytest.raises(DataWrongLen):
        c_string.put(value)


@given(st.lists(elements=st.binary(min_size=1, max_size=1), min_size=1))
def test_dt_array_bool(value: list[bytes]):
    binary_val = b""
    expected = []
    for el in value:
        binary_val += el
        expected.append(False if el == b"" or el == b"\x00" else True)
    c_array = CArray("some_name", CBool("_"), len(value))
    c_array.put(binary_val)
    assert c_array.value == expected


@given(st.lists(elements=st.binary(min_size=1, max_size=1), min_size=1))
def test_dt_array_byte(value: list[bytes]):
    binary_val = b""
    for el in value:
        binary_val += el
    c_array = CArray("some_name", CByte("_"), len(value))
    c_array.put(binary_val)
    assert c_array.value == value


@given(st.lists(elements=st.binary(min_size=2, max_size=2), min_size=1))
def test_dt_array_word(value: list[bytes]):
    binary_val = b""
    for el in value:
        binary_val += el
    c_array = CArray("some_name", CWord("_"), len(value))
    c_array.put(binary_val)
    assert c_array.value == value


@given(st.lists(elements=st.integers(min_value=-32768, max_value=32767), min_size=1))
def test_dt_array_int(value: list[int]):
    binary_val = b""
    for el in value:
        binary_val += el.to_bytes(2, "little", signed=True)
    c_array = CArray("some_name", CInt("_"), len(value))
    c_array.put(binary_val)
    assert c_array.value == value


@given(st.lists(elements=st.integers(min_value=-2147483648, max_value=2147483647), min_size=1))
def test_dt_array_dint(value: list[int]):
    binary_val = b""
    for el in value:
        binary_val += el.to_bytes(4, "little", signed=True)
    c_array = CArray("some_name", CDInt("_"), len(value))
    c_array.put(binary_val)
    assert c_array.value == value


@given(st.lists(elements=st.floats(width=32, allow_nan=False), min_size=1))
def test_dt_array_real(value: list[float]):
    binary_val = b""
    for el in value:
        binary_val += bytearray(struct.pack("f", el))
    c_array = CArray("some_name", CReal("_"), len(value))
    c_array.put(binary_val)
    assert c_array.value == value


@given(st.binary(min_size=1))
def test_dt_array_wrong_len(value: bytes):
    c_array = CArray("some_name", CInt("_"), count=len(value) + 3)
    with pytest.raises(DataWrongLen):
        c_array.put(value)
