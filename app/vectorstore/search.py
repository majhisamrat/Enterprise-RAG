import uuid
from typing import Any, Dict, List, Optional
from app.embeddings.embedder import Embedder
from app.vectorstore.qdrant_store import QdrantVectorStore


class VectorSearchEngine:
    """High-level query interface for dense vector search."""

    def __init__(self):
        self.store = QdrantVectorStore()
        self.embedder = Embedder()

    def search(
        self,
        query: str,
        limit: int = 10,
        organization_id: Optional[uuid.UUID] = None,
        department: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Embed query and search Qdrant dense vector store."""
        query_vector = self.embedder.embed_query(query)
        return self.store.search(
            query_embedding=query_vector,
            limit=limit,
            organization_id=organization_id,
            department=department,
        )