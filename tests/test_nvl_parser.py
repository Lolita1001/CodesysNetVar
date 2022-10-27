from pathlib import Path
import pytest

from hypothesis import given, strategies as st

from codesys.nvl_parser import NvlParser, NvlDeclarations
from utils.exeptions import NVLFileNotFound, ListIdMustBeUniq, IpAndPortWrong, AcknowledgeMustBeFalse, \
    ChecksumMustBeFalse

BASE_DIRECTORY = Path(__file__).parent

path_nvls_ok = list(Path("set_of_nvl_files_for_test").glob("*_ok_*.gvl"))
path_nvls_not_ok = list(Path("set_of_nvl_files_for_test").glob("*_notok_*.gvl"))
nvl_declaration_reference = [NvlDeclarations(name=_n, type=_t) for _n, _t in [("sinus", ["REAL"]),
                                                                              ("cosine", ["REAL"]),
                                                                              ("some_word", ["WORD"]),
                                                                              ("integer", ["INT"]),
                                                                              ("my_time", ["TIME"]),
                                                                              ("my_date", ["DATE"]),
                                                                              ("my_string20", ["STRING(20)"]),
                                                                              ("my_array", ["ARRAY[0..4]", "INT"]),
                                                                              ]]


class TestNvlParser:
    def setup(self):
        pass

    def test_file_not_exist(self):
        with pytest.raises(NVLFileNotFound):
            nvl_parser = NvlParser(Path("not_exist_file.gvl"))

    @pytest.mark.parametrize('path', path_nvls_ok)
    def test_parser_ok(self, path):
        nvl_parser = NvlParser(path)
        nvl_options = nvl_parser.parse()
        assert nvl_options.declarations == nvl_declaration_reference

    @pytest.mark.parametrize('path', path_nvls_ok[:1])
    def test_parser_not_uniq(self, path):
        nvl_parser_1 = NvlParser(path)
        nvl_options_1 = nvl_parser_1.parse()
        nvl_parser_2 = NvlParser(path)
        with pytest.raises(ListIdMustBeUniq):
            nvl_options_2 = nvl_parser_2.parse()

    @pytest.mark.parametrize('path', path_nvls_not_ok)
    def test_parser_not_ok(self, path):
        nvl_parser = NvlParser(path)
        with pytest.raises((AcknowledgeMustBeFalse, ChecksumMustBeFalse, IpAndPortWrong)):  # noqa
            nvl_options = nvl_parser.parse()

    def teardown(self):
        NvlParser.list_id = []
