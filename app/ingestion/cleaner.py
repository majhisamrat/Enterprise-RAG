import re

from loguru import logger

from app.ingestion.schemas import ParsedDocument, ParsedPage


class Cleaner:
    """
    Cleans extracted document text.

    Responsibilities:
    - Remove excessive whitespace
    - Normalize line breaks
    - Remove repeated blank lines
    - Remove non-printable characters
    - Trim leading/trailing spaces
    """

    def process(self, document: ParsedDocument) -> ParsedDocument:

        logger.info(f"Cleaning document: {document.document}")

        cleaned_pages = []

        total_characters = 0

        for page in document.pages:

            cleaned_text = self._clean_text(page.text)

            total_characters += len(cleaned_text)

            cleaned_pages.append(
                ParsedPage(
                    document=page.document,
                    page=page.page,
                    text=cleaned_text,
                    needs_ocr=page.needs_ocr,
                )
            )

        document.pages = cleaned_pages
        document.total_characters = total_characters

        logger.success(
            f"Cleaning completed for {document.document}"
        )

        return document

    def _clean_text(self, text: str) -> str:

        if not text:
            return ""

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        text = re.sub(r"[^\x20-\x7E\n\t]", "", text)

        text = re.sub(r"[ \t]+", " ", text)

        text = re.sub(r"\n{3,}", "\n\n", text)

        text = re.sub(r" *\n *", "\n", text)

        text = text.strip()

        return text