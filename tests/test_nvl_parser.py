from pathlib import Path
import pytest

from hypothesis import given, strategies as st

from codesys.nvl_parser import NvlParser
from utils.exeptions import NVLFileNotFound, ListIdMustBeUniq, IpAndPortWrong, AcknowledgeMustBeFalse, \
    ChecksumMustBeFalse

BASE_DIRECTORY = Path(__file__).parent

path_nvls_ok = list(Path("set_of_nvl_files_for_test").glob("*_ok_*.gvl"))
path_nvls_not_ok = list(Path("set_of_nvl_files_for_test").glob("*_notok_*.gvl"))


class TestNvlParser:
    def setup(self):
        pass

    def test_file_not_exist(self):
        with pytest.raises(NVLFileNotFound):
            nvl_parser = NvlParser(Path("not_exist_file.gvl"))

    def test_parser_ok(self):
        for nvl_path in path_nvls_ok:
            nvl_parser = NvlParser(nvl_path)
            nvl_options = nvl_parser.parse()

    def test_parser_not_uniq(self):
        nvl_path = path_nvls_ok[0]
        nvl_parser_1 = NvlParser(nvl_path)
        nvl_options_1 = nvl_parser_1.parse()
        nvl_parser_2 = NvlParser(nvl_path)
        with pytest.raises(ListIdMustBeUniq):
            nvl_options_2 = nvl_parser_2.parse()

    def test_parser_not_ok(self):
        for nvl_path in path_nvls_not_ok:
            nvl_parser = NvlParser(nvl_path)
            with pytest.raises((AcknowledgeMustBeFalse, ChecksumMustBeFalse, IpAndPortWrong)):  # noqa
                nvl_options = nvl_parser.parse()

    def teardown(self):
        NvlParser.list_id = []
