import uuid
from typing import Any, Dict, List, Optional
from loguru import logger

from app.keyword_search.search import KeywordSearchEngine
from app.retrieval.base import BaseRetriever


class SparseRetriever(BaseRetriever):
    """Sparse retrieval using Elasticsearch BM25 search engine."""

    def __init__(self):
        self.engine = KeywordSearchEngine()

    def retrieve(
        self,
        query: str,
        limit: int = 10,
        organization_id: Optional[uuid.UUID] = None,
        department: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        logger.info("Running sparse BM25 retrieval.")
        return self.engine.search(
            query=query,
            limit=limit,
            organization_id=organization_id,
            department=department,
        )