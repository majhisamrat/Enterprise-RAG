import uuid
from typing import Any, Dict, List, Optional
from loguru import logger

from app.embeddings.embedder import Embedder
from app.retrieval.base import BaseRetriever
from app.vectorstore.chroma_store import ChromaVectorStore


class DenseRetriever(BaseRetriever):
    """Dense vector retrieval using Chroma with tenant and department filtering."""

    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = ChromaVectorStore()

    def retrieve(
        self,
        query: str,
        limit: int = 10,
        organization_id: Optional[uuid.UUID] = None,
        knowledge_base_id: Optional[uuid.UUID] = None,
        upload_id: Optional[uuid.UUID] = None,
        department: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        logger.info(f"Running dense vector retrieval with KB filtering (KB: {knowledge_base_id})")
        query_vector = self.embedder.embed_query(query)
        return self.vector_store.search(
            query_embedding=query_vector,
            limit=limit,
            organization_id=organization_id,
            knowledge_base_id=knowledge_base_id,
            upload_id=upload_id,
            department=department,
        )