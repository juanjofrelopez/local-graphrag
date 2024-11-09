import pytest
from pathlib import Path
from unittest.mock import patch
from src.ingestion.loader import CustomLoader
from graphrag_sdk.document import Document

@pytest.fixture
def sample_text_file(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("Sample content for testing")
    return file_path

@pytest.fixture
def mock_partition():
    with patch('unstructured.partition.auto.partition') as mock:
        mock.return_value = ["Element 1", "Element 2"]
        yield mock

class TestCustomLoader:
    def test_init(self):
        path = Path("/test/path")
        loader = CustomLoader(path)
        assert loader.path == path

    def test_load_success(self, sample_text_file, mock_partition):
        loader = CustomLoader(sample_text_file)
        documents = list(loader.load())

        assert len(documents) == 2
        assert all(isinstance(doc, Document) for doc in documents)
        mock_partition.assert_called_once_with(str(sample_text_file))

    def test_load_file_not_found(self):
        loader = CustomLoader(Path("/nonexistent/path"))
        with pytest.raises(Exception):
            list(loader.load())

    @patch('unstructured.partition.auto.partition')
    def test_load_partition_error(self, mock_partition, sample_text_file):
        mock_partition.side_effect = Exception("Partition error")
        loader = CustomLoader(sample_text_file)

        with pytest.raises(Exception) as exc_info:
            list(loader.load())
        assert "Partition error" in str(exc_info.value)
