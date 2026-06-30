import pytest
from parser_core.factory import ParserFactory
from parser_core.interfaces import LanguageParser
from parser_core.models import AiekpAstNode


class DummyParser(LanguageParser):
    @property
    def supported_extensions(self):
        return [".dummy"]

    def parse(self, file_content: bytes) -> AiekpAstNode:
        return AiekpAstNode(
            type="dummy_root",
            text="dummy",
            start_byte=0,
            end_byte=5,
            start_point=(0, 0),
            end_point=(0, 5),
        )


def test_parser_registration():
    factory = ParserFactory()
    factory.register_parser(DummyParser())

    parser = factory.get_parser(".dummy")
    assert isinstance(parser, DummyParser)


def test_unsupported_extension_raises_error():
    factory = ParserFactory()

    with pytest.raises(ValueError):
        factory.get_parser(".unknown")
