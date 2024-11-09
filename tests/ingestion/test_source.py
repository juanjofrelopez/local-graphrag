import pytest
from src.ingestion.source import CustomSource
from src.ingestion.loader import CustomLoader
from graphrag_sdk.source import AbstractSource

class TestCustomSource:
    def test_init(self):
        source = CustomSource("/test/path")
        assert isinstance(source.loader, CustomLoader)
        assert str(source.loader.path) == "/test/path"

    def test_inheritance(self):
        source = CustomSource("/test/path")
        assert isinstance(source, AbstractSource)

    @pytest.mark.parametrize("test_path", [
        "/test/path",
        "relative/path",
        "/test/path/with/file.txt"
    ])
    def test_path_handling(self, test_path):
        source = CustomSource(test_path)
        assert str(source.loader.path) == test_path