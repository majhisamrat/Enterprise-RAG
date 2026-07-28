import uuid
from typing import Any, Optional, cast
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import TenantContext, get_current_user, get_tenant_context
from app.db.models import BackgroundJob, User
from app.db.session import get_db
from app.storage.file_validator import validate_extension
from app.storage.uploads import save_upload_file
from app.tasks.tasks import process_document_ingestion_task

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    background_processing: bool = Form(False),
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Upload and ingest an enterprise document (sync or async Celery job)."""
    try:
        validate_extension(file.filename)
        uploaded_file = save_upload_file(file)

        owner_id = getattr(current_user, "id", None) or uuid.uuid4()
        org_id = tenant_context.organization_id or getattr(current_user, "organization_id", None) or uuid.uuid4()

        if background_processing:
            # Dispatch async Celery background task
            job = cast(Any, process_document_ingestion_task).delay(
                file_path=uploaded_file["path"],
                organization_id=str(org_id),
                owner_id=str(owner_id),
                title=title or file.filename,
                department=department or tenant_context.department,
            )

            # Record BackgroundJob in PostgreSQL
            bg_job = BackgroundJob(
                organization_id=org_id,
                job_type="document_ingestion",
                status="PENDING",
                payload={
                    "file_path": uploaded_file["path"],
                    "celery_job_id": job.id,
                    "filename": file.filename,
                },
            )
            db.add(bg_job)

            return {
                "success": True,
                "background_processing": True,
                "job_id": job.id,
                "status": "PENDING",
                "filename": uploaded_file["original_name"],
            }
        else:
            # Synchronous processing with lazy-loaded IngestionService
            from app.services.ingestion_service import IngestionService
            ingestion_service = IngestionService(db_session=db)
            result = await ingestion_service.ingest_document(
                file_path=uploaded_file["path"],
                organization_id=org_id,
                owner_id=owner_id,
                title=title or file.filename,
                department=department or tenant_context.department,
            )

            return {
                "success": True,
                "background_processing": False,
                "document_id": result["document_id"],
                "title": result["title"],
                "chunks_count": result["chunks"],
                "status": result["status"],
                "filename": uploaded_file["original_name"],
            }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ingestion failed: {e}")