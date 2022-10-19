import ipaddress

from typing import TypedDict
from pathlib import Path

from pydantic import BaseModel
from loguru import logger
import xml.etree.ElementTree as Et


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
    def __init__(self, path: Path | list[Path]):
        """
        Parser NVL configuration file. Parse file and get variables from declarations and some settings
        :param path: path to the nvl configuration file
        """
        self._path: Path = path
        self.options: NvlOptions = self.parse(self._path)
        self.check_settings()

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

    def parse(self, nvl_path: Path) -> NvlOptions:
        parse_result = {}
        root = self.get_root_of_tree(nvl_path)
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

        return NvlOptions.parse_obj(parse_result)

    def check_settings(self) -> None:
        """
        :return None or AssertionError
        """
        assert not self.options.acknowledge, 'Attribute "Acknowledge" must be False'
        assert not self.options.checksum, 'Attribute "Checksum" must be False'
        if not self.options.pack:
            logger.warning('Recommended set attribute "Pack" for more speed communication')
