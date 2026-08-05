import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import and_, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Upload, VectorMetadata
from app.db.repositories.base import BaseRepository


class UploadRepository(BaseRepository[Upload]):
    """Repository for Upload management."""

    def __init__(self, session: AsyncSession):
        super().__init__(Upload, session)
        self.session = session

    async def get_by_kb(
        self, kb_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Upload]:
        """Get all uploads in a knowledge base."""
        stmt = (
            select(Upload)
            .where(Upload.knowledge_base_id == kb_id)
            .order_by(desc(Upload.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_kb_and_status(
        self, kb_id: uuid.UUID, status: str, skip: int = 0, limit: int = 100
    ) -> List[Upload]:
        """Get uploads in a KB with specific status."""
        stmt = (
            select(Upload)
            .where(
                and_(
                    Upload.knowledge_base_id == kb_id,
                    Upload.processing_status == status,
                )
            )
            .order_by(desc(Upload.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_organization(
        self, organization_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Upload]:
        """Get all uploads in an organization."""
        stmt = (
            select(Upload)
            .where(Upload.organization_id == organization_id)
            .order_by(desc(Upload.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_with_collection(self, upload_id: uuid.UUID) -> Optional[Upload]:
        """Get upload with embedding collection loaded."""
        stmt = select(Upload).where(Upload.id == upload_id)
        res = await self.session.execute(stmt)
        upload = res.scalar_one_or_none()
        if upload:
            await self.session.refresh(upload, ["embedding_collection"])
        return upload

    async def get_latest_by_kb(self, kb_id: uuid.UUID, limit: int = 5) -> List[Upload]:
        """Get latest uploads in a KB."""
        stmt = (
            select(Upload)
            .where(Upload.knowledge_base_id == kb_id)
            .order_by(desc(Upload.created_at))
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_status(
        self, upload_id: uuid.UUID, status: str, error_message: Optional[str] = None
    ) -> Optional[Upload]:
        """Update upload processing status."""
        upload = await self.get_by_id(upload_id)
        if upload:
            upload.processing_status = status
            if error_message:
                upload.error_message = error_message
            if status == "processing" and not upload.processing_start_at:
                upload.processing_start_at = datetime.now(timezone.utc)
            elif status == "completed" and not upload.processing_end_at:
                upload.processing_end_at = datetime.now(timezone.utc)
                if upload.processing_start_at:
                    duration = (
                        upload.processing_end_at - upload.processing_start_at
                    ).total_seconds() * 1000
                    upload.processing_duration_ms = int(duration)
            await self.update(upload)
        return upload

    async def update_vector_counts(
        self,
        upload_id: uuid.UUID,
        page_count: int,
        chunk_count: int,
        total_vectors: int,
    ) -> Optional[Upload]:
        """Update vector counts after processing."""
        upload = await self.get_by_id(upload_id)
        if upload:
            upload.page_count = page_count
            upload.chunk_count = chunk_count
            upload.total_vectors = total_vectors
            await self.update(upload)
        return upload

    async def get_completed_count_by_kb(self, kb_id: uuid.UUID) -> int:
        """Get count of completed uploads in a KB."""
        stmt = select(Upload).where(
            and_(
                Upload.knowledge_base_id == kb_id,
                Upload.processing_status == "completed",
            )
        )
        res = await self.session.execute(stmt)
        return len(list(res.scalars().all()))

    async def get_total_vectors_by_kb(self, kb_id: uuid.UUID) -> int:
        """Get total vectors for a KB."""
        stmt = select(Upload).where(Upload.knowledge_base_id == kb_id)
        res = await self.session.execute(stmt)
        uploads = list(res.scalars().all())
        return sum(u.total_vectors for u in uploads)

    async def delete_with_metadata(self, upload_id: uuid.UUID) -> int:
        """Delete upload and related metadata."""
        # Delete vector metadata first
        vm_stmt = select(VectorMetadata).where(VectorMetadata.upload_id == upload_id)
        vm_res = await self.session.execute(vm_stmt)
        for vm in vm_res.scalars().all():
            await self.session.delete(vm)

        # Delete upload (embedding_collection cascades via FK)
        upload = await self.get_by_id(upload_id)
        if upload:
            await self.session.delete(upload)
            await self.session.flush()
            return 1
        return 0
