from typing import TypeVar

from codesys.data_types import CType, CBool, CByte, CWord, CDWord, CLWord, CInt, CDInt, CLInt, CUInt, CUDInt, CULInt, CReal, CTime,\
    CDate, CString, CArray
from codesys.nvl_parser import NvlDeclarations


CodesysType = TypeVar('CodesysType', bound=CType)


def all_subclasses(cls) -> set[str]:
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])


def generate_inst_datatype(nvl_dec: list[NvlDeclarations]) -> list[CodesysType]:
    return [_get_inst_via_c_type(d_var['name'], d_var['type']) for d_var in nvl_dec]


def _get_inst_via_c_type(name: str, c_type: list[str] | str) -> CodesysType:
    c_type = [c_type] if isinstance(c_type, str) else c_type
    match name, *c_type:
        case name, 'BOOL':
            return CBool(name)
        case name, 'BYTE':
            return CByte(name)
        case name, 'WORD':
            return CWord(name)
        case name, 'DWORD':
            return CDWord(name)
        case name, 'LWORD':
            return CLWord(name)
        case name, 'INT':
            return CInt(name)
        case name, 'DINT':
            return CDInt(name)
        case name, 'LINT':
            return CLInt(name)
        case name, 'UINT':
            return CUInt(name)
        case name, 'UDINT':
            return CUDInt(name)
        case name, 'ULINT':
            return CULInt(name)
        case name, 'REAL':
            return CReal(name)
        case name, 'TIME':
            return CTime(name)
        case name, 'DATE':
            return CDate(name)
        case name, other if 'STRING' in other:
            size = int(other[7:-1])  # 'STRING(20)'
            return CString(name, size)
        case name, base_type, _, type_arr if 'ARRAY' in base_type:
            start, end = list(map(int, base_type[6:-1].split('..')))  # 'ARRAY[0..4]'
            return CArray(name, _get_inst_via_c_type('_', type_arr), end - start + 1)
        case _:
            raise AttributeError
