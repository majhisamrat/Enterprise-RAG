from pathlib import Path
import shutil
import tempfile

# import opendataloader_pdf  # Optional: not in requirements - disabled
import pymupdf as fitz
from loguru import logger

from app.ingestion.schemas import ParsedDocument, ParsedPage


class OpenDataLoaderParser:

    def parse(self, pdf_path: str | Path) -> ParsedDocument:

        pdf_path = Path(pdf_path)

        output_dir = Path(tempfile.mkdtemp())

        try:
            logger.info(f"Parsing {pdf_path.name} using OpenDataLoader (fallback to fitz)...")

            # Fallback to fitz since opendataloader_pdf is not installed
            with fitz.open(pdf_path) as pdf:
                markdown = ""
                for page_num in range(len(pdf)):
                    page = pdf[page_num]
                    text = page.get_text()
                    markdown += f"\n\n--- Page {page_num + 1} ---\n\n{text}"
                page_count = len(pdf)

            markdown = markdown.strip()

            # Decide whether OCR is needed
            needs_ocr = (
                len(markdown) < 50
                or len(markdown.split()) < 20
            )

            logger.info(
                f"Markdown characters: {len(markdown)} | "
                f"Needs OCR: {needs_ocr}"
            )

            return ParsedDocument(
                document=pdf_path.name,
                file_type="pdf",
                page_count=page_count,
                total_characters=len(markdown),
                needs_ocr=needs_ocr,
                ocr_used=False,
                pages=[
                    ParsedPage(
                        document=pdf_path.name,
                        page=1,
                        text=markdown,
                        needs_ocr=needs_ocr,
                    )
                ],
            )

        except Exception as e:
            logger.exception(e)
            raise RuntimeError(
                f"OpenDataLoader parsing failed: {e}"
            )

        finally:
            shutil.rmtree(output_dir, ignore_errors=True)