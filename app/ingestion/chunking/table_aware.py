"""
PHASE 8: Table-Aware Chunking for CSV/XLSX

Groups rows logically instead of character-count splitting.
Preserves header context in each chunk.
Used for semantic search on tabular data ("what trends in this data?").

Strategy:
- For CSV/XLSX: Group by N rows, keep header
- For PDF/DOCX: Use existing recursive chunking (no change)
"""

from typing import List, Optional
import pandas as pd
from app.ingestion.chunking.base import BaseChunker
from app.ingestion.schemas import ChunkedDocument, Chunk, ParsedDocument, ParsedPage
from app.utils.logger import logger


class TableAwareChunker(BaseChunker):
    """
    Table-aware chunking for CSV/XLSX.
    
    Groups rows logically (by N rows or natural key) so:
    1. Rows are never split mid-record
    2. Each chunk retains header context
    3. Embeddings preserve column meaning
    """
    
    def __init__(self, rows_per_chunk: int = 10):
        """
        Initialize table-aware chunker.
        
        Args:
            rows_per_chunk: Number of data rows per chunk (excluding header)
        """
        super().__init__()
        self.rows_per_chunk = rows_per_chunk
    
    def chunk(self, document: ParsedDocument) -> ChunkedDocument:
        """
        Chunk a document intelligently.
        
        For CSV/XLSX: Group rows, preserve header
        For other types: Fall back to recursive chunking
        """
        # Check document type
        if document.file_type in ("csv", "xlsx", "xls"):
            return self._chunk_table(document)
        else:
            # Fall back to recursive chunking for PDF/DOCX/etc
            from app.ingestion.chunking.recursive import RecursiveChunker
            recursive = RecursiveChunker()
            return recursive.chunk(document)
    
    def _chunk_table(self, document: ParsedDocument) -> ChunkedDocument:
        """Chunk a table document (CSV/XLSX)."""
        chunks: List[Chunk] = []
        
        for page in document.pages:
            # For each sheet/page, parse as table
            try:
                page_chunks = self._chunk_page_as_table(page)
                chunks.extend(page_chunks)
            except Exception as e:
                logger.warning(f"Failed to chunk page {page.page} as table: {e}")
                # Fallback: treat as text
                page_chunks = self._chunk_page_as_text(page)
                chunks.extend(page_chunks)
        
        logger.success(f"Chunked table: {len(chunks)} chunks")
        
        return ChunkedDocument(
            document=document.document,
            file_type=document.file_type,
            page_count=document.page_count,
            chunks=chunks,
        )
    
    def _chunk_page_as_table(self, page: ParsedPage) -> List[Chunk]:
        """
        Parse page as table and chunk by rows.
        
        Assumes first row is header, subsequent rows are data.
        """
        chunks = []
        text = page.text
        
        if not text or not text.strip():
            return chunks
        
        lines = text.strip().split('\n')
        if len(lines) < 2:
            # Only header, no data
            return chunks
        
        # First line is header
        header = lines[0]
        data_lines = lines[1:]
        
        # Group data rows
        for chunk_idx in range(0, len(data_lines), self.rows_per_chunk):
            chunk_rows = data_lines[chunk_idx:chunk_idx + self.rows_per_chunk]
            
            # Include header + rows in each chunk
            chunk_text = header + '\n' + '\n'.join(chunk_rows)
            
            chunk = Chunk(
                text=chunk_text,
                page=page.page,
                chunk_id=f"{page.page}_{chunk_idx}",
                metadata={
                    "rows_in_chunk": len(chunk_rows),
                    "is_table": True,
                    "header_included": True,
                },
            )
            chunks.append(chunk)
        
        logger.debug(
            f"Chunked page {page.page}: {len(chunks)} chunks "
            f"({len(data_lines)} data rows total)"
        )
        
        return chunks
    
    def _chunk_page_as_text(self, page: ParsedPage) -> List[Chunk]:
        """Fallback: chunk as text if table parsing fails."""
        chunks = []
        text = page.text
        
        if not text:
            return chunks
        
        # Simple character-based chunking
        chunk_size = 1000
        overlap = 200
        
        for idx in range(0, len(text), chunk_size - overlap):
            chunk_text = text[idx:idx + chunk_size]
            if len(chunk_text.strip()) < 10:
                continue
            
            chunk = Chunk(
                text=chunk_text,
                page=page.page,
                chunk_id=f"{page.page}_{idx}",
                metadata={"is_table": False},
            )
            chunks.append(chunk)
        
        return chunks