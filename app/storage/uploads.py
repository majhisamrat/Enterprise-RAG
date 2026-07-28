from pathlib import Path
from typing import Any, Dict
from uuid import uuid4
from fastapi import UploadFile

from app.storage.storage_manager import storage_manager


def save_upload_file(file: UploadFile) -> Dict[str, Any]:
    """Save UploadFile using storage manager and return upload metadata."""
    original_filename = file.filename or "document.tmp"
    extension = Path(original_filename).suffix.lower()
    unique_filename = f"{uuid4().hex}{extension}"

    file_path = storage_manager.save_file(
        file_data=file.file,
        destination_filename=unique_filename,
        folder_name="raw_documents",
    )

    return {
        "filename": unique_filename,
        "original_name": original_filename,
        "path": file_path,
        "size": getattr(file, "size", 0) or 0,
        "content_type": file.content_type or "application/octet-stream",
    }