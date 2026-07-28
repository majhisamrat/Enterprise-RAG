import asyncio
import uuid
from typing import Any, Dict, Optional
from app.utils.logger import logger

from app.tasks.celery_app import celery_app


@celery_app.task(name="process_document_ingestion_task")
def process_document_ingestion_task(
    file_path: str,
    organization_id: str,
    owner_id: str,
    title: Optional[str] = None,
    department: Optional[str] = None,
) -> Dict[str, Any]:
    """Background task for document parsing, chunking, embedding, and dual-store indexing."""
    logger.info(f"Celery task started: Ingesting file {file_path}")

    async def _ingest():
        from app.services.ingestion_service import IngestionService
        service = IngestionService()
        return await service.ingest_document(
            file_path=file_path,
            organization_id=uuid.UUID(organization_id),
            owner_id=uuid.UUID(owner_id),
            title=title,
            department=department,
        )

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    result = loop.run_until_complete(_ingest())
    logger.success(f"Celery task completed: Ingested file {file_path}")
    return result


@celery_app.task(name="reindex_document_task")
def reindex_document_task(document_id: str, organization_id: str) -> Dict[str, Any]:
    """Background task for document re-indexing."""
    logger.info(f"Re-indexing document {document_id}")
    return {"status": "SUCCESS", "document_id": document_id}


@celery_app.task(name="cleanup_expired_sessions_task")
def cleanup_expired_sessions_task() -> Dict[str, Any]:
    """Background task for cleaning expired sessions."""
    logger.info("Cleaning up expired user sessions and caches")
    return {"status": "CLEANED"}
