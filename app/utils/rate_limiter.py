"""Rate limiting service for chat messages - 10 messages per 24 hours per user."""

from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ChatMessage, ChatSession
from app.utils.logger import logger


class ChatRateLimiter:
    """Rate limiter for chat messages - enforces 10 messages per 24 hours."""
    
    MAX_MESSAGES_PER_24H = 10
    WINDOW_HOURS = 24

    @staticmethod
    async def get_message_count_last_24h(user_id, db: AsyncSession) -> int:
        """Count user's chat messages in the last 24 hours."""
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=ChatRateLimiter.WINDOW_HOURS)

        # Query: Join ChatSession and ChatMessage to count user messages from last 24h
        stmt = select(func.count(ChatMessage.id)).select_from(ChatMessage).join(
            ChatSession, ChatMessage.session_id == ChatSession.id
        ).where(
            ChatSession.user_id == user_id,
            ChatMessage.sender_role == "user",  # Only count user messages, not assistant
            ChatMessage.created_at >= cutoff_time
        )

        result = await db.execute(stmt)
        count = result.scalar() or 0
        return count

    @staticmethod
    async def get_earliest_message_time(user_id, db: AsyncSession) -> Optional[datetime]:
        """Get the timestamp of the earliest message in the current 24h window."""
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=ChatRateLimiter.WINDOW_HOURS)

        stmt = select(func.min(ChatMessage.created_at)).select_from(ChatMessage).join(
            ChatSession, ChatMessage.session_id == ChatSession.id
        ).where(
            ChatSession.user_id == user_id,
            ChatMessage.sender_role == "user",
            ChatMessage.created_at >= cutoff_time
        )

        result = await db.execute(stmt)
        earliest_time = result.scalar()
        return earliest_time

    @staticmethod
    async def check_rate_limit(user_id, db: AsyncSession) -> Tuple[bool, int, Optional[datetime]]:
        """
        Check if user has exceeded rate limit.
        
        Returns:
            Tuple of (is_allowed, message_count, reset_time)
            - is_allowed: True if user can send a message, False if limit exceeded
            - message_count: Current count of messages in last 24h
            - reset_time: When the limit will reset (only if limit exceeded)
        """
        count = await ChatRateLimiter.get_message_count_last_24h(user_id, db)
        
        if count >= ChatRateLimiter.MAX_MESSAGES_PER_24H:
            # Limit exceeded - calculate reset time
            earliest_time = await ChatRateLimiter.get_earliest_message_time(user_id, db)
            
            if earliest_time:
                # Reset time is 24 hours after the earliest message
                reset_time = earliest_time + timedelta(hours=ChatRateLimiter.WINDOW_HOURS)
                logger.warning(f"Rate limit exceeded for user {user_id}. Reset at {reset_time}")
                return False, count, reset_time
            else:
                # Shouldn't happen, but fallback to now + 24h
                reset_time = datetime.now(timezone.utc) + timedelta(hours=ChatRateLimiter.WINDOW_HOURS)
                return False, count, reset_time
        
        logger.info(f"User {user_id} has {count}/{ChatRateLimiter.MAX_MESSAGES_PER_24H} messages used")
        return True, count, None

    @staticmethod
    def format_reset_time(reset_time: datetime) -> str:
        """Format reset time for display - includes date and time."""
        # Format: "Aug 6, 2026 at 3:45 PM UTC"
        return reset_time.strftime("%b %d, %Y at %I:%M %p %Z")
