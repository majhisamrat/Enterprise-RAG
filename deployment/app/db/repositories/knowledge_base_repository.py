import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import KnowledgeBase, Upload, VectorMetadata, QueryLog
from app.db.repositories.base import BaseRepository


class KnowledgeBaseRepository(BaseRepository[KnowledgeBase]):
    """Repository for Knowledge Base management."""

    def __init__(self, session: AsyncSession):
        super().__init__(KnowledgeBase, session)
        self.session = session

    async def get_by_organization(
        self, organization_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[KnowledgeBase]:
        """Get all knowledge bases for an organization."""
        stmt = (
            select(KnowledgeBase)
            .where(KnowledgeBase.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .order_by(KnowledgeBase.last_queried_at.desc().nullslast())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_user(
        self, user_id: uuid.UUID, organization_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[KnowledgeBase]:
        """Get all knowledge bases created by a user."""
        stmt = (
            select(KnowledgeBase)
            .where(
                and_(
                    KnowledgeBase.user_id == user_id,
                    KnowledgeBase.organization_id == organization_id,
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(KnowledgeBase.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_name(
        self, organization_id: uuid.UUID, name: str
    ) -> Optional[KnowledgeBase]:
        """Get knowledge base by name within organization."""
        stmt = select(KnowledgeBase).where(
            and_(
                KnowledgeBase.organization_id == organization_id,
                KnowledgeBase.name == name,
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_with_uploads(self, kb_id: uuid.UUID) -> Optional[KnowledgeBase]:
        """Get knowledge base with all uploads loaded."""
        stmt = select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        res = await self.session.execute(stmt)
        kb = res.scalar_one_or_none()
        if kb:
            # Ensure uploads are loaded
            await self.session.refresh(kb, ["uploads"])
        return kb

    async def get_statistics(self, kb_id: uuid.UUID) -> dict:
        """Get aggregated statistics for a knowledge base."""
        # Query uploads for KB
        uploads_stmt = select(Upload).where(Upload.knowledge_base_id == kb_id)
        uploads_res = await self.session.execute(uploads_stmt)
        uploads = list(uploads_res.scalars().all())

        total_pages = sum(u.page_count for u in uploads)
        total_chunks = sum(u.chunk_count for u in uploads)
        total_vectors = sum(u.total_vectors for u in uploads)
        avg_processing_time = (
            sum(u.processing_duration_ms for u in uploads) / len(uploads)
            if uploads
            else 0
        )

        # Query logs for KB
        query_logs_stmt = select(func.count(QueryLog.id)).where(
            QueryLog.knowledge_base_id == kb_id
        )
        query_logs_res = await self.session.execute(query_logs_stmt)
        query_count = query_logs_res.scalar() or 0

        return {
            "total_uploads": len(uploads),
            "total_pages": total_pages,
            "total_chunks": total_chunks,
            "total_vectors": total_vectors,
            "avg_processing_time_ms": avg_processing_time,
            "query_count": query_count,
        }

    async def update_last_queried(self, kb_id: uuid.UUID) -> None:
        """Update last_queried_at timestamp and increment query_count."""
        kb = await self.get_by_id(kb_id)
        if kb:
            kb.last_queried_at = datetime.now(timezone.utc)
            kb.query_count = (kb.query_count or 0) + 1
            await self.update(kb)

    async def delete_cascade(self, kb_id: uuid.UUID, vector_store=None) -> int:
        """Delete knowledge base and all related data (cascade).
        
        Args:
            kb_id: Knowledge base ID to delete
            vector_store: Optional QdrantVectorStore instance to delete Qdrant collections
        """
        kb = await self.get_by_id(kb_id)
        if kb:
            # Delete Qdrant collection if vector store provided
            if vector_store:
                try:
                    await vector_store.delete_collection(kb_id)
                except Exception as e:
                    # Log but don't fail - database deletion is primary
                    from app.utils.logger import logger
                    logger.warning(f"Failed to delete Qdrant collection for KB {kb_id}: {e}")
            
            # Delete from database
            await self.session.delete(kb)
            await self.session.flush()
            return 1
        return 0
