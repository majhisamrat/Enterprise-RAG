import uuid
from typing import Any, Dict, List, Optional
from app.utils.logger import logger
from app.config import settings
from app.keyword_search.elastic_client import ElasticConnection


class KeywordSearchEngine:
    """Production-grade Elasticsearch BM25 Keyword Search Engine with filters."""

    def __init__(self, index_name: str = settings.ELASTIC_INDEX):
        self.index_name = index_name
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = ElasticConnection.get_client()
        return self._client

    def search(
        self,
        query: str,
        limit: int = 10,
        organization_id: Optional[uuid.UUID] = None,
        knowledge_base_id: Optional[uuid.UUID] = None,
        upload_id: Optional[uuid.UUID] = None,
        department: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Perform BM25 keyword search with organization, KB, upload, and department filters."""
        if not ElasticConnection.is_available():
            logger.debug("Elasticsearch circuit breaker OPEN — skipping search (0ms)")
            return []

        must_clauses = [
            {"match": {"text": query}}
        ]
        filter_clauses = []

        if organization_id:
            filter_clauses.append({"term": {"organization_id": str(organization_id)}})

        if knowledge_base_id:
            filter_clauses.append({"term": {"knowledge_base_id": str(knowledge_base_id)}})

        if upload_id:
            filter_clauses.append({"term": {"upload_id": str(upload_id)}})

        if department:
            filter_clauses.append({"term": {"department": department}})

        bool_query = {
            "must": must_clauses,
        }
        if filter_clauses:
            bool_query["filter"] = filter_clauses

        try:
            response = self.client.search(
                index=self.index_name,
                query={"bool": bool_query},
                size=limit,
            )

            hits = response["hits"]["hits"]
            results = []
            for hit in hits:
                src = hit["_source"]
                results.append({
                    "chunk_id": src.get("chunk_id"),
                    "document_id": src.get("document_id"),
                    "organization_id": src.get("organization_id"),
                    "title": src.get("title"),
                    "text": src.get("text"),
                    "score": hit["_score"],
                    "author": src.get("author"),
                    "department": src.get("department"),
                    "tags": src.get("tags"),
                    "language": src.get("language"),
                    "created_at": src.get("created_at"),
                })
            return results
        except Exception as e:
            logger.warning(f"Elasticsearch BM25 search offline or search warning: {e}")
            ElasticConnection.mark_offline()
            return []


# Backward compatibility alias
KeywordSearch = KeywordSearchEngine