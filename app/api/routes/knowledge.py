"""
Knowledge Base Management API endpoints.

Replaces /documents with /knowledge for Embedding Knowledge Platform.
Provides KB creation, upload management, filtering, and statistics.
"""

import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import TenantContext, get_current_user, get_tenant_context
from app.db.models import KnowledgeBase, Upload, User, BackgroundJob
from app.db.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.db.repositories.upload_repository import UploadRepository
from app.db.session import get_db
from app.storage.file_validator import validate_extension
from app.storage.uploads import save_upload_file
from app.tasks.tasks import process_document_ingestion_task
from app.utils.logger import app_logger
from app.utils.upload_limiter import DocumentUploadLimiter

router = APIRouter(prefix="/knowledge", tags=["Knowledge Bases"])


# ──────────────────────────────────────────────────────────────────────────────
# Knowledge Base Management Endpoints
# ──────────────────────────────────────────────────────────────────────────────


@router.post("", response_model=Dict[str, Any])
@router.post("/", response_model=Dict[str, Any], include_in_schema=False)
async def create_knowledge_base(
    name: str = Form(...),
    display_name: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new knowledge base for organizing document uploads.

    - **name**: Unique identifier (e.g., "Sales_2026")
    - **display_name**: Human-readable name (e.g., "Sales Q1-Q4 2026")
    - **description**: Optional description
    """
    try:
        # Check if KB with same name exists
        kb_repo = KnowledgeBaseRepository(db)
        existing = await kb_repo.get_by_name(tenant_context.organization_id, name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Knowledge base with name '{name}' already exists",
            )

        # Create new KB
        new_kb = KnowledgeBase(
            organization_id=tenant_context.organization_id,
            user_id=current_user.id,
            name=name,
            display_name=display_name,
            description=description,
            status="active",
            query_count=0,
        )
        kb = await kb_repo.create(new_kb)
        await db.commit()

        app_logger.info(f"Created knowledge base: {name} (ID: {kb.id})")

        return {
            "id": str(kb.id),
            "name": kb.name,
            "display_name": kb.display_name,
            "description": kb.description,
            "status": kb.status,
            "created_at": kb.created_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error creating KB: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to create knowledge base"
        )


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]], include_in_schema=False)
async def list_knowledge_bases(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    List knowledge bases for the organization.

    - **skip**: Pagination offset
    - **limit**: Max results per page
    - **status**: Filter by status (active, archived, deleted)
    """
    try:
        kb_repo = KnowledgeBaseRepository(db)
        kbs = await kb_repo.get_by_organization(
            organization_id=tenant_context.organization_id,
            skip=skip,
            limit=limit,
        )

        # Filter by status if provided
        if status:
            kbs = [kb for kb in kbs if kb.status == status]

        return [
            {
                "id": str(kb.id),
                "name": kb.name,
                "display_name": kb.display_name,
                "status": kb.status,
                "query_count": kb.query_count,
                "last_queried_at": kb.last_queried_at.isoformat() if kb.last_queried_at else None,
                "created_at": kb.created_at.isoformat(),
                "updated_at": kb.updated_at.isoformat(),
            }
            for kb in kbs
        ]
    except Exception as e:
        app_logger.error(f"Error listing KBs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list knowledge bases")


@router.get("/{kb_id}", response_model=Dict[str, Any])
async def get_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get knowledge base details by ID.

    Returns KB metadata, upload count, and statistics.
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid KB UUID")

    try:
        kb_repo = KnowledgeBaseRepository(db)
        kb = await kb_repo.get_by_id(kb_uuid)

        if not kb or kb.organization_id != tenant_context.organization_id:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        # Get statistics
        stats = await kb_repo.get_statistics(kb_uuid)

        return {
            "id": str(kb.id),
            "name": kb.name,
            "display_name": kb.display_name,
            "description": kb.description,
            "status": kb.status,
            "query_count": kb.query_count,
            "last_queried_at": kb.last_queried_at.isoformat() if kb.last_queried_at else None,
            "created_at": kb.created_at.isoformat(),
            "updated_at": kb.updated_at.isoformat(),
            "statistics": stats,
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error getting KB: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve knowledge base")


@router.delete("/{kb_id}", response_model=Dict[str, Any])
async def delete_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a knowledge base and all related data (cascading delete).

    This will delete:
    - All uploads and their vectors
    - All chat sessions for this KB
    - All query logs
    - All metadata
    - Qdrant collection for this KB
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid KB UUID")

    try:
        kb_repo = KnowledgeBaseRepository(db)
        kb = await kb_repo.get_by_id(kb_uuid)

        if not kb or kb.organization_id != tenant_context.organization_id:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        # Initialize vector store for Qdrant collection deletion
        from app.vectorstore.qdrant_store import QdrantVectorStore
        vector_store = QdrantVectorStore()

        # Delete KB and associated Qdrant collection
        deleted_count = await kb_repo.delete_cascade(kb_uuid, vector_store=vector_store)

        if deleted_count > 0:
            await db.commit()
            app_logger.info(f"Deleted knowledge base: {kb.name} (ID: {kb_uuid}) with Qdrant cleanup")

            return {
                "success": True,
                "deleted_kb_id": str(kb_uuid),
                "message": f"Deleted knowledge base '{kb.name}' and all related data including Qdrant vectors",
            }
        else:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error deleting KB: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete knowledge base")


# ──────────────────────────────────────────────────────────────────────────────
# Upload Management Endpoints
# ──────────────────────────────────────────────────────────────────────────────


@router.post("/{kb_id}/upload", response_model=Dict[str, Any])
async def upload_document_to_kb(
    kb_id: str,
    file: UploadFile = File(...),
    display_name: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    background_processing: bool = Form(True),
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a document to a knowledge base.

    - **kb_id**: Knowledge base UUID
    - **file**: PDF, DOCX, TXT, or MD file
    - **display_name**: Optional display name (defaults to filename)
    - **tags**: Optional comma-separated tags
    - **background_processing**: Process async (default: true) or sync (false)
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid KB UUID")

    try:
        # 🔐 CHECK UPLOAD LIMIT FIRST
        is_allowed, upload_count, reset_time = await DocumentUploadLimiter.check_upload_limit(current_user.id, db)
        
        if not is_allowed:
            # User has exceeded upload limit
            reset_time_str = DocumentUploadLimiter.format_reset_time(reset_time) if reset_time else "Unknown"
            
            app_logger.warning(
                f"Upload limit exceeded for user {current_user.id}. "
                f"Uploads: {upload_count}/{DocumentUploadLimiter.MAX_UPLOADS_PER_24H}. "
                f"Reset: {reset_time_str}"
            )
            
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Upload limit exceeded",
                    "message": f"You have reached your limit of {DocumentUploadLimiter.MAX_UPLOADS_PER_24H} documents per 24 hours.",
                    "reset_time": reset_time_str,
                    "upload_count": upload_count,
                    "max_uploads": DocumentUploadLimiter.MAX_UPLOADS_PER_24H,
                }
            )
        
        # Verify KB exists and belongs to org
        kb_repo = KnowledgeBaseRepository(db)
        kb = await kb_repo.get_by_id(kb_uuid)

        if not kb or kb.organization_id != tenant_context.organization_id:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        # Validate file
        validate_extension(file.filename)
        uploaded_file = save_upload_file(file)

        # Parse tags
        tags_list = [t.strip() for t in tags.split(",")] if tags else []

        # Create Upload record
        upload = Upload(
            knowledge_base_id=kb_uuid,
            organization_id=tenant_context.organization_id,
            user_id=current_user.id,
            original_filename=file.filename,
            display_name=display_name or file.filename,
            file_type=uploaded_file.get("file_type") or Path(file.filename or "").suffix.lstrip(".").lower() or "txt",
            file_size_bytes=uploaded_file["size"],
            storage_path=uploaded_file["path"],
            processing_status="pending",
            tags=tags_list,
            embedding_model="BAAI/bge-small-en-v1.5",
            embedding_dimension=384,
        )
        upload_repo = UploadRepository(db)
        upload = await upload_repo.create(upload)
        await db.commit()

        if background_processing:
            try:
                # Dispatch async Celery task
                job = process_document_ingestion_task.delay(
                    upload_id=str(upload.id),
                    file_path=uploaded_file["path"],
                    kb_id=str(kb_uuid),
                    organization_id=str(tenant_context.organization_id),
                    user_id=str(current_user.id),
                )

                # Record background job
                bg_job = BackgroundJob(
                    organization_id=tenant_context.organization_id,
                    job_type="document_ingestion",
                    status="PENDING",
                    payload={
                        "upload_id": str(upload.id),
                        "celery_job_id": job.id,
                        "filename": file.filename,
                    },
                )
                db.add(bg_job)
                await db.commit()

                app_logger.info(f"Queued async ingestion for upload: {upload.id}")

                return {
                    "success": True,
                    "upload_id": str(upload.id),
                    "kb_id": str(kb_uuid),
                    "filename": uploaded_file["original_name"],
                    "status": "PENDING",
                    "background_processing": True,
                    "job_id": job.id,
                }
            except Exception as cel_err:
                app_logger.warning(f"Celery dispatch failed ({cel_err}). Falling back to sync ingestion...")
                background_processing = False

        if not background_processing:
            # Sync processing fallback
            from app.services.ingestion_service import IngestionService

            ingestion_service = IngestionService(db_session=db)
            result = await ingestion_service.ingest_document(
                file_path=uploaded_file["path"],
                organization_id=tenant_context.organization_id,
                owner_id=current_user.id,
                title=display_name or file.filename,
                upload_id=upload.id,
                knowledge_base_id=kb_uuid,
            )

            # Update upload record
            upload = await upload_repo.update_status(str(upload.id), "completed")
            await upload_repo.update_vector_counts(
                upload.id,
                result.get("chunks", 0),
                result.get("chunks", 0),
                result.get("chunks", 0),
            )
            await db.commit()

            app_logger.info(f"Completed sync ingestion for upload: {upload.id}")

            return {
                "success": True,
                "upload_id": str(upload.id),
                "kb_id": str(kb_uuid),
                "filename": uploaded_file["original_name"],
                "status": "COMPLETED",
                "background_processing": False,
                "pages": result.get("pages"),
                "chunks": result.get("chunks"),
                "vectors": result.get("chunks"),
            }


    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document")


@router.get("/{kb_id}/history", response_model=Dict[str, Any])
async def get_upload_history(
    kb_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get upload history for a knowledge base.

    - **kb_id**: Knowledge base UUID
    - **skip**: Pagination offset
    - **limit**: Max results
    - **status**: Filter by status (pending, processing, completed, failed)
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid KB UUID")

    try:
        kb_repo = KnowledgeBaseRepository(db)
        kb = await kb_repo.get_by_id(kb_uuid)

        if not kb or kb.organization_id != tenant_context.organization_id:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        upload_repo = UploadRepository(db)
        uploads = await upload_repo.get_by_kb(kb_uuid, skip=skip, limit=limit)

        # Filter by status if provided
        if status:
            uploads = [u for u in uploads if u.processing_status == status]

        return {
            "kb_id": str(kb_uuid),
            "uploads": [
                {
                    "id": str(u.id),
                    "original_filename": u.original_filename,
                    "display_name": u.display_name,
                    "file_type": u.file_type,
                    "file_size_bytes": u.file_size_bytes,
                    "page_count": u.page_count,
                    "chunk_count": u.chunk_count,
                    "total_vectors": u.total_vectors,
                    "embedding_model": u.embedding_model,
                    "processing_status": u.processing_status,
                    "processing_duration_ms": u.processing_duration_ms,
                    "error_message": u.error_message,
                    "tags": u.tags,
                    "created_at": u.created_at.isoformat(),
                    "updated_at": u.updated_at.isoformat(),
                }
                for u in uploads
            ],
            "total": len(uploads),
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error getting upload history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve upload history")


@router.get("/{kb_id}/statistics", response_model=Dict[str, Any])
async def get_kb_statistics(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get aggregated statistics for a knowledge base.

    Returns: pages, chunks, vectors, query count, upload count, etc.
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid KB UUID")

    try:
        kb_repo = KnowledgeBaseRepository(db)
        kb = await kb_repo.get_by_id(kb_uuid)

        if not kb or kb.organization_id != tenant_context.organization_id:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        stats = await kb_repo.get_statistics(kb_uuid)

        return {
            "kb_id": str(kb_uuid),
            "kb_name": kb.name,
            **stats,
            "last_queried_at": kb.last_queried_at.isoformat() if kb.last_queried_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error getting KB statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@router.post("/{kb_id}/reindex", response_model=Dict[str, Any])
async def reindex_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Reindex a single knowledge base (per-KB reindexing).

    This will re-process only the uploads in this KB without affecting others.
    Queues a single Celery task that processes all uploads for the KB.
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid KB UUID")

    try:
        kb_repo = KnowledgeBaseRepository(db)
        kb = await kb_repo.get_by_id(kb_uuid)

        if not kb or kb.organization_id != tenant_context.organization_id:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        # Get all uploads for this KB to verify non-empty
        upload_repo = UploadRepository(db)
        uploads = await upload_repo.get_by_kb(kb_uuid, skip=0, limit=1000)

        if not uploads:
            return {
                "success": True,
                "kb_id": str(kb_uuid),
                "message": "No uploads to reindex",
                "uploads_reindexed": 0,
                "job_id": None,
            }

        # Queue single reindex task for the entire KB
        from app.tasks.tasks import reindex_kb_uploads_task

        job = reindex_kb_uploads_task.delay(
            kb_id=str(kb_uuid),
            organization_id=str(tenant_context.organization_id),
        )

        app_logger.info(
            f"Queued per-KB reindex for KB {kb_uuid} with {len(uploads)} uploads (Job ID: {job.id})"
        )

        return {
            "success": True,
            "kb_id": str(kb_uuid),
            "kb_name": kb.name,
            "uploads_count": len(uploads),
            "job_id": job.id,
            "status": "PENDING",
            "message": f"Reindexing queued for {len(uploads)} uploads in KB '{kb.name}'",
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error reindexing KB: {e}")
        raise HTTPException(status_code=500, detail="Failed to reindex knowledge base")
