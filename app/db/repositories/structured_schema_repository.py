"""
PHASE 2: Repository for StructuredFileSchema persistence.

Methods for reading/writing schema metadata without modification during query time.
"""

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models import StructuredFileSchema
from app.utils.logger import logger


class StructuredSchemaRepository:
    """Repository for persisting and querying structured file schemas."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_by_upload_id(self, upload_id: uuid.UUID) -> Optional[StructuredFileSchema]:
        """Get schema for a specific upload."""
        stmt = select(StructuredFileSchema).where(
            StructuredFileSchema.upload_id == upload_id
        ).order_by(StructuredFileSchema.schema_version.desc())
        
        result = await self.db_session.execute(stmt)
        return result.scalars().first()
    
    async def get_all_versions(self, upload_id: uuid.UUID) -> List[StructuredFileSchema]:
        """Get all schema versions for an upload (for audit trail)."""
        stmt = select(StructuredFileSchema).where(
            StructuredFileSchema.upload_id == upload_id
        ).order_by(StructuredFileSchema.schema_version.desc())
        
        result = await self.db_session.execute(stmt)
        return result.scalars().all()
    
    async def list_by_kb(
        self,
        knowledge_base_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StructuredFileSchema]:
        """List all schemas in a knowledge base."""
        stmt = (
            select(StructuredFileSchema)
            .where(StructuredFileSchema.knowledge_base_id == knowledge_base_id)
            .order_by(StructuredFileSchema.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db_session.execute(stmt)
        return result.scalars().all()
    
    async def upsert_for_upload(
        self,
        upload_id: uuid.UUID,
        knowledge_base_id: uuid.UUID,
        columns: dict,
        sheet_name: Optional[str] = None,
    ) -> StructuredFileSchema:
        """
        Create or replace schema for an upload.
        
        Schema versioning rule: On re-ingest, create NEW record with incremented version.
        Old versions are preserved for audit trail.
        
        Args:
            upload_id: Upload ID
            knowledge_base_id: KB context
            columns: Dict of column metadata (from SchemaDiscoveryEngine.discover())
            sheet_name: Sheet name (XLSX only)
        
        Returns:
            Created or updated StructuredFileSchema record
        """
        # Get latest version
        latest = await self.get_by_upload_id(upload_id)
        next_version = (latest.schema_version + 1) if latest else 1
        
        schema = StructuredFileSchema(
            upload_id=upload_id,
            knowledge_base_id=knowledge_base_id,
            sheet_name=sheet_name,
            schema_version=next_version,
            columns=columns,
        )
        
        self.db_session.add(schema)
        await self.db_session.flush()
        
        logger.info(
            f"Upserted schema for upload {upload_id}: "
            f"version {next_version}, {len(columns)} columns"
        )
        
        return schema
    
    async def delete_by_upload(self, upload_id: uuid.UUID) -> int:
        """Delete all schemas for an upload (used during re-ingest)."""
        stmt = select(StructuredFileSchema).where(
            StructuredFileSchema.upload_id == upload_id
        )
        result = await self.db_session.execute(stmt)
        schemas = result.scalars().all()
        
        for schema in schemas:
            await self.db_session.delete(schema)
        
        await self.db_session.flush()
        
        logger.info(f"Deleted {len(schemas)} schema versions for upload {upload_id}")
        return len(schemas)
