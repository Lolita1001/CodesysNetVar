from loguru import logger

from codesys.nvl_parser import NvlOptions, NvlDeclarations
from codesys.data_types import CBool, CByte, CWord, CDWord, CLWord, CInt, CDInt, CLInt, CUInt, CUDInt, CULInt, CReal, \
    CTime, CDate, CString, CArray, CType, CodesysType
from network.parser import Rcv


class CTypeDeclaration(list[CType]):
    def append(self, obj) -> None:
        assert issubclass(obj.__class__, CType), 'Appended object is not subclass of Codesys'
        super().append(obj)  # noqa

    def get_via_name(self, name: str):
        for i in self:
            if i.name == name:
                return i
        return None


class DataPacker:
    def __init__(self, nvl: NvlOptions):
        """
        prepare data types and packing data to variables classes
        :param nvl: nvl config
        """
        self.nvl = nvl
        self.c_types_declarations = self.generate_instance_datatype(self.nvl.declarations)
        self.callback = None #partial(write_to_db, create_table(self.nvl.list_id, self.data))
        # logger.debug(self)

    def generate_instance_datatype(self, declaration: list[NvlDeclarations]):
        c_types_declarations = CTypeDeclaration()
        for dec_var in declaration:
            c_types_declarations.append(self._get_inst_via_c_type(dec_var['name'], dec_var['type']))
        return c_types_declarations

    def _get_inst_via_c_type(self, name: str, c_type: list[str] | str) -> CodesysType:
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
                return CArray(name, self._get_inst_via_c_type('_', type_arr), end - start + 1)

    def put_data(self, rcv: Rcv):
        try:
            if self.nvl.pack:
                self._put_data_pack(rcv.data_raw)
            else:
                self._put_data_unpack(rcv.n_package_in_list, rcv.data_raw)
        except Exception:
            logger.exception('')
            self.clear_data()

    def _put_data_unpack(self, number: int, data_raw: bytes):
        self.c_types_declarations[number].put(data_raw)
        logger.debug('Put data from each packet...')
        logger.debug(f'Raw: {data_raw}')
        logger.debug(self.c_types_declarations[number])
        if self.callback and \
                number + 1 == self.c_types_declarations.__len__() and \
                all([d.value for d in self.c_types_declarations]):
            self.callback(self.c_types_declarations)
            logger.debug('Recorded...')
            logger.debug(self)

    def _put_data_pack(self, r_data: bytes):
        start = 0
        for c_type in self.c_types_declarations:
            c_type.put(r_data[start:start+c_type.size])

            logger.debug('Put data from part of packet...')
            logger.debug(f'Raw: {r_data[start:start+c_type.size]}')
            logger.debug(c_type)

            start += c_type.size
        logger.debug('Put data from all packet...')
        logger.debug(f'Raw: {r_data}')
        logger.debug(self)

        if self.callback:
            self.callback(self.c_types_declarations)
            logger.debug('Recorded...')
            logger.debug(self.c_types_declarations)

    def clear_data(self):
        for c_type in self.c_types_declarations:
            c_type.clear()

    def __repr__(self):
        return '\n'.join([c_type.__repr__() for c_type in self.c_types_declarations])
