from loguru import logger
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.ingestion.chunking.base import BaseChunker
from app.ingestion.chunking.utils import generate_chunk_id
from app.ingestion.schemas import (
    Chunk,
    ChunkedDocument,
    ParsedDocument,
)


class RecursiveChunker(BaseChunker):

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

    def chunk(
        self,
        document: ParsedDocument,
    ) -> ChunkedDocument:

        logger.info(
            f"Chunking document: {document.document}"
        )

        chunks: list[Chunk] = []

        for page in document.pages:

            splits = self.splitter.split_text(page.text)

            cursor = 0

            for text in splits:

                start = page.text.find(text, cursor)

                if start == -1:
                    start = cursor

                end = start + len(text)

                cursor = end

                chunks.append(
                    Chunk(
                        chunk_id=generate_chunk_id(
                            document=document.document,
                            page=page.page,
                            text=text,
                        ),
                        document=document.document,
                        page=page.page,
                        text=text,
                        start_char=start,
                        end_char=end,
                        metadata={
                            "file_type": document.file_type,
                            "page": page.page,
                            "needs_ocr": page.needs_ocr,
                        },
                    )
                )
        logger.success(
            f"Generated {len(chunks)} chunks."
        )

        return ChunkedDocument(
            document=document.document,
            chunks=chunks,
            metadata=document.metadata,
        )