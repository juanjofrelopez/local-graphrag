from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Iterator, List
from graphrag_sdk.document import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomLoader:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> Iterator[Document]:
        try:
            logger.info(f"Processing document: {self.path}")
            from unstructured.partition.auto import partition

            elements = partition(str(self.path))
            yield from [Document(str(element)) for element in elements]
        except Exception as e:
            logger.error(f"Error processing {self.path}: {str(e)}")
            raise
