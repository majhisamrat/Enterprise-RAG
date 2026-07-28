from abc import ABC, abstractmethod

from app.ingestion.schemas import ParsedDocument, ChunkedDocument

class BaseChunker(ABC):

    @abstractmethod
    def chunk(self,document: ParsedDocument) -> ChunkedDocument :

        raise NotImplementedError