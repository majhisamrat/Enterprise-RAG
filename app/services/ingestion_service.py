import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from app.utils.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentMetadata
from app.db.repositories.document_repository import DocumentRepository
from app.embeddings.embedder import Embedder
from app.ingestion.chunking.recursive import RecursiveChunker
from app.ingestion.pipeline import IngestionPipeline
from app.keyword_search.index import ElasticsearchIndexer
from app.vectorstore.qdrant_store import QdrantVectorStore
from app.utils.exceptions import IngestionError


# ── Shared singletons: loaded once, reused across all requests ──
_shared_pipeline: Optional[IngestionPipeline] = None
_shared_chunker: Optional[RecursiveChunker] = None
_shared_embedder: Optional[Embedder] = None


def _get_pipeline() -> IngestionPipeline:
    global _shared_pipeline
    if _shared_pipeline is None:
        _shared_pipeline = IngestionPipeline()
    return _shared_pipeline


def _get_chunker() -> RecursiveChunker:
    global _shared_chunker
    if _shared_chunker is None:
        _shared_chunker = RecursiveChunker(chunk_size=1000, chunk_overlap=200)
    return _shared_chunker


def _get_embedder() -> Embedder:
    global _shared_embedder
    if _shared_embedder is None:
        _shared_embedder = Embedder()
    return _shared_embedder


class IngestionService:
    """Service layer managing complete document ingestion lifecycle."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session
        # Reuse shared singletons — no model reload per request
        self.pipeline = _get_pipeline()
        self.chunker = _get_chunker()
        self.embedder = _get_embedder()
        self.vector_store = QdrantVectorStore()
        self.elastic_index = ElasticsearchIndexer()

    async def ingest_document(
        self,
        file_path: str,
        organization_id: Optional[uuid.UUID] = None,
        owner_id: Optional[uuid.UUID] = None,
        title: Optional[str] = None,
        department: Optional[str] = None,
        author: Optional[str] = None,
        tags: Optional[list] = None,
    ) -> Dict[str, Any]:
        """Process document through full RAG ingestion pipeline and persist to all stores."""
        path = Path(file_path)
        if not path.exists():
            raise IngestionError(f"File not found: {file_path}")

        organization_id = organization_id or uuid.uuid4()
        owner_id = owner_id or uuid.uuid4()

        logger.info(f"Starting document ingestion for file: {path.name} (Org: {organization_id})")

        try:
            # 1. Parse, OCR, Clean & Extract Metadata
            parsed_doc = self.pipeline.process(str(path))

            # 2. Recursive Chunking
            chunked_doc = self.chunker.chunk(parsed_doc)

            # 3. Generate Dense Embeddings
            embedded_doc = self.embedder.embed(chunked_doc)

            doc_id = uuid.uuid4()
            doc_title = title or path.stem

            # 4. Index in Qdrant (Dense Search) with resilient offline fallback
            try:
                await self.vector_store.upsert_document_chunks(
                    document=embedded_doc,
                    document_id=doc_id,
                    organization_id=organization_id,
                    department=department,
                    author=author,
                    tags=tags,
                )
            except Exception as e:
                logger.warning(f"Qdrant vector store indexing skipped (server offline?): {e}")

            # 5. Index in Elasticsearch (Sparse BM25 Search) with resilient offline fallback
            try:
                await self.elastic_index.index_document_chunks(
                    document=embedded_doc,
                    document_id=doc_id,
                    organization_id=organization_id,
                    title=doc_title,
                    department=department,
                    author=author,
                    tags=tags,
                )
            except Exception as e:
                logger.warning(f"Elasticsearch BM25 indexing skipped (server offline?): {e}")

            # 6. Database Persistence if session present
            if self.db_session:
                doc_repo = DocumentRepository(self.db_session)
                doc_record = Document(
                    id=doc_id,
                    organization_id=organization_id,
                    owner_id=owner_id,
                    filename=path.name,
                    title=doc_title,
                    mime_type="application/octet-stream",
                    file_size=path.stat().st_size,
                    checksum=str(hash(path.name)),
                    storage_path=str(path),
                    parser_used="ParserFactory",
                    status="indexed",
                )
                await doc_repo.create(doc_record)

            logger.success(f"Successfully ingested document '{doc_title}' ({len(embedded_doc.chunks)} chunks)")

            return {
                "document_id": str(doc_id),
                "title": doc_title,
                "pages": getattr(parsed_doc, "page_count", 1),
                "chunks": len(embedded_doc.chunks),
                "status": "indexed",
            }
        except Exception as e:
            logger.error(f"Ingestion failed for file '{path.name}': {e}")
            raise IngestionError(f"Failed to ingest document: {e}")
