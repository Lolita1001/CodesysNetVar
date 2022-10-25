import pytest

from codesys.data_types import CBool, CByte, CWord, CDWord, CLWord, CInt, CUInt, CDInt, CLInt, CUDInt, CULInt, CReal, \
    CLReal, CTime, CDate, CString, CArray
from utils.exeptions import DataWrongLen


@pytest.mark.parametrize('name, value, expected', [
    ('some_name', b'\x00', False),
    ('some_name', b'\x01', True),
    ('some_name', b'\x02', True),
    ('some_name', b'\x03', True),
    ('some_name', b'\xff', True),
    ('', b'\x00', False),
])
def test_dt_bool(name, value, expected):
    c_bool = CBool(name)
    c_bool.put(value)
    assert c_bool.value == expected


@pytest.mark.parametrize('name, value', [
    ('some_name', b''),
    ('some_name', b'\x00\x00'),
    ('some_name', b'\x02\x02\x02'),
    ('some_name', b'123456789'),
])
def test_dt_bool_wrong_len(name, value):
    c_bool = CBool(name)
    with pytest.raises(DataWrongLen):
        c_bool.put(value)


@pytest.mark.parametrize('name, value', [
    ('some_name', b'\x00'),
    ('some_name', b'\x01'),
    ('some_name', b'\x02'),
    ('some_name', b'\x03'),
    ('some_name', b'\xff'),
    ('', b'\x00'),
])
def test_dt_byte(name, value):
    c_byte = CByte(name)
    c_byte.put(value)
    assert c_byte.value == value


@pytest.mark.parametrize('name, value', [
    ('some_name', b''),
    ('some_name', b'\x00\x00'),
    ('some_name', b'\x02\x02\x02'),
    ('some_name', b'123456789'),
])
def test_dt_byte_wrong_len(name, value):
    c_byte = CByte(name)
    with pytest.raises(DataWrongLen):
        c_byte.put(value)


@pytest.mark.parametrize('name, value', [
    ('some_name', b'\x00\x00'),
    ('some_name', b'\x01\x01'),
    ('some_name', b'\x02\x10'),
    ('some_name', b'\x03\x20'),
    ('some_name', b'\xff\x50'),
    ('', b'\x50\x50'),
])
def test_dt_word(name, value):
    c_word = CWord(name)
    c_word.put(value)
    assert c_word.value == value


@pytest.mark.parametrize('name, value', [
    ('some_name', b''),
    ('some_name', b'\x01'),
    ('some_name', b'\x02\x10\x10'),
    ('some_name', b'\x03\x20\x10\x10'),
    ('some_name', b'\xff\x50\x10\x10\x10'),
    ('', b'\x50\x50\x10\x10\x10\x10\x10\x10\x10'),
])
def test_dt_word_wrong_len(name, value):
    c_word = CWord(name)
    with pytest.raises(DataWrongLen):
        c_word.put(value)


@pytest.mark.parametrize('name, value', [
    ('some_name', b'\x00\x00\x00\x00'),
    ('some_name', b'\x01\x00\x00\x01'),
    ('some_name', b'\x00\x00\x02\x10'),
    ('some_name', b'\x00\x00\x03\x20'),
    ('some_name', b'\xff\x00\x00\x50'),
    ('', b'\x50\x50\x00\x00'),
])
def test_dt_word(name, value):
    c_dword = CDWord(name)
    c_dword.put(value)
    assert c_dword.value == value


@pytest.mark.parametrize('name, value', [
    ('some_name', b''),
    ('some_name', b'\x01'),
    ('some_name', b'\x02\x10'),
    ('some_name', b'\x02\x10\x10'),
    ('some_name', b'\x03\x20\x10\x10\x00'),
    ('some_name', b'\xff\x50\x10\x10\x10\x00\x00'),
    ('', b'\x50\x50\x10\x10\x10\x10\x10\x10\x10\x00'),
])
def test_dt_dword_wrong_len(name, value):
    c_dword = CDWord(name)
    with pytest.raises(DataWrongLen):
        c_dword.put(value)


@pytest.mark.parametrize('name, value', [
    ('some_name', b'\x00\x00\x00\x00\x00\x00\x00\x00'),
    ('some_name', b'\x01\x00\x00\x00\x00\x00\x00\x01'),
    ('some_name', b'\x00\x00\x00\x02\x10\x00\x02\x10'),
    ('some_name', b'\x00\x00\x03\x00\x00\x02\x10\x20'),
    ('some_name', b'\xff\x00\x00\x02\x10\x00\x00\x50'),
    ('', b'\x50\x00\x00\x02\x10\x50\x00\x00'),
])
def test_dt_word(name, value):
    c_lword = CLWord(name)
    c_lword.put(value)
    assert c_lword.value == value


@pytest.mark.parametrize('name, value', [
    ('some_name', b''),
    ('some_name', b'\x01'),
    ('some_name', b'\x02\x10'),
    ('some_name', b'\x02\x10\x10'),
    ('some_name', b'\x03\x20\x10\x10'),
    ('some_name', b'\x03\x20\x10\x10\x00'),
    ('some_name', b'\xff\x50\x10\x10\x10\x00'),
    ('some_name', b'\xff\x50\x10\x10\x10\x00\x00'),
    ('some_name', b'\xff\x50\x10\x10\x10\x00\x00\x00\x00'),
    ('', b'\x50\x50\x10\x10\x10\x10\x10\x10\x10\x00\x00\x00'),
])
def test_dt_lword_wrong_len(name, value):
    c_lword = CLWord(name)
    with pytest.raises(DataWrongLen):
        c_lword.put(value)
