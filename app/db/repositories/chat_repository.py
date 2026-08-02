import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage, ChatSession
from app.db.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatSession]):
    def __init__(self, session: AsyncSession):
        super().__init__(ChatSession, session)

    async def get_session_by_id(self, session_id: uuid.UUID) -> Optional[ChatSession]:
        """Get a chat session by ID without loading messages."""
        stmt = select(ChatSession).where(ChatSession.id == session_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_session_with_messages(self, session_id: uuid.UUID) -> Optional[ChatSession]:
        stmt = (
            select(ChatSession)
            .where(ChatSession.id == session_id)
            .options(selectinload(ChatSession.messages).selectinload(ChatMessage.retrieved_sources))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_user_sessions(self, user_id: uuid.UUID, limit: int = 50) -> List[ChatSession]:
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def add_message(self, message: ChatMessage) -> ChatMessage:
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message
