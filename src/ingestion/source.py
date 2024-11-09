from graphrag_sdk.source import AbstractSource
from src.ingestion.loader import CustomLoader


class CustomSource(AbstractSource):
    def __init__(self, path: str):
        super().__init__(path)
        self.loader = CustomLoader(self.path)
