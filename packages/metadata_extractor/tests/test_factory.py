import pytest
from metadata_extractor.factory import ExtractorFactory
from metadata_extractor.interfaces import LanguageExtractor
from metadata_extractor.models import FileMetadata
from parser_core.models import AiekpAstNode


class DummyExtractor(LanguageExtractor):
    def extract(self, ast_root: AiekpAstNode, file_path: str) -> FileMetadata:
        return FileMetadata(file_path=file_path, language="dummy")


def test_register_and_get_extractor():
    factory = ExtractorFactory()
    dummy = DummyExtractor()

    # Should work with or without dot
    factory.register_extractor(".dummy", dummy)
    factory.register_extractor("test", dummy)

    assert factory.get_extractor(".dummy") is dummy
    assert factory.get_extractor("dummy") is dummy
    assert factory.get_extractor(".test") is dummy
    assert factory.get_extractor("test") is dummy


def test_get_unregistered_extractor():
    factory = ExtractorFactory()
    with pytest.raises(
        ValueError, match="No extractor registered for extension: .unknown"
    ):
        factory.get_extractor(".unknown")
