#!/usr/bin/env python3
"""
PHASE 0 FIX: Reindex all uploaded documents to fix document_name payload bug.

This script re-runs ingestion for every existing Upload row in the database,
ensuring vectors are indexed with correct document_name (filename) instead of the broken
f"doc_{document_id}" UUID-based name that was baked in before the fix.

CRITICAL: Run this after deploying the PHASE 0 fixes to ingestion_service.py
and hybrid.py to rebuild vector payloads with correct document names.

Usage:
  python scripts/reindex_all_uploads.py [--kb-id <id>] [--limit N] [--dry-run]

Options:
  --kb-id <id>   Reindex only a specific knowledge base (UUID)
  --limit N      Reindex only the first N uploads (default: 0 = all)
  --dry-run      Print what would be reindexed without actually reindexing
"""

import asyncio
import sys
import argparse
import time
from pathlib import Path
from typing import Optional
import uuid

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.db.base import Base
from app.db.models import Upload
from app.services.ingestion_service import IngestionService
from app.vectorstore.qdrant_store import QdrantVectorStore
from app.keyword_search.index import ElasticsearchIndexer
from app.utils.logger import logger
from sqlalchemy import select, and_


async def get_db_session() -> AsyncSession:
    """Create async database session."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        return session


async def reindex_upload(
    upload: Upload,
    ingestion_service: IngestionService,
    vector_store: QdrantVectorStore,
    elastic_indexer: ElasticsearchIndexer,
    dry_run: bool = False,
) -> bool:
    """Reindex a single upload, deleting old vectors and re-ingesting."""
    try:
        if not upload.storage_path or not Path(upload.storage_path).exists():
            logger.warning(
                f"❌ Upload {upload.id} ('{upload.original_filename}'): "
                f"storage_path doesn't exist or is null — skipping"
            )
            return False

        logger.info(
            f"⏳ Reindexing upload {upload.id}: "
            f"'{upload.original_filename}' (KB: {upload.knowledge_base_id})"
        )

        if dry_run:
            logger.info(f"   [DRY-RUN] Would delete vectors for upload {upload.id}")
            logger.info(f"   [DRY-RUN] Would re-ingest from {upload.storage_path}")
            return True

        # Step 1: Delete old vectors from Qdrant and Elasticsearch for this upload
        logger.info(f"   Deleting old vectors for upload {upload.id}...")

        # Delete from Qdrant
        try:
            client = vector_store.client
            if client:
                collection_name = vector_store._get_collection_name(upload.knowledge_base_id)
                # Use Qdrant's delete API to remove points with matching upload_id
                from qdrant_client.models import PointIdsList, Filter, FieldCondition, MatchValue
                
                points_to_delete = client.scroll(
                    collection_name=collection_name,
                    limit=10000,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key="upload_id",
                                match=MatchValue(value=str(upload.id))
                            )
                        ]
                    ),
                )[0]
                
                if points_to_delete:
                    point_ids = [p.id for p in points_to_delete]
                    client.delete(collection_name=collection_name, points_selector=PointIdsList(points=point_ids))
                    logger.info(f"   Deleted {len(point_ids)} Qdrant vectors")
        except Exception as e:
            logger.warning(f"   Qdrant deletion warning: {e}")

        # Delete from Elasticsearch
        try:
            await elastic_indexer.delete_documents_by_upload(upload.id)
        except Exception as e:
            logger.warning(f"   Elasticsearch deletion warning: {e}")

        # Step 2: Re-ingest the file
        logger.info(f"   Re-ingesting from {upload.storage_path}...")
        result = await ingestion_service.ingest_document(
            file_path=upload.storage_path,
            organization_id=upload.organization_id,
            owner_id=upload.user_id,
            title=upload.display_name or upload.original_filename,
            tags=upload.tags,
            upload_id=upload.id,
            knowledge_base_id=upload.knowledge_base_id,
        )

        logger.success(
            f"✓ Reindexed {upload.original_filename}: "
            f"{result.get('chunks', 0)} chunks, {result.get('pages', 1)} pages"
        )
        return True

    except Exception as e:
        logger.error(
            f"❌ Failed to reindex upload {upload.id} ('{upload.original_filename}'): {e}"
        )
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main reindex workflow."""
    parser = argparse.ArgumentParser(description="Reindex all uploads with corrected document_name payload")
    parser.add_argument("--kb-id", type=str, help="Reindex only a specific KB (UUID)")
    parser.add_argument("--limit", type=int, default=0, help="Reindex only first N uploads (0=all)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be reindexed")

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("🚀 PHASE 0 FIX: Reindex All Uploads (Fix document_name payload bug)")
    logger.info("=" * 80)

    # Get database session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as db_session:
        # Query uploads to reindex
        query_stmt = select(Upload)

        if args.kb_id:
            try:
                kb_uuid = uuid.UUID(args.kb_id)
                query_stmt = query_stmt.where(Upload.knowledge_base_id == kb_uuid)
                logger.info(f"Filtering to KB: {kb_uuid}")
            except ValueError:
                logger.error(f"Invalid KB UUID: {args.kb_id}")
                return 1

        result = await db_session.execute(query_stmt)
        uploads = result.scalars().all()

        if args.limit > 0:
            uploads = uploads[: args.limit]

        if not uploads:
            logger.warning("No uploads found to reindex")
            return 0

        logger.info(f"Found {len(uploads)} uploads to reindex")

        if args.dry_run:
            logger.info("DRY-RUN MODE: No actual reindexing will occur")

        # Initialize services
        ingestion_service = IngestionService(db_session=db_session)
        vector_store = QdrantVectorStore()
        elastic_indexer = ElasticsearchIndexer()

        # Reindex each upload
        start_time = time.perf_counter()
        successful = 0
        failed = 0

        for idx, upload in enumerate(uploads, start=1):
            logger.info(f"\n[{idx}/{len(uploads)}] Processing upload...")
            success = await reindex_upload(
                upload,
                ingestion_service,
                vector_store,
                elastic_indexer,
                dry_run=args.dry_run,
            )
            if success:
                successful += 1
            else:
                failed += 1

            # Small delay between reindexes to avoid overwhelming services
            if idx < len(uploads):
                await asyncio.sleep(0.5)

        elapsed = time.perf_counter() - start_time

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 REINDEX SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total uploads processed: {len(uploads)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total time: {elapsed:.2f}s")

        if args.dry_run:
            logger.info("\n(This was a DRY-RUN — no actual changes were made)")

        await engine.dispose()

        return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
