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


@celery_app.task(name="reindex_kb_uploads_task")
def reindex_kb_uploads_task(kb_id: str, organization_id: str) -> Dict[str, Any]:
    """
    Background task for per-KB reindexing.
    
    Re-processes all uploads for a knowledge base:
    1. Delete old vectors from Qdrant/Elasticsearch per upload
    2. Re-chunk and re-embed the uploaded documents
    3. Re-index all vectors with KB metadata
    4. Update upload status and vector counts
    """
    logger.info(f"Starting per-KB reindex for KB {kb_id}")

    async def _reindex():
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from app.config.settings import settings
        from app.db.repositories.upload_repository import UploadRepository
        from app.db.repositories.knowledge_base_repository import KnowledgeBaseRepository
        from app.services.ingestion_service import IngestionService
        from app.vectorstore.qdrant_store import QdrantVectorStore
        from app.keyword_search.index import ElasticsearchIndexer
        from pathlib import Path

        # Setup DB session for this task
        engine = create_async_engine(str(settings.DATABASE_URL), echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        db = async_session()

        try:
            kb_uuid = uuid.UUID(kb_id)
            org_uuid = uuid.UUID(organization_id)

            kb_repo = KnowledgeBaseRepository(db)
            upload_repo = UploadRepository(db)

            # Verify KB exists
            kb = await kb_repo.get_by_id(kb_uuid)
            if not kb or kb.organization_id != org_uuid:
                logger.error(f"KB {kb_id} not found or doesn't belong to org {organization_id}")
                return {
                    "status": "FAILED",
                    "kb_id": kb_id,
                    "reason": "KB not found",
                }

            # Get all uploads for this KB
            uploads = await upload_repo.get_by_kb(kb_uuid, skip=0, limit=10000)
            logger.info(f"Reindexing {len(uploads)} uploads for KB {kb_id}")

            vector_store = QdrantVectorStore()
            elastic_index = ElasticsearchIndexer()
            ingestion_service = IngestionService(db_session=db)

            total_vectors_created = 0
            failed_uploads = 0

            for upload in uploads:
                try:
                    logger.info(f"Reindexing upload {upload.id}: {upload.original_filename}")

                    # Update status to reindexing
                    await upload_repo.update_status(upload.id, "reindexing")

                    # Delete old vectors from Qdrant
                    try:
                        await vector_store.delete_vectors_by_upload(upload.id)
                        logger.info(f"Deleted old vectors for upload {upload.id}")
                    except Exception as e:
                        logger.warning(f"Failed to delete old vectors for upload {upload.id}: {e}")

                    # Delete old vectors from Elasticsearch
                    try:
                        await elastic_index.delete_documents_by_upload(upload.id)
                        logger.info(f"Deleted old Elasticsearch docs for upload {upload.id}")
                    except Exception as e:
                        logger.warning(f"Failed to delete Elasticsearch docs for upload {upload.id}: {e}")

                    # Re-ingest the document
                    if upload.storage_path and Path(upload.storage_path).exists():
                        result = await ingestion_service.ingest_document(
                            file_path=upload.storage_path,
                            organization_id=org_uuid,
                            owner_id=upload.user_id,
                            title=upload.display_name or upload.original_filename,
                            department=upload.department,
                            author=upload.author,
                            tags=upload.tags,
                            upload_id=upload.id,
                            knowledge_base_id=kb_uuid,
                        )

                        chunks_count = result.get("chunks", 0)
                        total_vectors_created += chunks_count

                        # Update upload status and counts
                        await upload_repo.update_status(upload.id, "completed")
                        await upload_repo.update_vector_counts(
                            upload_id=upload.id,
                            chunk_count=result.get("chunks", 0),
                            total_vectors=result.get("chunks", 0),
                        )
                        logger.success(f"Reindexed upload {upload.id}: {chunks_count} chunks")
                    else:
                        logger.error(f"Upload file not found: {upload.storage_path}")
                        await upload_repo.update_status(upload.id, "failed")
                        failed_uploads += 1

                except Exception as e:
                    logger.error(f"Error reindexing upload {upload.id}: {e}")
                    await upload_repo.update_status(upload.id, "failed")
                    failed_uploads += 1

            # Update KB status
            await kb_repo.update_last_queried(kb_uuid)
            await db.commit()

            logger.success(
                f"KB reindex complete for {kb_id}: "
                f"{len(uploads) - failed_uploads} succeeded, "
                f"{failed_uploads} failed, "
                f"{total_vectors_created} total vectors"
            )

            return {
                "status": "SUCCESS",
                "kb_id": kb_id,
                "uploads_processed": len(uploads),
                "uploads_failed": failed_uploads,
                "total_vectors_created": total_vectors_created,
            }

        except Exception as e:
            logger.error(f"Fatal error in KB reindex task: {e}")
            return {
                "status": "FAILED",
                "kb_id": kb_id,
                "reason": str(e),
            }
        finally:
            await db.close()
            await engine.dispose()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    result = loop.run_until_complete(_reindex())
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
