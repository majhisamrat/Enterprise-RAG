from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class ParsedPage(BaseModel):
    document: str

    page: int | str

    text: str = ""

    needs_ocr: bool = False
    

    image_path: Optional[str] = None


class DocumentMetadata(BaseModel):
    filename: str

    extension: str

    size_bytes: int

    page_count: int

    total_characters: int

    created_at: Optional[datetime] = None

    modified_at: Optional[datetime] = None


class ParsedDocument(BaseModel):
    document: str

    file_type: str

    page_count: int

    total_characters: int

    needs_ocr: bool
    ocr_used: bool = False

    pages: list[ParsedPage]

    metadata: Optional[DocumentMetadata] = None


class Chunk(BaseModel):

    chunk_id: str

    document: str

    page: int | str

    text: str

    start_char: int

    end_char: int

    embedding: list[float] | None = None

    metadata: dict[str, Any] = {}


class ChunkedDocument(BaseModel):

    document: str

    chunks: list[Chunk]

    metadata: Optional[DocumentMetadata] = None