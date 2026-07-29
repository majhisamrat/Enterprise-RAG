import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.utils.logger import logger

from app.reranker.reranker import BGEReranker
from app.retrieval.dense import DenseRetriever
from app.retrieval.fusion import ReciprocalRankFusion
from app.retrieval.sparse import SparseRetriever
from app.config import settings


class HybridRetriever:
    """Hybrid Retriever combining Dense Vector Search, Sparse BM25 Search, RRF, and Cross-Encoder Reranking with Fast Single-Document Fallback."""

    def __init__(self) -> None:
        self.dense = DenseRetriever()
        self.sparse = SparseRetriever()
        self.fusion = ReciprocalRankFusion(k=60)
        self.reranker = BGEReranker() if settings.ENABLE_RERANKER else None

    def retrieve(
        self,
        query: str,
        limit: int = 10,
        organization_id: Optional[uuid.UUID] = None,
        knowledge_base_id: Optional[uuid.UUID] = None,
        upload_id: Optional[uuid.UUID] = None,
        department: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval with optional KB/upload filtering.
        
        - **knowledge_base_id**: Filter to single KB only (optional)
        - **upload_id**: Filter to single upload only (optional)
        """
        logger.info(
            f"Running hybrid retrieval for query: '{query}' "
            f"(Org: {organization_id}, KB: {knowledge_base_id}, Upload: {upload_id})"
        )

        # Keep the candidate set bounded.  Cross-encoder inference on CPU grows
        # linearly with this number and was the dominant source of query latency.
        limit = min(limit, settings.MAX_RETRIEVAL_RESULTS)
        candidate_limit = min(max(limit * 2, limit), settings.RERANKER_MAX_CANDIDATES)

        # Run dense and sparse retrieval concurrently with KB filtering
        with ThreadPoolExecutor(max_workers=2) as executor:
            dense_future = executor.submit(
                self.dense.retrieve,
                query,
                candidate_limit,
                organization_id,
                knowledge_base_id,
                upload_id,
                department,
            )
            sparse_future = executor.submit(
                self.sparse.retrieve,
                query,
                candidate_limit,
                organization_id,
                knowledge_base_id,
                upload_id,
                department,
            )

            dense_results = dense_future.result()
            sparse_results = sparse_future.result()

        logger.info(f"Dense Results: {len(dense_results)} | Sparse Results: {len(sparse_results)}")

        # Perform Reciprocal Rank Fusion
        fused_results = self.fusion.fuse(dense_results, sparse_results)
        logger.info(f"Fused candidate documents: {len(fused_results)}")

        # Local file search fallback if Qdrant / ES vector stores return 0 candidates
        if not fused_results:
            logger.info("Vector & BM25 stores offline/empty — running local document file search fallback...")
            fused_results = self._local_file_search_fallback(query)

        # RRF is already a strong ranker.  The heavyweight cross-encoder is
        # optional for deployments with sufficient CPU/GPU capacity.
        if self.reranker is not None:
            return self.reranker.rerank(
                query,
                fused_results[:settings.RERANKER_MAX_CANDIDATES],
                top_k=limit,
            )
        return fused_results[:limit]

    def _local_file_search_fallback(self, query: str) -> List[Dict[str, Any]]:
        """Fallback to parse ONLY the most recently uploaded PDF document when vector DB is offline."""
        results: List[Dict[str, Any]] = []
        upload_dirs = [Path("data/uploads"), Path("data/uploads/raw_documents")]
        seen_files = set()

        all_files = []
        for u_dir in upload_dirs:
            if not u_dir.exists():
                continue
            for fpath in u_dir.rglob("*"):
                if fpath.is_file() and fpath.suffix.lower() in [".pdf", ".docx", ".txt", ".md"]:
                    if fpath.name not in seen_files:
                        seen_files.add(fpath.name)
                        all_files.append((fpath.stat().st_mtime, fpath))

        # Sort files by creation/modification time so ONLY the latest uploaded file is parsed
        all_files.sort(key=lambda x: x[0], reverse=True)
        if not all_files:
            return []

        query_terms = [t.lower() for t in query.split() if len(t) > 2]

        from app.ingestion.parsers.pymupdf_parser import DocumentParser
        parser = DocumentParser()

        # Parse ONLY the single latest uploaded document for sub-second performance
        for mtime, fpath in all_files[:1]:
            try:
                parsed_doc = parser.parse(fpath)
                for page in parsed_doc.pages:
                    if not page.text.strip():
                        continue
                    lines = [l.strip() for l in page.text.split("\n") if l.strip()]
                    full_page_text = "\n".join(lines)

                    for idx in range(0, len(full_page_text), 400):
                        chunk_text = full_page_text[idx:idx + 600]
                        if len(chunk_text) < 20:
                            continue

                        matches = sum(1 for term in query_terms if term in chunk_text.lower())
                        score = 0.5 + (matches * 0.2)

                        results.append({
                            "chunk_id": f"{fpath.stem}_p{page.page}_c{idx}",
                            "document_id": str(fpath.name),
                            "title": fpath.name,
                            "page_number": page.page,
                            "chunk_index": idx,
                            "text": chunk_text,
                            "score": score,
                            "rrf_score": score,
                        })
            except Exception as e:
                logger.warning(f"Local fallback error reading {fpath.name}: {e}")

        results.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
        # Limit to top 5 chunks max so CPU CrossEncoder reranking finishes in < 1.5 seconds
        return results[:5]
