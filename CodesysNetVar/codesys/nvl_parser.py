import ipaddress

from typing import TypedDict
from pathlib import Path

from pydantic import BaseModel
from loguru import logger
import xml.etree.ElementTree as Et

from exeptions import ListIdMustBeUniq, AcknowledgeMustBeUniq, ChecksumMustBeUniq


class NvlDeclarations(TypedDict, total=False):
    name: str
    type: list[str]


class NvlOptions(BaseModel):
    declarations: list[NvlDeclarations]
    list_id: int
    pack: bool
    checksum: bool
    acknowledge: bool
    ip_address: ipaddress.IPv4Address
    port: int


class NvlParser:
    list_id = []

    def __init__(self, path: Path | list[Path]):
        """
        Parser NVL configuration file. Parse file and get variables from declarations and some settings
        :param path: path to the nvl configuration file
        """
        self._path: Path = path

    @staticmethod
    def get_root_of_tree(path: Path) -> Et.Element:
        _my_tree = Et.parse(path)
        return _my_tree.getroot()

    @staticmethod
    def get_declarations_text_from_root(root_element: Et.Element) -> str:
        return root_element.find('Declarations').text

    @staticmethod
    def get_netvar_settings_element_from_root(root_element: Et.Element) -> Et.Element:
        return root_element.find('NetvarSettings')

    @staticmethod
    def get_var_global_strings(declarations_text: str) -> list[str]:
        pos_start = declarations_text.find('VAR_GLOBAL') + len('VAR_GLOBAL\n')
        pos_end = declarations_text.find('\nEND_VAR')
        return declarations_text[pos_start:pos_end].split('\n')

    @staticmethod
    def nvl_declaration_filler(var_strings: list[str]) -> list[NvlDeclarations]:
        nvl_declaration: list[NvlDeclarations] = []
        for s in var_strings:
            v_name, v_type = s.split(':')
            v_name = v_name.replace('\t', '').replace(' ', '')
            v_type = list(filter(lambda x: len(x) > 0, v_type.replace(';', '').split(' ')))
            if v_name[:2] != '//':
                nvl_declaration.append(NvlDeclarations(name=v_name, type=v_type))
        return nvl_declaration

    def parse(self) -> NvlOptions:
        parse_result = {}
        root = self.get_root_of_tree(self._path)
        parse_result['declarations'] = self.nvl_declaration_filler(
                                            self.get_var_global_strings(
                                                self.get_declarations_text_from_root(root)))

        element_netvar_settings = self.get_netvar_settings_element_from_root(root)
        parse_result['list_id'] = element_netvar_settings.find('ListIdentifier').text
        parse_result['pack'] = element_netvar_settings.find('Pack').text
        parse_result['checksum'] = element_netvar_settings.find('Checksum').text
        parse_result['acknowledge'] = element_netvar_settings.find('Acknowledge').text

        element_protocol_settings = element_netvar_settings.find('ProtocolSettings')
        parse_result['ip_address'] = element_protocol_settings[0].attrib['Value']
        parse_result['port'] = element_protocol_settings[1].attrib['Value']

        nvl_options = NvlOptions.parse_obj(parse_result)
        self.check_settings(nvl_options)
        self.check_uniq_list_id(nvl_options.list_id)
        return nvl_options

    @staticmethod
    def check_settings(options: NvlOptions) -> None:
        """
        :return None or AttributeError
        """
        if options.acknowledge:
            raise AcknowledgeMustBeUniq('Attribute "Acknowledge" must be False')
        if options.checksum:
            raise ChecksumMustBeUniq('Attribute "Checksum" must be False')
        if not options.pack:
            logger.warning('Recommended set attribute "Pack" for more speed communication')

    @classmethod
    def check_uniq_list_id(cls, list_id):
        if list_id in cls.list_id:
            raise ListIdMustBeUniq("List id in NVL settings must be uniq")
        cls.list_id.append(list_id)
