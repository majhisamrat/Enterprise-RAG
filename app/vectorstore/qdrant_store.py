import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.utils.logger import logger
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PayloadSchemaType, PointStruct, VectorParams

from app.config import settings
from app.ingestion.schemas import ChunkedDocument
from app.vectorstore.base import BaseVectorStore
from app.vectorstore.qdrant_client import QdrantConnection


class QdrantVectorStore(BaseVectorStore):
    """Production-grade Qdrant Vector Store with circuit breaker for offline resilience."""

    def __init__(self, collection_name: str = settings.QDRANT_COLLECTION):
        self.collection_name = collection_name
        self._client = None

    @property
    def client(self):
        if self._client is None:
            if not QdrantConnection.is_available():
                return None
            self._client = QdrantConnection.get_client()
            self._ensure_collection()
            # _ensure_collection trips the global circuit breaker on a failed
            # connection.  Do not immediately make a second timed-out call.
            if not QdrantConnection.is_available():
                self._client = None
                return None
        return self._client

    def _ensure_collection(self):
        """Ensure vector collection exists in Qdrant with proper index configuration."""
        if self._client is None:
            return
        client = self._client
        try:
            collections = client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                logger.info(f"Creating Qdrant collection '{self.collection_name}'...")
                client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE,
                    ),
                )
                # Create payload index for fast tenant & department filtering
                client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="organization_id",
                    field_schema=PayloadSchemaType.KEYWORD,
                )
                client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="department",
                    field_schema=PayloadSchemaType.KEYWORD,
                )
        except Exception as e:
            logger.warning(f"Qdrant collection initialization warning (server offline?): {e}")
            QdrantConnection.mark_offline()

    async def upsert_document_chunks(
        self,
        document: ChunkedDocument,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
        page_number: int = 1,
        author: Optional[str] = "System",
        department: Optional[str] = "General",
        tags: Optional[List[str]] = None,
        language: str = "en",
    ):
        """Upsert document vector chunks into Qdrant store with circuit breaker."""
        if not QdrantConnection.is_available():
            logger.debug("Qdrant circuit breaker OPEN — skipping upsert (0ms)")
            return

        points = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for idx, chunk in enumerate(document.chunks):
            chunk_uuid = str(uuid.uuid4())
            payload = {
                "chunk_id": getattr(chunk, "chunk_id", chunk_uuid),
                "document_id": str(document_id),
                "organization_id": str(organization_id),
                "page_number": getattr(chunk, "page", page_number),
                "chunk_index": idx,
                "text": chunk.text,
                "author": author or "System",
                "department": department or "General",
                "tags": tags or [],
                "language": language,
                "created_at": now_iso,
                "metadata": getattr(chunk, "metadata", {}),
            }

            points.append(
                PointStruct(
                    id=chunk_uuid,
                    vector=chunk.embedding if chunk.embedding is not None else [],
                    payload=payload,
                )
            )

        try:
            client = self.client
            if client is None:
                logger.debug("Qdrant client unavailable — skipping upsert")
                return
            client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            logger.info(f"Upserted {len(points)} vector chunks to Qdrant collection '{self.collection_name}'")
        except Exception as e:
            QdrantConnection.mark_offline()
            raise

    def index(self, document: ChunkedDocument):
        """Standard interface implementation for indexing."""
        dummy_org = uuid.UUID("00000000-0000-0000-0000-000000000001")
        dummy_doc = uuid.uuid4()
        import asyncio
        asyncio.run(self.upsert_document_chunks(document, dummy_doc, dummy_org))

    def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        organization_id: Optional[uuid.UUID] = None,
        department: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Perform dense vector search with circuit breaker."""
        if not QdrantConnection.is_available():
            logger.debug("Qdrant circuit breaker OPEN — skipping search (0ms)")
            return []

        must_conditions = []

        if organization_id:
            must_conditions.append(
                FieldCondition(
                    key="organization_id",
                    match=MatchValue(value=str(organization_id)),
                )
            )

        if department:
            must_conditions.append(
                FieldCondition(
                    key="department",
                    match=MatchValue(value=department),
                )
            )

        query_filter = Filter(must=must_conditions) if must_conditions else None

        try:
            client = self.client
            if client is None:
                logger.debug("Qdrant client unavailable — skipping search")
                return []
            results = client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                query_filter=query_filter,
                limit=limit,
            )

            formatted_results = []
            for pt in results.points:
                payload = pt.payload or {}
                formatted_results.append({
                    "chunk_id": payload.get("chunk_id"),
                    "document_id": payload.get("document_id"),
                    "organization_id": payload.get("organization_id"),
                    "page_number": payload.get("page_number"),
                    "chunk_index": payload.get("chunk_index"),
                    "text": payload.get("text"),
                    "score": getattr(pt, "score", 0.0),
                    "author": payload.get("author"),
                    "department": payload.get("department"),
                    "tags": payload.get("tags"),
                    "language": payload.get("language"),
                    "created_at": payload.get("created_at"),
                    "metadata": payload.get("metadata"),
                })
            return formatted_results
        except Exception as e:
            logger.warning(f"Qdrant vector store offline or search warning: {e}")
            QdrantConnection.mark_offline()
            return []
