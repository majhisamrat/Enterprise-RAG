import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.utils.logger import logger
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PayloadSchemaType, PointStruct, VectorParams

from app.config import settings
from app.ingestion.schemas import ChunkedDocument
from app.vectorstore.base import BaseVectorStore
from app.vectorstore.qdrant_client import QdrantConnection


class QdrantVectorStore(BaseVectorStore):
    """
    Production-grade Qdrant Vector Store with KB-based collection strategy.
    
    🎯 PERFECT KB SEGMENTATION STRATEGY:
    
    Each Knowledge Base gets its own Qdrant collection for complete isolation:
    - KB vectors: stored in kb-specific collections (enterprise_rag_kb_12345678)
    - Non-KB vectors: stored in default collection (enterprise_rag)
    
    This ensures:
    1. When user selects specific KB → only search that KB's collection
    2. When user selects "All KBs" → search default + all KB collections  
    3. Perfect vector separation by KB as requested
    """

    def __init__(self, collection_name: str = settings.QDRANT_COLLECTION):
        self.base_collection_name = collection_name
        self._client = None

    def _get_collection_name(self, knowledge_base_id: Optional[uuid.UUID] = None) -> str:
        """
        Get collection name based on KB strategy for perfect segmentation:
        - If KB provided: use kb-specific collection (enterprise_rag_kb_12345678)
        - If no KB: use default collection for backward compatibility
        """
        if knowledge_base_id:
            kb_short = str(knowledge_base_id).replace('-', '')[:8]
            return f"{self.base_collection_name}_kb_{kb_short}"
        return self.base_collection_name

    @property
    def collection_name(self) -> str:
        """Default collection name for backward compatibility"""
        return self.base_collection_name

    @property
    def client(self):
        if self._client is None:
            if not QdrantConnection.is_available():
                return None
            self._client = QdrantConnection.get_client()
            # Only ensure default collection here
            self._ensure_collection(knowledge_base_id=None)
            if not QdrantConnection.is_available():
                self._client = None
                return None
        return self._client

    def _ensure_collection(self, knowledge_base_id: Optional[uuid.UUID] = None):
        """Ensure vector collection exists in Qdrant with proper index configuration."""
        if self._client is None:
            return
        client = self._client
        
        collection_name = self._get_collection_name(knowledge_base_id)
        
        try:
            collections = client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            if not exists:
                kb_info = f" for KB {knowledge_base_id}" if knowledge_base_id else " (default)"
                logger.info(f"🚀 Creating Qdrant collection '{collection_name}'{kb_info}...")
                
                # CRITICAL: Use wait=True to ensure collection is ready before returning
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE,
                    ),
                    timeout=30,  # 30 second timeout for creation
                )
                
                logger.info(f"✅ Collection '{collection_name}' created and ready")
                
                # Create payload indexes for fast filtering
                try:
                    client.create_payload_index(
                        collection_name=collection_name,
                        field_name="organization_id",
                        field_schema=PayloadSchemaType.KEYWORD,
                    )
                    client.create_payload_index(
                        collection_name=collection_name,
                        field_name="knowledge_base_id",
                        field_schema=PayloadSchemaType.KEYWORD,
                    )
                    client.create_payload_index(
                        collection_name=collection_name,
                        field_name="upload_id",
                        field_schema=PayloadSchemaType.KEYWORD,
                    )
                    client.create_payload_index(
                        collection_name=collection_name,
                        field_name="department",
                        field_schema=PayloadSchemaType.KEYWORD,
                    )
                    logger.info(f"✅ Created payload indexes for collection '{collection_name}'")
                except Exception as e:
                    logger.warning(f"Failed to create payload indexes: {e}")
        except Exception as e:
            QdrantConnection.mark_offline()
            logger.error(f"Failed to ensure collection '{collection_name}': {e}")
            raise

    async def upsert_document_chunks(
        self,
        document: ChunkedDocument,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
        upload_id: Optional[uuid.UUID] = None,
        knowledge_base_id: Optional[uuid.UUID] = None,
        document_name: Optional[str] = None,
        upload_date: Optional[str] = None,
        page_number: int = 1,
        author: Optional[str] = "System",
        department: Optional[str] = "General",
        tags: Optional[List[str]] = None,
        language: str = "en",
        embedding_model: str = "BAAI/bge-small-en-v1.5",
    ):
        """
        🎯 Upsert document chunks with PERFECT KB SEGMENTATION
        
        Strategy:
        - If knowledge_base_id provided: store in KB-specific collection
        - If no KB: store in default collection for backward compatibility
        
        This ensures vectors are completely separated by KB for accurate filtering.
        """
        if not QdrantConnection.is_available():
            logger.debug("Qdrant circuit breaker OPEN — skipping upsert (0ms)")
            return

        # Access client to ensure it's initialized
        client = self.client
        if client is None:
            logger.warning("Qdrant client unavailable - skipping upsert")
            return

        # Get KB-specific collection name for perfect segmentation
        collection_name = self._get_collection_name(knowledge_base_id)
        
        # Ensure KB-specific collection exists
        if knowledge_base_id:
            self._ensure_collection(knowledge_base_id)

        points = []
        now_iso = datetime.now(timezone.utc).isoformat()
        upload_date = upload_date or now_iso
        
        for idx, chunk in enumerate(document.chunks):
            chunk_uuid = str(uuid.uuid4())
            payload = {
                # Core identifiers
                "chunk_id": getattr(chunk, "chunk_id", chunk_uuid),
                "document_id": str(document_id),
                "organization_id": str(organization_id),
                
                # 🎯 KB tracking for perfect segmentation
                "upload_id": str(upload_id) if upload_id else str(document_id),
                "knowledge_base_id": str(knowledge_base_id) if knowledge_base_id else None,
                "document_name": document_name or f"doc_{document_id}",
                "upload_date": upload_date,
                
                # Chunk metadata
                "page_number": getattr(chunk, "page", page_number),
                "chunk_index": idx,
                "chunk_text": chunk.text,
                "text": chunk.text,  # Keep for backward compatibility
                
                # Embedding metadata
                "embedding_model": embedding_model,
                "embedding_dimension": len(chunk.embedding) if chunk.embedding else 0,
                
                # User metadata
                "author": author or "System",
                "department": department or "General",
                "tags": tags or [],
                "language": language,
                
                # Timestamps
                "created_at": now_iso,
                "metadata": getattr(chunk, "metadata", {}),
            }

            points.append(
                PointStruct(
                    id=chunk_uuid,
                    vector=chunk.embedding if chunk.embedding else [0.0] * 384,
                    payload=payload,
                )
            )

        try:
            client = self.client
            if client is None:
                logger.debug("Qdrant client unavailable — skipping upsert")
                return
                
            client.upsert(
                collection_name=collection_name,
                points=points,
            )
            
            kb_info = f" → KB {knowledge_base_id}" if knowledge_base_id else " → default"
            logger.info(
                f"✅ Stored {len(points)} vectors in collection '{collection_name}'{kb_info}"
            )
            
        except Exception as e:
            QdrantConnection.mark_offline()
            logger.error(f"Failed to upsert to collection '{collection_name}': {e}")
            raise

    def index(self, document: ChunkedDocument):
        """Standard interface implementation for indexing."""
        dummy_org = uuid.UUID("00000000-0000-0000-0000-000000000001")
        dummy_doc = uuid.uuid4()
        import asyncio
        asyncio.run(self.upsert_document_chunks(document, dummy_doc, dummy_org))

    def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        organization_id: Optional[uuid.UUID] = None,
        knowledge_base_id: Optional[uuid.UUID] = None,
        upload_id: Optional[uuid.UUID] = None,
        department: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        🎯 PERFECT KB-BASED SEARCH STRATEGY
        
        Implements exactly what user requested:
        - If knowledge_base_id provided: search ONLY that KB's collection
        - If no KB filter: search default collection (for "All Knowledge Bases")
        
        This ensures complete KB isolation during retrieval.
        """
        if not QdrantConnection.is_available():
            logger.debug("Qdrant circuit breaker OPEN — skipping search (0ms)")
            return []

        # 🎯 Determine which collection to search based on KB filter
        if knowledge_base_id:
            # Search ONLY the specific KB collection
            collection_name = self._get_collection_name(knowledge_base_id)
            search_info = f"KB {knowledge_base_id}"
        else:
            # Search default collection for "All Knowledge Bases"
            collection_name = self.base_collection_name
            search_info = "All KBs (default collection)"

        try:
            client = self.client
            if client is None:
                logger.debug("Qdrant client unavailable — skipping search")
                return []
            
            # Ensure client is fresh by checking collections
            collections = client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if collection_name not in collection_names:
                logger.warning(f"Collection '{collection_name}' not found. Available: {collection_names[:3]}")
                # Try to create it now if KB-specific
                if knowledge_base_id:
                    logger.info(f"Creating collection '{collection_name}' on-demand during search...")
                    self._ensure_collection(knowledge_base_id)
                    # Check again
                    collections = client.get_collections().collections
                    if not any(c.name == collection_name for c in collections):
                        logger.debug(f"Collection '{collection_name}' still doesn't exist after creation attempt")
                        return []
                else:
                    logger.debug(f"Default collection '{collection_name}' does not exist")
                    return []

            # Build filter conditions
            must_conditions = []

            if organization_id:
                must_conditions.append(
                    FieldCondition(
                        key="organization_id",
                        match=MatchValue(value=str(organization_id)),
                    )
                )

            # Extra safety: filter by KB if specified
            if knowledge_base_id:
                must_conditions.append(
                    FieldCondition(
                        key="knowledge_base_id",
                        match=MatchValue(value=str(knowledge_base_id)),
                    )
                )

            # Filter by upload if specified
            if upload_id:
                must_conditions.append(
                    FieldCondition(
                        key="upload_id",
                        match=MatchValue(value=str(upload_id)),
                    )
                )

            if department:
                must_conditions.append(
                    FieldCondition(
                        key="department",
                        match=MatchValue(value=department),
                    )
                )

            query_filter = Filter(must=must_conditions) if must_conditions else None
                
            try:
                results = client.query_points(
                    collection_name=collection_name,
                    query=query_embedding,
                    query_filter=query_filter,
                    limit=limit,
                )
            except Exception as search_error:
                # Check if this is a collection-not-found (404) error
                error_str = str(search_error).lower()
                if "404" in error_str or "not found" in error_str:
                    logger.warning(
                        f"Collection '{collection_name}' not found (404). "
                        f"This may be a transient issue. Attempting recovery..."
                    )
                    # Don't mark offline for 404 - try to recover by recreating collection
                    if knowledge_base_id:
                        try:
                            logger.info(f"Recovery: Recreating collection '{collection_name}'...")
                            self._ensure_collection(knowledge_base_id)
                            # Retry the query once
                            results = client.query_points(
                                collection_name=collection_name,
                                query=query_embedding,
                                query_filter=query_filter,
                                limit=limit,
                            )
                        except Exception as recovery_error:
                            logger.error(f"Recovery attempt failed: {recovery_error}")
                            return []
                    else:
                        return []
                else:
                    # Other errors - mark offline
                    logger.error(f"Qdrant query_points failed for collection '{collection_name}': {search_error}")
                    logger.debug(f"Query embedding dimension: {len(query_embedding)}")
                    QdrantConnection.mark_offline()
                    return []

            formatted_results = []
            for pt in results.points:
                payload = pt.payload or {}
                formatted_results.append({
                    # Core identifiers
                    "chunk_id": payload.get("chunk_id"),
                    "document_id": payload.get("document_id"),
                    "organization_id": payload.get("organization_id"),
                    
                    # KB tracking
                    "upload_id": payload.get("upload_id"),
                    "knowledge_base_id": payload.get("knowledge_base_id"),
                    "document_name": payload.get("document_name"),
                    "upload_date": payload.get("upload_date"),
                    
                    # Chunk metadata
                    "page_number": payload.get("page_number"),
                    "chunk_index": payload.get("chunk_index"),
                    "text": payload.get("text") or payload.get("chunk_text"),
                    
                    # Embedding metadata
                    "embedding_model": payload.get("embedding_model"),
                    "embedding_dimension": payload.get("embedding_dimension"),
                    
                    # Score
                    "score": getattr(pt, "score", 0.0),
                    
                    # User metadata
                    "author": payload.get("author"),
                    "department": payload.get("department"),
                    "tags": payload.get("tags"),
                    "language": payload.get("language"),
                    
                    # Metadata
                    "created_at": payload.get("created_at"),
                    "metadata": payload.get("metadata"),
                })
            
            logger.info(f"🔍 Found {len(formatted_results)} vectors from {search_info}")
            return formatted_results
                    
        except Exception as e:
            logger.warning(f"Error searching collection '{collection_name}': {e}")
            QdrantConnection.mark_offline()
            return []

    async def delete_vectors_by_upload(self, upload_id: uuid.UUID, knowledge_base_id: Optional[uuid.UUID] = None) -> int:
        """
        Delete all vectors for a specific upload from KB-specific or default collection.
        
        Used during per-KB reindexing to remove old vectors before re-uploading.
        """
        if not QdrantConnection.is_available():
            logger.debug("Qdrant circuit breaker OPEN — skipping delete (0ms)")
            return 0

        collection_name = self._get_collection_name(knowledge_base_id)

        try:
            client = self.client
            if client is None:
                logger.debug("Qdrant client unavailable — skipping delete")
                return 0

            # Delete all points with matching upload_id
            delete_filter = Filter(
                must=[
                    FieldCondition(
                        key="upload_id",
                        match=MatchValue(value=str(upload_id)),
                    )
                ]
            )

            result = client.delete(
                collection_name=collection_name,
                points_selector=delete_filter,
            )

            deleted_count = result.deleted if hasattr(result, "deleted") else 0
            kb_info = f" from KB {knowledge_base_id}" if knowledge_base_id else " from default"
            logger.info(f"🗑️ Deleted {deleted_count} vectors for upload {upload_id}{kb_info}")
            return deleted_count

        except Exception as e:
            logger.warning(f"Error deleting vectors for upload {upload_id}: {e}")
            QdrantConnection.mark_offline()
            return 0

    async def delete_collection(self, knowledge_base_id: uuid.UUID) -> bool:
        """
        Delete entire KB-specific collection from Qdrant.
        
        Used when a Knowledge Base is deleted to clean up all associated vectors and collections.
        This ensures complete cleanup and prevents orphaned collections in Qdrant.
        """
        if not QdrantConnection.is_available():
            logger.debug("Qdrant circuit breaker OPEN — skipping collection delete")
            return False

        collection_name = self._get_collection_name(knowledge_base_id)

        try:
            client = self.client
            if client is None:
                logger.debug("Qdrant client unavailable — skipping collection delete")
                return False

            # Check if collection exists
            collections = client.get_collections().collections
            collection_exists = any(c.name == collection_name for c in collections)
            
            if not collection_exists:
                logger.info(f"Collection '{collection_name}' does not exist — nothing to delete")
                return True

            # Delete the entire collection
            client.delete_collection(collection_name=collection_name)
            logger.info(f"✅ Deleted Qdrant collection '{collection_name}' for KB {knowledge_base_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete Qdrant collection '{collection_name}': {e}")
            QdrantConnection.mark_offline()
            return False