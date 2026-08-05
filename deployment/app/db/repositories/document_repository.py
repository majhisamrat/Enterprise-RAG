import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document
from app.db.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(Document, session)

    async def get_by_checksum(self, organization_id: uuid.UUID, checksum: str) -> Optional[Document]:
        stmt = select(Document).where(
            Document.organization_id == organization_id,
            Document.checksum == checksum,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_organization(self, organization_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        stmt = (
            select(Document)
            .where(Document.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
