import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import TenantContext, get_current_user, get_tenant_context
from app.db.models import BackgroundJob, Document, User
from app.db.repositories.document_repository import DocumentRepository
from app.db.session import get_db
from app.tasks.tasks import process_document_ingestion_task, reindex_document_task
from app.utils.exceptions import DocumentNotFoundError
from app.utils.logger import app_logger

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/")
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List documents belonging to the user's organization."""
    doc_repo = DocumentRepository(db)
    docs = await doc_repo.get_by_organization(
        organization_id=tenant_context.organization_id,
        skip=skip,
        limit=limit,
    )
    return [
        {
            "id": str(d.id),
            "filename": d.filename,
            "title": d.title,
            "file_size": d.file_size,
            "status": d.status,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get document details by UUID."""
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document UUID")

    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get_by_id(doc_uuid)
    if not doc or doc.organization_id != tenant_context.organization_id:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": str(doc.id),
        "organization_id": str(doc.organization_id),
        "owner_id": str(doc.owner_id),
        "filename": doc.filename,
        "title": doc.title,
        "mime_type": doc.mime_type,
        "file_size": doc.file_size,
        "checksum": doc.checksum,
        "storage_path": doc.storage_path,
        "status": doc.status,
        "created_at": doc.created_at.isoformat(),
    }


@router.post("/{document_id}/reindex")
async def reindex_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Trigger background Celery re-indexing task for a document."""
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document UUID")

    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get_by_id(doc_uuid)
    if not doc or doc.organization_id != tenant_context.organization_id:
        raise HTTPException(status_code=404, detail="Document not found")

    # Dispatch Celery background re-indexing task
    job = reindex_document_task.delay(
        document_id=str(doc.id),
        organization_id=str(tenant_context.organization_id),
    )

    # Log BackgroundJob in database
    bg_job = BackgroundJob(
        organization_id=tenant_context.organization_id,
        job_type="reindex_document",
        status="PENDING",
        payload={"document_id": str(doc.id), "celery_job_id": job.id},
    )
    db.add(bg_job)

    return {
        "success": True,
        "job_id": job.id,
        "document_id": str(doc.id),
        "status": "PENDING",
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document and its metadata from PostgreSQL."""
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document UUID")

    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get_by_id(doc_uuid)
    if not doc or doc.organization_id != tenant_context.organization_id:
        raise HTTPException(status_code=404, detail="Document not found")

    await doc_repo.delete(doc)
    return {"success": True, "deleted_document_id": str(doc.id)}
