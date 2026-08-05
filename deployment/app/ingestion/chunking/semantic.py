from app.ingestion.chunking.base import BaseChunker


class SemanticChunker(BaseChunker):

    def chunk(self, document):
        
        raise NotImplementedError()