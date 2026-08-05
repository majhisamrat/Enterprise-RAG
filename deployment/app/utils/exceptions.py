"""
Application Exception Hierarchy
"""
from typing import Any, Dict, Optional


class BaseRAGException(Exception):
    """Base exception for Enterprise RAG application."""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(BaseRAGException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Invalid credentials or token"):
        super().__init__(message=message, status_code=401)


class PermissionDeniedError(BaseRAGException):
    """Raised when user lacks required permission or tenant context."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, status_code=403)


class DocumentNotFoundError(BaseRAGException):
    """Raised when document is not found."""

    def __init__(self, document_id: str):
        super().__init__(message=f"Document '{document_id}' not found", status_code=404)


class IngestionError(BaseRAGException):
    """Raised during document ingestion failure."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=422, details=details)


class VectorStoreError(BaseRAGException):
    """Raised on Qdrant vector store operations error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)


class SearchIndexError(BaseRAGException):
    """Raised on Elasticsearch BM25 index operations error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)


class LLMProviderError(BaseRAGException):
    """Raised on Gemini LLM provider failure."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=502, details=details)


class StorageError(BaseRAGException):
    """Raised during file storage operations."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)
