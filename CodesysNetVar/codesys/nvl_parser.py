import ipaddress

from typing import TypedDict, Any
from pathlib import Path

from pydantic import BaseModel
from loguru import logger
import xml.etree.ElementTree as Et

from utils.exeptions import ListIdMustBeUniq, AcknowledgeMustBeUniq, ChecksumMustBeUniq, IpAndPortWrong, NodeNotFound
from settings.settings import settings


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
    list_id: list[int] = []

    def __init__(self, path: Path):
        """
        Parser NVL configuration file. Parse file and get settings and declarations
        :param path: path to the nvl configuration file
        """
        self._path = path

    @staticmethod
    def get_root_of_tree(path: Path) -> Et.Element:
        _my_tree = Et.parse(path)
        return _my_tree.getroot()

    @staticmethod
    def get_element_by_text_find_from_node(node: Et.Element, text_find: str) -> Et.Element:
        node_by_text = node.find(text_find)
        if node_by_text is None:
            raise NodeNotFound(f"Node {text_find} not found")
        return node_by_text

    @staticmethod
    def get_text_from_node(node: Et.Element) -> str:
        text = node.text
        if text is None:
            raise NodeNotFound(f"Node {node} don't have text")
        return text

    @staticmethod
    def get_var_global_strings(declarations_text: str) -> list[str]:
        pos_start = declarations_text.find("VAR_GLOBAL") + len("VAR_GLOBAL\n")
        pos_end = declarations_text.find("\nEND_VAR")
        return declarations_text[pos_start:pos_end].split("\n")

    @staticmethod
    def nvl_declaration_filler(var_strings: list[str]) -> list[NvlDeclarations]:
        nvl_declaration: list[NvlDeclarations] = []
        for s in var_strings:
            v_name, raw_v_type = s.split(":")
            v_name = v_name.replace("\t", "").replace(" ", "")
            v_type = list(filter(lambda x: len(x) > 0, raw_v_type.replace(";", "").split(" ")))
            if v_name[:2] != "//":
                nvl_declaration.append(NvlDeclarations(name=v_name, type=v_type))
        return nvl_declaration

    def parse(self) -> NvlOptions:
        parse_result: Any = {}
        root = self.get_root_of_tree(self._path)
        parse_result["declarations"] = self.nvl_declaration_filler(
            self.get_var_global_strings(
                self.get_text_from_node(self.get_element_by_text_find_from_node(root, "Declarations"))
            )
        )

        element_netvar_settings = self.get_element_by_text_find_from_node(root, "NetvarSettings")  # noqa
        parse_result["list_id"] = self.get_text_from_node(
            self.get_element_by_text_find_from_node(element_netvar_settings, "ListIdentifier")
        )
        parse_result["pack"] = self.get_text_from_node(
            self.get_element_by_text_find_from_node(element_netvar_settings, "Pack")
        )
        parse_result["checksum"] = self.get_text_from_node(
            self.get_element_by_text_find_from_node(element_netvar_settings, "Checksum")
        )
        parse_result["acknowledge"] = self.get_text_from_node(
            self.get_element_by_text_find_from_node(element_netvar_settings, "Acknowledge")
        )

        element_protocol_settings = self.get_element_by_text_find_from_node(
            element_netvar_settings, "ProtocolSettings"
        )
        parse_result["ip_address"] = element_protocol_settings[0].attrib["Value"]
        parse_result["port"] = element_protocol_settings[1].attrib["Value"]

        nvl_options = NvlOptions.parse_obj(parse_result)
        self.check_settings(nvl_options)
        self.check_uniq_list_id(nvl_options.list_id)
        logger.info(f'Result parse of nvl file "{self._path}":')
        logger.info(nvl_options)
        return nvl_options

    @staticmethod
    def check_settings(options: NvlOptions) -> None:
        if options.acknowledge:
            raise AcknowledgeMustBeUniq('Attribute "Acknowledge" must be False')
        if options.checksum:
            raise ChecksumMustBeUniq('Attribute "Checksum" must be False')
        if not options.pack:
            logger.warning('Recommended set attribute "Pack" for more speed communication')
        if options.ip_address != settings.network.local_ip or options.port != settings.network.local_port:
            raise IpAndPortWrong("IP address and port must be equal from .env and NVLs config")

    @classmethod
    def check_uniq_list_id(cls, list_id: int) -> None:
        if list_id in cls.list_id:
            raise ListIdMustBeUniq("List id in NVL settings must be uniq")
        cls.list_id.append(list_id)
