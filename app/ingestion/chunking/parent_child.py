from app.ingestion.chunking.base import BaseChunker


class ParentChildChunker(BaseChunker):

    def chunk(self, document):
        raise NotImplementedError(
            "Parent-child chunking will be implemented later."
        )