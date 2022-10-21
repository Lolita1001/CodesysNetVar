from loguru import logger

from codesys.nvl_parser import NvlOptions, NvlDeclarations
from codesys.data_types import (
    CBool,
    CByte,
    CWord,
    CDWord,
    CLWord,
    CInt,
    CDInt,
    CLInt,
    CUInt,
    CUDInt,
    CULInt,
    CReal,
    CTime,
    CDate,
    CString,
    CArray,
    CodesysType,
    CTypeDeclaration,
)
from network.parser import Rcv
from utils.exeptions import UnsupportedType
from db_connector import create_table_and_orm_class


class DataPacker:
    def __init__(self, nvl: NvlOptions):
        """
        prepare data types and packing data to variables classes
        :param nvl: nvl config
        """
        self.nvl = nvl
        self.c_types_declarations = self.generate_instance_datatype(self.nvl.declarations)
        self.OrmModel = create_table_and_orm_class(self.nvl.list_id, self.c_types_declarations)
        # logger.debug(self)

    def generate_instance_datatype(self, declaration: list[NvlDeclarations]) -> CTypeDeclaration:
        c_types_declarations = CTypeDeclaration()
        for dec_var in declaration:
            c_types_declarations.append(self._get_inst_via_c_type(dec_var["name"], dec_var["type"]))
        return c_types_declarations

    def _get_inst_via_c_type(self, name: str, c_type: list[str] | str) -> CodesysType:
        c_type = [c_type] if isinstance(c_type, str) else c_type
        match name, *c_type:
            case name, "BOOL":
                return CBool(name)
            case name, "BYTE":
                return CByte(name)
            case name, "WORD":
                return CWord(name)
            case name, "DWORD":
                return CDWord(name)
            case name, "LWORD":  # noqa
                return CLWord(name)
            case name, "INT":
                return CInt(name)
            case name, "DINT":
                return CDInt(name)
            case name, "LINT":
                return CLInt(name)
            case name, "UINT":
                return CUInt(name)
            case name, "UDINT":  # noqa
                return CUDInt(name)
            case name, "ULINT":
                return CULInt(name)
            case name, "REAL":
                return CReal(name)
            case name, "TIME":
                return CTime(name)
            case name, "DATE":
                return CDate(name)
            case name, other if "STRING" in other:
                size = int(other[7:-1])  # 'STRING(20)'
                return CString(name, size)
            case name, base_type, _, type_arr if "ARRAY" in base_type:
                start, end = list(map(int, base_type[6:-1].split("..")))  # 'ARRAY[0..4]'
                return CArray(name, self._get_inst_via_c_type("_", type_arr), end - start + 1)
            case _:
                raise UnsupportedType(f"Data type {c_type} is not support")

    def put_data(self, rcv: Rcv) -> None:
        try:
            if self.nvl.pack:
                is_last_packet = self._put_data_pack(rcv.data_raw)
            else:
                is_last_packet = self._put_data_unpack(rcv.n_package_in_list, rcv.data_raw)
            logger.debug(f"DataPacker of {self.nvl.list_id} ID list: The data are put in Codesys class instances")
            logger.debug("\n".join([c_type.__repr__() for c_type in self.c_types_declarations]))
            if is_last_packet and self.OrmModel:
                self.write_to_orm()
        except Exception as ex:
            logger.exception(ex)
            self.clear_data()

    def _put_data_unpack(self, number: int, data_raw: bytes) -> bool:
        self.c_types_declarations[number].put(data_raw)
        return number + 1 == self.c_types_declarations.__len__() and all(
            [c_type.value for c_type in self.c_types_declarations]
        )

    def _put_data_pack(self, r_data: bytes) -> bool:
        start = 0
        for c_type in self.c_types_declarations:
            c_type.put(r_data[start: start + c_type.size])
            start += c_type.size
        return True

    def write_to_orm(self) -> None:
        orm_model = self.OrmModel()
        for c_type in self.c_types_declarations:
            orm_model.update_value(c_type)
        logger.debug(f"Start writing orm class to DB")
        orm_model.write_to_db()

    def clear_data(self) -> None:
        for c_type in self.c_types_declarations:
            c_type.clear()

    def __repr__(self) -> str:
        return "\n".join([c_type.__repr__() for c_type in self.c_types_declarations])
