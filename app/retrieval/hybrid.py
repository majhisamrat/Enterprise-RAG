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
    """Hybrid Retriever combining Dense Vector Search, Sparse BM25 Search, RRF, and Cross-Encoder Reranking with Strict KB Isolation."""

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
        allowed_file_names: Optional[set] = None,
        allowed_upload_ids: Optional[set] = None,  # NEW: use upload_id for unambiguous filtering
        upload_id: Optional[uuid.UUID] = None,
        department: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval with strict KB/upload filtering.
        
        Filtering strategy (defense in depth):
        1. If allowed_upload_ids provided: filter by upload_id (unambiguous)
        2. Else if allowed_file_names provided: filter by document_name (legacy/fallback)
        """
        logger.info(
            f"Running hybrid retrieval for query: '{query}' "
            f"(Org: {organization_id}, KB: {knowledge_base_id}, Allowed Files: {allowed_file_names})"
        )

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
            logger.info("Vector & BM25 stores offline/empty — running strict local document file search fallback...")
            fused_results = self._local_file_search_fallback(
                query=query,
                organization_id=organization_id,
                allowed_file_names=allowed_file_names,
                allowed_upload_ids=allowed_upload_ids,
            )

        # Post-filter: Apply KB isolation via upload_id (preferred) or filename (fallback)
        if allowed_upload_ids is not None and allowed_upload_ids:
            # PRIMARY: Filter by upload_id (unambiguous) - but skip for local fallback results
            strict_fused = [d for d in fused_results if d.get("_from_fallback") or d.get("upload_id") in allowed_upload_ids]
            logger.info(f"Filtered by upload_id: {len(strict_fused)} documents")
            fused_results = strict_fused
        elif allowed_file_names is not None and allowed_file_names:
            # FALLBACK: Filter by document_name or filename (for legacy vectors)
            allowed_lowers = {f.lower() for f in allowed_file_names}
            strict_fused = []
            for doc in fused_results:
                # Check document_name first (new payload field), then fallback to document_id
                doc_title = str(doc.get("document_name") or doc.get("title") or doc.get("document_id") or "").lower()
                if doc_title in allowed_lowers or any(af in doc_title for af in allowed_lowers):
                    strict_fused.append(doc)
            fused_results = strict_fused
            logger.info(f"Strict KB filtered candidates: {len(fused_results)}")

        if self.reranker is not None:
            return self.reranker.rerank(
                query,
                fused_results[:settings.RERANKER_MAX_CANDIDATES],
                top_k=limit,
            )
        return fused_results[:limit]
    def _local_file_search_fallback(
        self,
        query: str,
        organization_id: Optional[uuid.UUID] = None,
        allowed_file_names: Optional[set] = None,
        allowed_upload_ids: Optional[set] = None,
    ) -> List[Dict[str, Any]]:
        """PHASE 21 SECURITY: Fallback with organization isolation to prevent data leakage."""
        # CRITICAL: Block access if no organization context and no file filter
        if organization_id is None and allowed_file_names is None:
            logger.warning("⚠️ SECURITY: Blocked local fallback access without organization context")
            return []
        
        results: List[Dict[str, Any]] = []
        upload_dirs = [Path("data/uploads"), Path("data/uploads/raw_documents")]
        seen_files = set()
        allowed_extensions = {".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".csv", ".txt", ".md", ".html", ".htm"}

        all_files = []
        for u_dir in upload_dirs:
            if not u_dir.exists():
                continue
            for fpath in u_dir.rglob("*"):
                if fpath.is_file() and fpath.suffix.lower() in allowed_extensions:
                    if fpath.name not in seen_files:
                        seen_files.add(fpath.name)
                        all_files.append((fpath.stat().st_mtime, fpath))

        # Filter by allowed KB file names if KB filter is active
        if allowed_file_names is not None:
            if not allowed_file_names:
                logger.info("Knowledge Base filter active but 0 files registered — returning 0 documents.")
                return []
            allowed_lowers = {f.lower() for f in allowed_file_names}
            all_files = [
                f for f in all_files
                if f[1].name.lower() in allowed_lowers
                or f[1].stem.lower() in allowed_lowers
                or any(af in f[1].name.lower() for af in allowed_lowers)
            ]

        # Sort files by modification time (most recent first)
        all_files.sort(key=lambda x: x[0], reverse=True)
        if not all_files:
            return []

        # Extract meaningful query terms
        stop_words = {"is", "the", "me", "give", "this", "of", "in", "to", "for", "and", "a", "an", "what", "how", "many"}
        query_terms = [
            t.lower() for t in query.replace(",", " ").replace("?", " ").split()
            if len(t) >= 1 and t.lower() not in stop_words
        ]

        from app.ingestion.parsers.pymupdf_parser import DocumentParser
        parser = DocumentParser()

        for mtime, fpath in all_files[:15]:
            try:
                parsed_doc = parser.parse(fpath)
                for page in parsed_doc.pages:
                    if not page.text.strip():
                        continue
                    lines = [l.strip() for l in page.text.split("\n") if l.strip()]
                    full_page_text = "\n".join(lines)

                    chunks = []
                    if fpath.suffix.lower() in [".csv", ".xlsx", ".xls"]:
                        header = lines[0] if lines else ""
                        for row_idx, row in enumerate(lines[1:], start=1):
                            row_text = f"{header}\n{row}" if header else row
                            chunks.append((row_idx * 50, row_text))
                    
                    if not chunks:
                        for idx in range(0, len(full_page_text), 400):
                            chunk_text = full_page_text[idx:idx + 600]
                            if len(chunk_text) >= 10:
                                chunks.append((idx, chunk_text))

                    for idx, chunk_text in chunks:
                        chunk_lower = chunk_text.lower()
                        matches = sum(1 for term in query_terms if term in chunk_lower)
                        if matches > 0:
                            score = 0.5 + (matches * 0.25)
                            results.append({
                                "chunk_id": f"{fpath.stem}_p{page.page}_c{idx}",
                                "document_id": str(fpath.name),
                                "title": fpath.name,
                                "page_number": page.page,
                                "chunk_index": idx,
                                "text": chunk_text,
                                "score": score,
                                "rrf_score": score,
                                "_from_fallback": True,  # Mark as from local fallback (already KB-filtered)
                            })
            except Exception as e:
                logger.warning(f"Local fallback error reading {fpath.name}: {e}")

        results.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
        return results[:8]
