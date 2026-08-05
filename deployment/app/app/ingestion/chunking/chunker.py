from loguru import logger

from app.ingestion.chunking.recursive import RecursiveChunker
from app.ingestion.chunking.semantic import SemanticChunker
from app.ingestion.chunking.parent_child import ParentChildChunker
from app.ingestion.chunking.hierarchical import HierarchicalChunker
from app.ingestion.chunking.table_aware import TableAwareChunker
from app.ingestion.chunking.markdown import MarkdownChunker
from app.ingestion.schemas import (
    ChunkedDocument,
    ParsedDocument,
)


class Chunker:

    def __init__(self, strategy: str = "recursive"):

        self.strategy = strategy.lower()

        self.chunkers = {
            "recursive": RecursiveChunker(),
            "semantic": SemanticChunker(),
            "parent_child": ParentChildChunker(),
            "hierarchical": HierarchicalChunker(),
            "table": TableAwareChunker(),
            "markdown": MarkdownChunker(),
        }

        if self.strategy not in self.chunkers:
            raise ValueError(
                f"Unsupported chunking strategy: {strategy}"
            )

    def process(
        self,
        document: ParsedDocument,
    ) -> ChunkedDocument:

        logger.info(
            f"Using '{self.strategy}' chunking strategy."
        )

        return self.chunkers[self.strategy].chunk(document)