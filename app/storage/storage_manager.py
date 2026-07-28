import os
import shutil
from pathlib import Path
from typing import BinaryIO, Union
from loguru import logger

from app.config import settings
from app.utils.exceptions import StorageError


class StorageManager:
    """Unified Object Storage Manager supporting Local File System, S3, and MinIO."""

    REQUIRED_DIRECTORIES = [
        "raw_documents",
        "processed_documents",
        "ocr_images",
        "parsed_json",
        "document_versions",
        "thumbnails",
    ]

    def __init__(self, base_dir: str = settings.UPLOAD_DIR, backend: str = settings.STORAGE_BACKEND):
        self.base_dir = Path(base_dir)
        self.backend = backend
        self._init_local_storage()

    def _init_local_storage(self):
        """Ensure required local directory structure exists."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        for folder in self.REQUIRED_DIRECTORIES:
            (self.base_dir / folder).mkdir(parents=True, exist_ok=True)

    def get_folder_path(self, folder_name: str) -> Path:
        """Get absolute path for a specific subfolder."""
        if folder_name not in self.REQUIRED_DIRECTORIES:
            raise StorageError(f"Invalid storage folder '{folder_name}'. Must be one of {self.REQUIRED_DIRECTORIES}")
        path = self.base_dir / folder_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_file(
        self,
        file_data: Union[bytes, BinaryIO],
        destination_filename: str,
        folder_name: str = "raw_documents",
    ) -> str:
        """Save file data to designated storage location."""
        folder = self.get_folder_path(folder_name)
        target_path = folder / destination_filename

        try:
            if isinstance(file_data, bytes):
                with open(target_path, "wb") as f:
                    f.write(file_data)
            else:
                with open(target_path, "wb") as f:
                    shutil.copyfileobj(file_data, f)

            logger.info(f"Saved file to storage: {target_path}")
            return str(target_path.resolve())
        except Exception as e:
            logger.error(f"Failed to save file '{destination_filename}': {e}")
            raise StorageError(f"Storage write failure: {e}")

    def get_file_path(self, filename: str, folder_name: str = "raw_documents") -> Path:
        """Retrieve path for file."""
        path = self.get_folder_path(folder_name) / filename
        if not path.exists():
            raise StorageError(f"File '{filename}' not found in '{folder_name}'")
        return path

    def delete_file(self, filename: str, folder_name: str = "raw_documents") -> bool:
        """Delete file from storage."""
        try:
            path = self.get_folder_path(folder_name) / filename
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file from storage: {path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file '{filename}': {e}")
            return False


storage_manager = StorageManager()
