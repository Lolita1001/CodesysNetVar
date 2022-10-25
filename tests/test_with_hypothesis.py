import struct
import math
import pytest

from hypothesis import given, strategies as st

from codesys.data_types import CBool, CByte, CWord, CDWord, CLWord, CInt, CUInt, CDInt, CLInt, CUDInt, CULInt, CReal, \
    CLReal, CTime, CDate, CString, CArray
from utils.exeptions import DataWrongLen


@given(st.binary(min_size=1, max_size=1))
def test_dt_bool(value):
    c_bool = CBool('some_name')
    c_bool.put(value)
    if value == b'\x00' or value == b'':
        assert not c_bool.value
    else:
        assert c_bool.value


@given(st.binary().filter(lambda x: len(x) != 1))
def test_dt_bool_wrong_len(value):
    c_bool = CBool("some_name")
    with pytest.raises(DataWrongLen):
        c_bool.put(value)


@given(st.binary(min_size=1, max_size=1))
def test_dt_byte(value):
    c_byte = CByte("some_name")
    c_byte.put(value)
    assert c_byte.value == value


@given(st.binary().filter(lambda x: len(x) != 1))
def test_dt_byte_wrong_len(value):
    c_byte = CByte("some_name")
    with pytest.raises(DataWrongLen):
        c_byte.put(value)


@given(st.binary(min_size=2, max_size=2))
def test_dt_word(value):
    c_word = CWord("some_name")
    c_word.put(value)
    assert c_word.value == value


@given(st.binary().filter(lambda x: len(x) != 2))
def test_dt_word_wrong_len(value):
    c_word = CWord("some_name")
    with pytest.raises(DataWrongLen):
        c_word.put(value)


@given(st.binary(min_size=4, max_size=4))
def test_dt_dword(value):
    c_dword = CDWord("some_name")
    c_dword.put(value)
    assert c_dword.value == value


@given(st.binary().filter(lambda x: len(x) != 4))
def test_dt_dword_wrong_len(value):
    c_dword = CDWord("some_name")
    with pytest.raises(DataWrongLen):
        c_dword.put(value)


@given(st.binary(min_size=8, max_size=8))
def test_dt_lword(value):
    c_lword = CLWord("some_name")
    c_lword.put(value)
    assert c_lword.value == value


@given(st.binary().filter(lambda x: len(x) != 8))
def test_dt_lword_wrong_len(value):
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
def test_dt_int_wrong_len(value):
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
def test_dt_uint_wrong_len(value):
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
def test_dt_dint_wrong_len(value):
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
def test_dt_dint_wrong_len(value):
    c_udint = CUDInt("some_name")
    with pytest.raises(DataWrongLen):
        c_udint.put(value)


@given(st.integers())
def test_dt_lint(value: int):
    c_lint = CLInt("some_name")
    binary_val = value.to_bytes(c_lint.size, "little", signed=True)
    c_lint.put(binary_val)
    assert c_lint.value == value


@given(st.binary().filter(lambda x: len(x) != 8))
def test_dt_lint_wrong_len(value):
    c_lint = CLInt("some_name")
    with pytest.raises(DataWrongLen):
        c_lint.put(value)


@given(st.integers())
def test_dt_ulint(value: int):
    c_ulint = CULInt("some_name")
    binary_val = value.to_bytes(c_ulint.size, "little", signed=True)
    c_ulint.put(binary_val)
    assert c_ulint.value == value


@given(st.binary().filter(lambda x: len(x) != 8))
def test_dt_ulint_wrong_len(value):
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
def test_dt_real_wrong_len(value):
    c_real = CReal("some_name")
    with pytest.raises(DataWrongLen):
        c_real.put(value)


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
def test_dt_lreal_wrong_len(value):
    c_lreal = CLReal("some_name")
    with pytest.raises(DataWrongLen):
        c_lreal.put(value)
