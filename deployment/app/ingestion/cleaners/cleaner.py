from loguru import logger

from app.ingestion.cleaners.encoding import fix_encoding
from app.ingestion.cleaners.header_footer import (
    remove_headers,
    remove_footers,
)
from app.ingestion.cleaners.normalize import normalize_text
from app.ingestion.schemas import ParsedDocument, ParsedPage


class TextCleaner:
    """
    Cleans extracted document text.

    Responsibilities:
    - Fix encoding
    - Remove headers
    - Remove footers
    - Normalize whitespace
    """

    def clean(self, document: ParsedDocument) -> ParsedDocument:

        logger.info(f"Cleaning document: {document.document}")

        cleaned_pages: list[ParsedPage] = []

        total_characters = 0

        for page in document.pages:

            text = page.text

            text = fix_encoding(text)
            text = remove_headers(text)
            text = remove_footers(text)
            text = normalize_text(text)

            total_characters += len(text)

            cleaned_pages.append(
                ParsedPage(
                    document=page.document,
                    page=page.page,
                    text=text,
                    needs_ocr=page.needs_ocr,
                    image_path=page.image_path,
                )
            )

        document.pages = cleaned_pages
        document.total_characters = total_characters

        logger.success(
            f"Cleaning completed: {document.document}"
        )

        return document