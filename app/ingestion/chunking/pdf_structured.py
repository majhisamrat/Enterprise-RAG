"""
PDF-Aware Chunking for Structured Data (Employee Records, etc.)

Detects structured records by pattern (e.g., EMP-0001, EMP-0002, etc.)
and chunks one record per chunk to preserve granularity for semantic search.

Why this matters:
- Raw recursive chunking creates 9 chunks for 100 employees (11 records per chunk)
- Semantic search on "details of EMP-0099" fails because EMP-0099 might be 
  grouped with other employees in the same chunk, diluting its relevance
- Pattern-based chunking creates 100+ chunks (1 record per chunk)
- Each employee ID is its own retrievable unit
"""

import re
from typing import List, Optional
from app.ingestion.chunking.base import BaseChunker
from app.ingestion.chunking.recursive import RecursiveChunker
from app.ingestion.schemas import ChunkedDocument, Chunk, ParsedDocument, ParsedPage
from app.utils.logger import logger


class PDFStructuredChunker(BaseChunker):
    """
    Intelligent chunker for PDFs with structured records.
    
    Detects:
    - Employee records (EMP-0001, EMP-0002, ...)
    - Invoice records (INV-0001, ...)
    - Any pattern with ID and structured fields
    
    Chunks one record per chunk to maximize retrieval precision.
    """
    
    # Common record ID patterns
    RECORD_PATTERNS = {
        "employee": r"EMP-\d{4,5}",  # EMP-0001, EMP-00100
        "invoice": r"INV-\d{4,5}",
        "customer": r"CUST-\d{4,5}",
        "product": r"PROD-\d{4,5}",
        "order": r"ORD-\d{4,5}",
        "transaction": r"TXN-\d{4,5}",
    }
    
    def __init__(self, fallback_chunk_size: int = 800):
        """
        Initialize PDF structured chunker.
        
        Args:
            fallback_chunk_size: Chunk size for unstructured fallback
        """
        super().__init__()
        self.fallback_chunk_size = fallback_chunk_size
        self.recursive_chunker = RecursiveChunker(chunk_size=fallback_chunk_size)
    
    def chunk(self, document: ParsedDocument) -> ChunkedDocument:
        """
        Chunk a document intelligently.
        
        For PDFs with structured records: Chunk by record ID
        For other types: Fall back to recursive chunking
        """
        # Only apply pattern-based chunking to PDFs
        if document.file_type != "pdf":
            return self.recursive_chunker.chunk(document)
        
        logger.info(f"Attempting pattern-based chunking for PDF: {document.document}")
        
        chunks: List[Chunk] = []
        
        for page in document.pages:
            # Try to detect and chunk by pattern
            page_chunks = self._chunk_by_pattern(page, document)
            
            if page_chunks:
                chunks.extend(page_chunks)
                logger.debug(
                    f"Page {page.page}: Detected structured records "
                    f"({len(page_chunks)} chunks)"
                )
            else:
                # Fallback to recursive chunking if no patterns found
                logger.debug(f"Page {page.page}: No patterns detected, using recursive chunking")
                chunks.extend(self._chunk_page_recursive(page, document))
        
        if not chunks:
            logger.warning(f"No chunks generated, using recursive chunking")
            chunks = self.recursive_chunker.chunk(document).chunks
        
        logger.success(f"Chunked PDF: {len(chunks)} chunks")
        
        return ChunkedDocument(
            document=document.document,
            file_type=document.file_type,
            page_count=document.page_count,
            chunks=chunks,
        )
    
    def _chunk_by_pattern(self, page: ParsedPage, document: ParsedDocument) -> List[Chunk]:
        """
        Detect and chunk by record patterns (EMP-0001, etc.).
        """
        text = page.text
        if not text or not text.strip():
            return []
        
        chunks = []
        
        # Try each pattern
        for pattern_name, pattern in self.RECORD_PATTERNS.items():
            # Find all record IDs in the text
            matches = list(re.finditer(pattern, text))
            
            if not matches:
                continue
            
            logger.debug(
                f"Found {len(matches)} {pattern_name} records on page {page.page}"
            )
            
            # Split text by record boundaries
            for idx, match in enumerate(matches):
                record_id = match.group()
                start_pos = match.start()
                
                # Next record starts at the next match, or end of text
                if idx + 1 < len(matches):
                    end_pos = matches[idx + 1].start()
                else:
                    end_pos = len(text)
                
                # Extract the record text
                record_text = text[start_pos:end_pos].strip()
                
                if len(record_text) < 10:  # Skip tiny chunks
                    continue
                
                chunk = Chunk(
                    text=record_text,
                    page=page.page,
                    document=document.document,
                    chunk_id=f"{page.page}_{pattern_name}_{record_id}",
                    start_char=start_pos,
                    end_char=end_pos,
                    metadata={
                        "record_type": pattern_name,
                        "record_id": record_id,
                        "is_structured": True,
                        "file_type": document.file_type,
                    },
                )
                chunks.append(chunk)
            
            # If we found patterns, return these chunks
            if chunks:
                return chunks
        
        # No patterns found
        return []
    
    def _chunk_page_recursive(self, page: ParsedPage, document: ParsedDocument) -> List[Chunk]:
        """
        Fallback: Use recursive chunking for a single page.
        """
        # Create a temporary ParsedDocument with just this page
        temp_doc = ParsedDocument(
            document=document.document,
            file_type=document.file_type,
            pages=[page],
            page_count=1,
            metadata=document.metadata,
        )
        
        chunked = self.recursive_chunker.chunk(temp_doc)
        return chunked.chunks
