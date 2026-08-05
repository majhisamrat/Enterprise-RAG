from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import UploadFile, HTTPException

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".xls",
    ".csv",
    ".html",
    ".htm",
    ".md",
    ".txt",
}


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class DocumentLoader:
    """
    Handles uploaded documents.
    """

    def __init__(self):
        self.upload_dir = UPLOAD_DIR

    def validate(self, file: UploadFile) -> None:
        extension = Path(file.filename).suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {extension}",
            )

    def save(self, file: UploadFile) -> Path:
        """
        Save uploaded file locally.

        Returns:
            Path to saved file.
        """

        self.validate(file)

        extension = Path(file.filename).suffix.lower()

        unique_name = f"{uuid4().hex}{extension}"

        destination = self.upload_dir / unique_name

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return destination

    def info(self, file_path: Path) -> dict:
        return {
            "filename": file_path.name,
            "path": str(file_path),
            "size_bytes": file_path.stat().st_size,
            "extension": file_path.suffix.lower(),
        }