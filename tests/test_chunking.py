import pytest
from app.ingestion.chunking.recursive import RecursiveChunker
from app.ingestion.schemas import ParsedDocument, ParsedPage


def test_recursive_chunker():
    chunker = RecursiveChunker(chunk_size=100, chunk_overlap=20)
    sample_text = "Enterprise RAG platforms require high performance chunking and vector storage. " * 5
    page = ParsedPage(
        document="test_doc.pdf",
        page=1,
        text=sample_text,
    )
    doc = ParsedDocument(
        document="test_doc.pdf",
        file_type=".pdf",
        page_count=1,
        total_characters=len(sample_text),
        needs_ocr=False,
        ocr_used=False,
        pages=[page],
    )

    chunked = chunker.chunk(doc)
    assert len(chunked.chunks) > 0
    assert all(len(c.text) <= 150 for c in chunked.chunks)
