from pathlib import Path
from app.utils.logger import logger

from app.ingestion.cleaners.cleaner import TextCleaner
from app.ingestion.ocr.ocr import OCRProcessor
from app.ingestion.parsers.opendataloader_parser import OpenDataLoaderParser
from app.ingestion.parsers.pymupdf_parser import DocumentParser
from app.ingestion.schemas import ParsedDocument


class ParserFactory:
    """Fast, production-grade parser factory using PyMuPDF as primary fast engine."""

    def __init__(self):
        self.primary = DocumentParser()  # PyMuPDF: sub-50ms fast native parser
        self.fallback = OpenDataLoaderParser()
        self.ocr = OCRProcessor()
        self.cleaner = TextCleaner()

    def parse(self, file_path: str | Path) -> ParsedDocument:
        file_path = Path(file_path)

        try:
            document = self.primary.parse(file_path)
            logger.success("Parsed successfully using PyMuPDF.")
        except Exception as e:
            logger.warning(f"PyMuPDF parsing failed: {e}. Falling back to OpenDataLoader...")
            document = self.fallback.parse(file_path)
            logger.success("Parsed successfully using OpenDataLoader.")

        logger.info(
            f"Needs OCR: {document.needs_ocr}, "
            f"Characters: {document.total_characters}"
        )

        if document.needs_ocr:
            logger.info("Starting OCR pipeline...")
            document = self.ocr.process(document, file_path)
            logger.success("OCR completed.")

        logger.info("Starting text cleaning...")
        document = self.cleaner.clean(document)
        logger.success("Text cleaning completed.")

        return document