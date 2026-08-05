from app.ingestion.chunking.base import BaseChunker


class TableAwareChunker(BaseChunker):
    """
    Table-aware chunking.

    Phase 7.2

    Preserves rows and columns instead
    of splitting tables incorrectly.
    """

    def chunk(self, document):
        raise NotImplementedError(
            "Table-aware chunking will be implemented later."
        )