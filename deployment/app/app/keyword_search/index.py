import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.utils.logger import logger
from elasticsearch.helpers import bulk

from app.config import settings
from app.ingestion.schemas import ChunkedDocument
from app.keyword_search.elastic_client import ElasticConnection


class ElasticsearchIndexer:
    """Production-grade Elasticsearch BM25 Indexer with circuit breaker."""

    def __init__(self, index_name: str = settings.ELASTIC_INDEX):
        self.index_name = index_name
        self._client = None

    @property
    def client(self):
        if self._client is None:
            if not ElasticConnection.is_available():
                return None
            self._client = ElasticConnection.get_client()
            self._ensure_index()
            # Avoid a second failed request after _ensure_index has marked the
            # service offline.
            if not ElasticConnection.is_available():
                self._client = None
                return None
        return self._client

    def _ensure_index(self):
        """Create Elasticsearch index with BM25 mappings if it doesn't exist."""
        if self._client is None:
            return
        client = self._client
        try:
            if not client.indices.exists(index=self.index_name):
                logger.info(f"Creating Elasticsearch index '{self.index_name}' with BM25 mapping...")
                mapping = {
                    "mappings": {
                        "properties": {
                            "document_id": {"type": "keyword"},
                            "chunk_id": {"type": "keyword"},
                            "organization_id": {"type": "keyword"},
                            "title": {"type": "text", "analyzer": "standard"},
                            "text": {"type": "text", "analyzer": "standard"},
                            "author": {"type": "keyword"},
                            "department": {"type": "keyword"},
                            "tags": {"type": "keyword"},
                            "language": {"type": "keyword"},
                            "created_at": {"type": "date"},
                            "updated_at": {"type": "date"},
                        }
                    }
                }
                client.indices.create(index=self.index_name, body=mapping)
        except Exception as e:
            logger.warning(f"Elasticsearch index check/creation warning (server offline?): {e}")
            ElasticConnection.mark_offline()

    async def index_document_chunks(
        self,
        document: ChunkedDocument,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
        title: str = "",
        author: Optional[str] = "System",
        department: Optional[str] = "General",
        tags: Optional[List[str]] = None,
        language: str = "en",
        upload_id: Optional[uuid.UUID] = None,  # NEW
        knowledge_base_id: Optional[uuid.UUID] = None,  # NEW
    ):
        """Bulk index document chunks with circuit breaker and KB metadata."""
        if not ElasticConnection.is_available():
            logger.debug("Elasticsearch circuit breaker OPEN — skipping indexing (0ms)")
            return 0

        actions = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for idx, chunk in enumerate(document.chunks):
            chunk_uuid = getattr(chunk, "chunk_id", str(uuid.uuid4()))
            doc = {
                "_index": self.index_name,
                "_id": chunk_uuid,
                "_source": {
                    "document_id": str(document_id),
                    "chunk_id": chunk_uuid,
                    "organization_id": str(organization_id),
                    # KB metadata (NEW)
                    "upload_id": str(upload_id) if upload_id else str(document_id),
                    "knowledge_base_id": str(knowledge_base_id) if knowledge_base_id else None,
                    "page_number": getattr(chunk, "page", 1),
                    "chunk_index": idx,
                    "title": title or "Untitled Document",
                    "text": chunk.text,
                    "author": author or "System",
                    "department": department or "General",
                    "tags": tags or [],
                    "language": language,
                    "created_at": now_iso,
                    "updated_at": now_iso,
                },
            }
            actions.append(doc)

        try:
            client = self.client
            if client is None:
                logger.debug("Elasticsearch client unavailable — skipping indexing")
                return 0
            success, _ = bulk(client, actions)
            logger.info(f"Bulk indexed {success} document chunks in Elasticsearch index '{self.index_name}'")
            return success
        except Exception as e:
            ElasticConnection.mark_offline()
            raise

    async def delete_documents_by_upload(self, upload_id: uuid.UUID) -> int:
        """
        Delete all documents for a specific upload from Elasticsearch.
        
        Used during per-KB reindexing to remove old documents before re-indexing.
        """
        if not ElasticConnection.is_available():
            logger.debug("Elasticsearch circuit breaker OPEN — skipping delete (0ms)")
            return 0

        try:
            client = self.client
            if client is None:
                logger.debug("Elasticsearch client unavailable — skipping delete")
                return 0

            # Delete all documents with matching upload_id
            result = client.delete_by_query(
                index=self.index_name,
                body={
                    "query": {
                        "term": {
                            "upload_id": str(upload_id)
                        }
                    }
                }
            )

            deleted_count = result.get("deleted", 0)
            logger.info(f"Deleted {deleted_count} documents for upload {upload_id} from Elasticsearch")
            return deleted_count

        except Exception as e:
            logger.warning(f"Error deleting documents for upload {upload_id}: {e}")
            ElasticConnection.mark_offline()
            return 0


# Backward compatibility alias
ElasticIndexManager = ElasticsearchIndexer
