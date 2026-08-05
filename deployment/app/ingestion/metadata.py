from datetime import UTC, datetime
from pathlib import Path

from loguru import logger

from app.ingestion.schemas import (
    DocumentMetadata,
    ParsedDocument,
)


class MetadataExtractor:
    """
    Extracts filesystem metadata and attaches it to a ParsedDocument.
    """

    def process(
        self,
        document: ParsedDocument,
        file_path: str | Path,
    ) -> ParsedDocument:

        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(
                f"File does not exist: {file_path}"
            )

        logger.info(
            f"Extracting metadata from '{file_path.name}'"
        )

        stat = file_path.stat()

        metadata = DocumentMetadata(
            filename=file_path.name,
            extension=file_path.suffix.lower(),
            size_bytes=stat.st_size,
            page_count=document.page_count,
            total_characters=document.total_characters,
            created_at=datetime.fromtimestamp(
                stat.st_ctime,
                tz=UTC,
            ),
            modified_at=datetime.fromtimestamp(
                stat.st_mtime,
                tz=UTC,
            ),
        )

        document.metadata = metadata

        logger.success(
            f"Metadata extracted successfully "
            f"(pages={metadata.page_count}, "
            f"size={metadata.size_bytes} bytes)"
        )

        return document