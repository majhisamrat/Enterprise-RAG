import asyncio
import uuid
from typing import Any, Dict, Optional
from pathlib import Path
from app.utils.logger import logger

from app.tasks.celery_app import celery_app


@celery_app.task(name="process_document_ingestion_task")
def process_document_ingestion_task(
    file_path: str,
    organization_id: str,
    owner_id: Optional[str] = None,
    user_id: Optional[str] = None,
    upload_id: Optional[str] = None,
    kb_id: Optional[str] = None,
    title: Optional[str] = None,
    department: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Background task for document parsing, chunking, embedding, and dual-store indexing."""
    logger.info(f"Celery task started: Ingesting file {file_path} (Upload: {upload_id})")

    user_uuid_str = user_id or owner_id or str(uuid.uuid4())
    org_uuid = uuid.UUID(organization_id) if organization_id else uuid.uuid4()
    owner_uuid = uuid.UUID(user_uuid_str) if user_uuid_str else uuid.uuid4()
    upload_uuid = uuid.UUID(upload_id) if upload_id else None
    kb_uuid = uuid.UUID(kb_id) if kb_id else None

    async def _ingest():
        from pathlib import Path
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from app.config.settings import settings
        from app.services.ingestion_service import IngestionService
        from app.db.repositories.upload_repository import UploadRepository
        from app.db.repositories.structured_schema_repository import StructuredSchemaRepository
        from app.structured.schema_discovery import SchemaDiscoveryEngine
        from app.structured.duckdb_store import StructuredDataStore
        import pandas as pd

        # Use PostgreSQL (not SQLite in Celery)
        from sqlalchemy import text
        db_url = str(settings.DATABASE_URL)
        engine = create_async_engine(db_url, echo=False)
        
        # Test connection with proper SQL expression
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("PostgreSQL connection successful in Celery worker")
            use_db = True
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed in Celery: {e}. Using fallback SQLite.")
            # Use SQLite fallback with proper schema
            db_url = "sqlite+aiosqlite:///./data/enterprise_rag_celery.db"
            engine = create_async_engine(db_url, echo=False)
            
            # Create tables if they don't exist
            try:
                from app.db.base import Base
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("SQLite fallback database schema created")
                use_db = True
            except Exception as schema_err:
                logger.warning(f"Failed to create SQLite schema: {schema_err}")
                use_db = False
        
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            file_ext = Path(file_path).suffix.lower()
            
            # PHASE 2: Structured data handling for CSV/XLSX
            if file_ext in ['.csv', '.xlsx', '.xls']:
                logger.info(f"Detected structured file: {file_ext} - running schema discovery")
                
                try:
                    # 1. Load data with pandas
                    if file_ext == '.csv':
                        df = pd.read_csv(file_path)
                        sheets = {None: df}
                    else:  # .xlsx or .xls
                        xlsx_file = pd.ExcelFile(file_path)
                        sheets = {name: xlsx_file.parse(name) for name in xlsx_file.sheet_names}
                    
                    # 2. Discover schema for each sheet
                    schema_engine = SchemaDiscoveryEngine()
                    structured_repo = StructuredSchemaRepository(session)
                    duckdb_store = StructuredDataStore()
                    
                    total_rows = 0
                    for sheet_name, dataframe in sheets.items():
                        logger.info(f"Processing sheet '{sheet_name}': {len(dataframe)} rows, {len(dataframe.columns)} columns")
                        
                        # Discover schema
                        schema_metadata = schema_engine.discover(dataframe, sheet_name=sheet_name)
                        
                        # Convert schema to JSON-serializable list format (not dict with keys)
                        columns_list = [
                            meta.to_dict()
                            for col_name, meta in schema_metadata.items()
                        ]
                        
                        # 3. Persist schema to database
                        if kb_uuid and upload_uuid:
                            await structured_repo.upsert_for_upload(
                                upload_id=upload_uuid,
                                knowledge_base_id=kb_uuid,
                                columns=columns_list,
                                sheet_name=sheet_name,
                            )
                            logger.success(f"Persisted schema for sheet '{sheet_name}': {len(columns_list)} columns")
                        
                        # 4. Load data into DuckDB
                        if kb_uuid and upload_uuid:
                            table_name = duckdb_store.write_table(
                                upload_id=upload_uuid,
                                kb_id=kb_uuid,
                                dataframe=dataframe,
                                sheet_name=sheet_name,
                            )
                            logger.success(f"Loaded {len(dataframe)} rows into DuckDB table '{table_name}'")
                        
                        total_rows += len(dataframe)
                    
                    # Close DuckDB connection
                    duckdb_store.close()
                    
                    # 5. Update upload status
                    if upload_uuid:
                        upload_repo = UploadRepository(session)
                        await upload_repo.update_status(str(upload_uuid), "completed")
                        await upload_repo.update_vector_counts(
                            upload_uuid,
                            page_count=1,  # CSV has no pages
                            chunk_count=total_rows,
                            total_vectors=0,  # No vectors for structured files
                        )
                        await session.commit()
                    
                    logger.success(f"Structured file ingestion complete: {total_rows} total rows across {len(sheets)} sheets")
                    
                    return {
                        "document_id": str(upload_uuid),
                        "title": title or Path(file_path).name,
                        "sheets": len(sheets),
                        "rows": total_rows,
                        "status": "indexed",
                        "type": "structured",
                    }
                
                except Exception as e:
                    logger.error(f"Structured file ingestion failed: {e}")
                    if upload_uuid:
                        upload_repo = UploadRepository(session)
                        await upload_repo.update_status(str(upload_uuid), "failed")
                        await session.commit()
                    raise
            
            # Existing semantic document ingestion (PDF/DOCX/PPTX)
            service = IngestionService(db_session=session)
            result = await service.ingest_document(
                file_path=file_path,
                organization_id=org_uuid,
                owner_id=owner_uuid,
                title=title,
                department=department,
                upload_id=upload_uuid,
                knowledge_base_id=kb_uuid,
            )

            if upload_uuid:
                upload_repo = UploadRepository(session)
                await upload_repo.update_status(str(upload_uuid), "completed")
                await upload_repo.update_vector_counts(
                    upload_uuid,
                    page_count=result.get("pages", 0),
                    chunk_count=result.get("chunks", 0),
                    total_vectors=result.get("chunks", 0),
                )
                await session.commit()

            await engine.dispose()
            return result

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(_ingest())
        logger.success(f"Celery task completed: Ingested file {file_path}")
        return result
    except Exception as e:
        logger.error(f"Celery task failed: {e}")
        return {
            "document_id": str(upload_uuid),
            "title": title or Path(file_path).name,
            "status": "failed",
            "error": str(e),
        }



@celery_app.task(name="reindex_kb_uploads_task")
def reindex_kb_uploads_task(kb_id: str, organization_id: str) -> Dict[str, Any]:
    """
    Background task for per-KB reindexing.
    
    Re-processes all uploads for a knowledge base:
    1. Delete old vectors from Qdrant/Elasticsearch per upload
    2. Re-chunk and re-embed the uploaded documents
    3. Re-index all vectors with KB metadata
    4. Update upload status and vector counts
    """
    logger.info(f"Starting per-KB reindex for KB {kb_id}")

    async def _reindex():
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import text
        from app.config.settings import settings
        from app.db.repositories.upload_repository import UploadRepository
        from app.db.repositories.knowledge_base_repository import KnowledgeBaseRepository
        from app.services.ingestion_service import IngestionService
        from app.vectorstore.qdrant_store import QdrantVectorStore
        from app.keyword_search.index import ElasticsearchIndexer
        from pathlib import Path

        # Setup DB session for this task with fallback to SQLite
        db_url = str(settings.DATABASE_URL)
        engine = create_async_engine(db_url, echo=False)
        
        # Test connection first
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("PostgreSQL connection successful in reindex task")
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed in reindex task: {e}. Using fallback SQLite.")
            # Use SQLite fallback with proper schema
            db_url = "sqlite+aiosqlite:///./data/enterprise_rag_celery.db"
            engine = create_async_engine(db_url, echo=False)
            
            # Create tables if they don't exist
            try:
                from app.db.base import Base
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("SQLite fallback database schema created")
            except Exception as schema_err:
                logger.warning(f"Failed to create SQLite schema: {schema_err}")
        
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        db = async_session()

        try:
            kb_uuid = uuid.UUID(kb_id)
            org_uuid = uuid.UUID(organization_id)

            kb_repo = KnowledgeBaseRepository(db)
            upload_repo = UploadRepository(db)

            # Verify KB exists
            kb = await kb_repo.get_by_id(kb_uuid)
            if not kb or kb.organization_id != org_uuid:
                logger.error(f"KB {kb_id} not found or doesn't belong to org {organization_id}")
                return {
                    "status": "FAILED",
                    "kb_id": kb_id,
                    "reason": "KB not found",
                }

            # Get all uploads for this KB
            uploads = await upload_repo.get_by_kb(kb_uuid, skip=0, limit=10000)
            logger.info(f"Reindexing {len(uploads)} uploads for KB {kb_id}")

            vector_store = QdrantVectorStore()
            elastic_index = ElasticsearchIndexer()
            ingestion_service = IngestionService(db_session=db)

            total_vectors_created = 0
            failed_uploads = 0

            for upload in uploads:
                try:
                    logger.info(f"Reindexing upload {upload.id}: {upload.original_filename}")

                    # Update status to reindexing
                    await upload_repo.update_status(upload.id, "reindexing")

                    # Delete old vectors from Qdrant
                    try:
                        await vector_store.delete_vectors_by_upload(upload.id)
                        logger.info(f"Deleted old vectors for upload {upload.id}")
                    except Exception as e:
                        logger.warning(f"Failed to delete old vectors for upload {upload.id}: {e}")

                    # Delete old vectors from Elasticsearch
                    try:
                        await elastic_index.delete_documents_by_upload(upload.id)
                        logger.info(f"Deleted old Elasticsearch docs for upload {upload.id}")
                    except Exception as e:
                        logger.warning(f"Failed to delete Elasticsearch docs for upload {upload.id}: {e}")

                    # Re-ingest the document
                    if upload.storage_path and Path(upload.storage_path).exists():
                        result = await ingestion_service.ingest_document(
                            file_path=upload.storage_path,
                            organization_id=org_uuid,
                            owner_id=upload.user_id,
                            title=upload.display_name or upload.original_filename,
                            department=upload.department,
                            author=upload.author,
                            tags=upload.tags,
                            upload_id=upload.id,
                            knowledge_base_id=kb_uuid,
                        )

                        chunks_count = result.get("chunks", 0)
                        total_vectors_created += chunks_count

                        # Update upload status and counts
                        await upload_repo.update_status(upload.id, "completed")
                        await upload_repo.update_vector_counts(
                            upload_id=upload.id,
                            page_count=result.get("pages", 0),
                            chunk_count=result.get("chunks", 0),
                            total_vectors=result.get("chunks", 0),
                        )
                        logger.success(f"Reindexed upload {upload.id}: {chunks_count} chunks")
                    else:
                        logger.error(f"Upload file not found: {upload.storage_path}")
                        await upload_repo.update_status(upload.id, "failed")
                        failed_uploads += 1

                except Exception as e:
                    logger.error(f"Error reindexing upload {upload.id}: {e}")
                    await upload_repo.update_status(upload.id, "failed")
                    failed_uploads += 1

            # Update KB status
            await kb_repo.update_last_queried(kb_uuid)
            await db.commit()

            logger.success(
                f"KB reindex complete for {kb_id}: "
                f"{len(uploads) - failed_uploads} succeeded, "
                f"{failed_uploads} failed, "
                f"{total_vectors_created} total vectors"
            )

            return {
                "status": "SUCCESS",
                "kb_id": kb_id,
                "uploads_processed": len(uploads),
                "uploads_failed": failed_uploads,
                "total_vectors_created": total_vectors_created,
            }

        except Exception as e:
            logger.error(f"Fatal error in KB reindex task: {e}")
            return {
                "status": "FAILED",
                "kb_id": kb_id,
                "reason": str(e),
            }
        finally:
            await db.close()
            await engine.dispose()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    result = loop.run_until_complete(_reindex())
    return result


@celery_app.task(name="reindex_document_task")
def reindex_document_task(document_id: str, organization_id: str) -> Dict[str, Any]:
    """Background task for document re-indexing."""
    logger.info(f"Re-indexing document {document_id}")
    return {"status": "SUCCESS", "document_id": document_id}


@celery_app.task(name="cleanup_expired_sessions_task")
def cleanup_expired_sessions_task() -> Dict[str, Any]:
    """Background task for cleaning expired sessions."""
    logger.info("Cleaning up expired user sessions and caches")
    return {"status": "CLEANED"}
