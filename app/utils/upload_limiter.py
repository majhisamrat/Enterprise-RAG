"""Upload rate limiting service - 5 documents per 24 hours per user."""

from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Upload
from app.utils.logger import logger


class DocumentUploadLimiter:
    """Rate limiter for document uploads - enforces 5 documents per 24 hours."""
    
    MAX_UPLOADS_PER_24H = 5
    WINDOW_HOURS = 24

    @staticmethod
    async def get_upload_count_last_24h(user_id, db: AsyncSession) -> int:
        """Count user's document uploads in the last 24 hours."""
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=DocumentUploadLimiter.WINDOW_HOURS)

        # Query: Count uploads by user from last 24h
        stmt = select(func.count(Upload.id)).where(
            Upload.user_id == user_id,
            Upload.created_at >= cutoff_time
        )

        result = await db.execute(stmt)
        count = result.scalar() or 0
        return count

    @staticmethod
    async def get_earliest_upload_time(user_id, db: AsyncSession) -> Optional[datetime]:
        """Get the timestamp of the earliest upload in the current 24h window."""
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=DocumentUploadLimiter.WINDOW_HOURS)

        stmt = select(func.min(Upload.created_at)).where(
            Upload.user_id == user_id,
            Upload.created_at >= cutoff_time
        )

        result = await db.execute(stmt)
        earliest_time = result.scalar()
        return earliest_time

    @staticmethod
    async def check_upload_limit(user_id, db: AsyncSession) -> Tuple[bool, int, Optional[datetime]]:
        """
        Check if user has exceeded upload limit.
        
        Returns:
            Tuple of (is_allowed, upload_count, reset_time)
            - is_allowed: True if user can upload, False if limit exceeded
            - upload_count: Current count of uploads in last 24h
            - reset_time: When the limit will reset (only if limit exceeded)
        """
        count = await DocumentUploadLimiter.get_upload_count_last_24h(user_id, db)
        
        if count >= DocumentUploadLimiter.MAX_UPLOADS_PER_24H:
            # Limit exceeded - calculate reset time
            earliest_time = await DocumentUploadLimiter.get_earliest_upload_time(user_id, db)
            
            if earliest_time:
                # Reset time is 24 hours after the earliest upload
                reset_time = earliest_time + timedelta(hours=DocumentUploadLimiter.WINDOW_HOURS)
                logger.warning(f"Upload limit exceeded for user {user_id}. Reset at {reset_time}")
                return False, count, reset_time
            else:
                # Shouldn't happen, but fallback to now + 24h
                reset_time = datetime.now(timezone.utc) + timedelta(hours=DocumentUploadLimiter.WINDOW_HOURS)
                return False, count, reset_time
        
        logger.info(f"User {user_id} has {count}/{DocumentUploadLimiter.MAX_UPLOADS_PER_24H} uploads used")
        return True, count, None

    @staticmethod
    def format_reset_time(reset_time: datetime) -> str:
        """Format reset time for display - includes date and time."""
        # Format: "Aug 6, 2026 at 3:45 PM UTC"
        return reset_time.strftime("%b %d, %Y at %I:%M %p %Z")
