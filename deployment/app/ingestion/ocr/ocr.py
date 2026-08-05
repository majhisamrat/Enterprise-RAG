from pathlib import Path
from typing import Any, List

from app.utils.logger import logger

from app.ingestion.ocr.pdf_to_image import pdf_to_images
from app.ingestion.schemas import ParsedDocument


class OCRProcessor:
    """
    OCR processor using EasyOCR.
    Lazy-loaded: the heavy EasyOCR model is only initialized when OCR is actually needed.
    """

    def __init__(self):
        self._reader = None  # Lazy: don't load until process() is called

    @property
    def reader(self):
        """Load EasyOCR model on first use only."""
        if self._reader is None:
            import easyocr
            logger.info("Loading EasyOCR model (lazy init)...")
            self._reader = easyocr.Reader(["en"], gpu=False)
            logger.success("EasyOCR loaded.")
        return self._reader

    def process(
        self,
        document: ParsedDocument,
        pdf_path: str | Path,
    ) -> ParsedDocument:

        logger.info(f"Running OCR for {document.document}")

        image_map = pdf_to_images(str(pdf_path))

        total_characters = 0

        for page in document.pages:

            if not page.needs_ocr:
                total_characters += len(page.text)
                continue

            page.image_path = image_map.get(int(page.page))

            if page.image_path is None:
                logger.warning(
                    f"No image for page {page.page}"
                )
                continue

            logger.info(f"OCR Page {page.page}")

            page.text = self.extract_text(page.image_path)

            page.needs_ocr = False

            total_characters += len(page.text)

        document.total_characters = total_characters
        document.needs_ocr = False
        document.ocr_used = True
        for image in image_map.values():
            Path(image).unlink(missing_ok=True)

        logger.success("OCR completed.")

        return document

    def extract_text(self, image_path: str) -> str:

        try:

            results: List[Any] = self.reader.readtext(
                image_path,
                detail=0,
                paragraph=True,
            )

            return "\n".join(str(r) for r in results)

        except Exception as e:

            logger.exception(e)

            return ""