from app.ingestion.chunking.base import BaseChunker


class HierarchicalChunker(BaseChunker):
    """
    Hierarchical chunking.

    Phase 7.2

    Splits documents into:

        Document
            ├── Sections
            │      ├── Paragraphs
            │      │      ├── Chunks

    Useful for enterprise manuals.
    """

    def chunk(self, document):
        raise NotImplementedError(
            "Hierarchical chunking will be implemented later."
        )