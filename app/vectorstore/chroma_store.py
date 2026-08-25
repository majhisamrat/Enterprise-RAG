import uuid
import os
import pickle
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.utils.logger import logger
from app.config import settings
from app.ingestion.schemas import ChunkedDocument
from app.vectorstore.base import BaseVectorStore

try:
    import chromadb
except ImportError:
    chromadb = None


class ChromaVectorStore(BaseVectorStore):
    """
    Lightweight Chroma Vector Store replacing Qdrant.
    
    Uses persistent file-based storage to share vectors across processes
    (FastAPI server, Celery workers, etc.)
    
    🎯 PERSISTENT STORAGE:
    - Stores vectors to disk at .chroma/vectors.pkl
    - Auto-loads on each instance creation
    - Shared across all processes
    """

    # Persistent storage path - use absolute path for cross-process compatibility
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    CHROMA_DIR = os.path.join(PROJECT_ROOT, ".chroma")
    VECTORS_FILE = os.path.join(CHROMA_DIR, "vectors.pkl")

    # Class-level cache (loaded from disk)
    _shared_in_memory_store: Dict[str, Any] = {}
    _shared_collections: Dict[str, Any] = {}

    def __init__(self, collection_name: str = settings.QDRANT_COLLECTION):
        self.base_collection_name = collection_name
        self._client = None
        
        # Always point to the class-level shared store
        self._in_memory_store = ChromaVectorStore._shared_in_memory_store
        self._collections = {}

    @classmethod
    def _load_from_disk(cls):
        """Load vectors from persistent disk storage."""
        try:
            os.makedirs(cls.CHROMA_DIR, exist_ok=True)
            if os.path.exists(cls.VECTORS_FILE):
                with open(cls.VECTORS_FILE, "rb") as f:
                    loaded_data = pickle.load(f)
                    cls._shared_in_memory_store = loaded_data
                logger.info(f"✅ Loaded {len(cls._shared_in_memory_store)} collections from disk ({sum(len(c.get('ids', [])) for c in cls._shared_in_memory_store.values())} vectors)")
                logger.info(f"📋 Available collections: {list(cls._shared_in_memory_store.keys())}")
            else:
                logger.debug("📦 No persistent vectors found - starting with empty store")
                cls._shared_in_memory_store = {}
        except Exception as e:
            logger.warning(f"Failed to load vectors from disk: {e} - using empty store")
            cls._shared_in_memory_store = {}

    @classmethod
    def _save_to_disk(cls):
        """Save vectors to persistent disk storage."""
        try:
            os.makedirs(cls.CHROMA_DIR, exist_ok=True)
            with open(cls.VECTORS_FILE, "wb") as f:
                pickle.dump(cls._shared_in_memory_store, f)
                f.flush()  # Ensure data is written to disk
                os.fsync(f.fileno())  # Sync to disk
            
            # Log actual counts
            collection_count = len(cls._shared_in_memory_store)
            vector_count = sum(len(c.get('ids', [])) for c in cls._shared_in_memory_store.values())
            logger.info(f"💾 Saved {collection_count} collections ({vector_count} total vectors) to {cls.VECTORS_FILE}")
        except Exception as e:
            logger.error(f"Failed to save vectors to disk: {e}")

    def _initialize_client(self):
        """Initialize Chroma client with fallback to simple in-memory store."""
        if chromadb is None:
            logger.warning("chromadb not installed - using simple in-memory vector store")
            self._in_memory_store = {}  # Simple dict-based store: collection_name -> [docs]
            return

        try:
            # Use lazy HTTP client (only connect when actually needed)
            self._client = {
                "type": "lazy_http",
                "host": "localhost",
                "port": 8123,
            }
            logger.info("✅ Chroma HTTP client configured (lazy initialization)")
        except Exception as e:
            logger.warning(f"Failed to configure Chroma: {e}")
            self._in_memory_store = {}
            logger.info("✅ Using simple in-memory vector store")

    def _get_collection_name(self, knowledge_base_id: Optional[uuid.UUID] = None) -> str:
        """
        Get collection name based on KB strategy for perfect segmentation:
        - If KB provided: use kb-specific collection (enterprise_documents_kb_12345678)
        - If no KB: use default collection for backward compatibility
        """
        if knowledge_base_id:
            kb_str = str(knowledge_base_id)
            kb_short = kb_str.replace('-', '')[:8]
            collection = f"{self.base_collection_name}_kb_{kb_short}"
            logger.debug(f"Collection name: {collection} (KB: {kb_str})")
            return collection
        return self.base_collection_name

    @property
    def collection_name(self) -> str:
        """Default collection name for backward compatibility"""
        return self.base_collection_name

    @property
    def client(self):
        """Get Chroma client, reinitialize if needed."""
        if self._client is None:
            self._initialize_client()
        return self._client

    def _get_or_create_collection(self, knowledge_base_id: Optional[uuid.UUID] = None):
        """Get or create a Chroma collection."""
        collection_name = self._get_collection_name(knowledge_base_id)

        # Initialize client on first use
        if self._client is None and not hasattr(self, '_in_memory_store'):
            self._initialize_client()

        # If using in-memory store
        if self._in_memory_store is not None:
            # CRITICAL: Always get from _shared_in_memory_store directly to ensure we have latest from disk
            if collection_name not in ChromaVectorStore._shared_in_memory_store:
                ChromaVectorStore._shared_in_memory_store[collection_name] = {
                    "ids": [],
                    "embeddings": [],
                    "documents": [],
                    "metadatas": []
                }
                logger.info(f"📦 Created in-memory collection '{collection_name}'")
            
            kb_info = f" for KB {knowledge_base_id}" if knowledge_base_id else " (default)"
            collection_vectors = len(ChromaVectorStore._shared_in_memory_store[collection_name]['ids'])
            logger.debug(f"✅ In-memory collection '{collection_name}'{kb_info} ready ({collection_vectors} vectors)")
            
            # Return reference to shared store, not cached copy
            return ChromaVectorStore._shared_in_memory_store[collection_name]

        # If using Chroma client
        if self._client is None:
            logger.warning("Chroma client unavailable")
            return None

        try:
            # Get or create collection with metadata support
            collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},  # Use cosine similarity like Qdrant
            )
            self._collections[collection_name] = collection
            
            kb_info = f" for KB {knowledge_base_id}" if knowledge_base_id else " (default)"
            logger.info(f"✅ Collection '{collection_name}'{kb_info} ready")
            return collection
        except Exception as e:
            logger.error(f"Failed to get/create collection '{collection_name}': {e}")
            return None

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
        # LOG THE INPUT
        logger.info(f"🚀 UPSERT START: KB={knowledge_base_id}, Upload={upload_id}, Chunks={len(document.chunks)}")
        
        collection = self._get_or_create_collection(knowledge_base_id)
        if collection is None:
            logger.warning("Failed to get/create collection - skipping upsert")
            return

        collection_name = self._get_collection_name(knowledge_base_id)
        logger.info(f"📊 Collection Name: {collection_name}")
        logger.info(f"📊 Will store KB ID in metadata: {str(knowledge_base_id) if knowledge_base_id else 'NONE'}")

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        now_iso = datetime.now(timezone.utc).isoformat()
        upload_date = upload_date or now_iso

        for idx, chunk in enumerate(document.chunks):
            chunk_uuid = str(uuid.uuid4())
            
            ids.append(chunk_uuid)
            
            # Use embedding if available, else None (Chroma will handle)
            if chunk.embedding:
                embeddings.append(chunk.embedding)
            
            documents.append(chunk.text)
            
            metadata = {
                # Core identifiers
                "chunk_id": getattr(chunk, "chunk_id", chunk_uuid),
                "document_id": str(document_id),
                "organization_id": str(organization_id),
                
                # 🎯 KB tracking for perfect segmentation
                "upload_id": str(upload_id) if upload_id else str(document_id),
                "knowledge_base_id": str(knowledge_base_id) if knowledge_base_id else "",
                "document_name": document_name or f"doc_{document_id}",
                "upload_date": upload_date,
                
                # Chunk metadata
                "page_number": str(getattr(chunk, "page", page_number)),
                "chunk_index": str(idx),
                
                # Embedding metadata
                "embedding_model": embedding_model,
                "embedding_dimension": str(len(chunk.embedding) if chunk.embedding else 0),
                
                # User metadata
                "author": author or "System",
                "department": department or "General",
                "language": language,
                
                # Timestamps
                "created_at": now_iso,
            }
            
            # Store tags as comma-separated string (Chroma metadata limitation)
            if tags:
                metadata["tags"] = ",".join(tags)
            
            metadatas.append(metadata)

        try:
            collection_name = self._get_collection_name(knowledge_base_id)
            
            # If using in-memory store (dict-based)
            if isinstance(collection, dict) and "ids" in collection:
                logger.info(f"📝 Upserting to in-memory collection: {collection_name}")
                logger.info(f"   Before: {len(collection['ids'])} vectors, Adding: {len(ids)} vectors")
                
                # Remove old entries if they exist (upsert behavior)
                for id_ in ids:
                    if id_ in collection["ids"]:
                        idx = collection["ids"].index(id_)
                        collection["ids"].pop(idx)
                        if idx < len(collection["embeddings"]):
                            collection["embeddings"].pop(idx)
                        if idx < len(collection["documents"]):
                            collection["documents"].pop(idx)
                        if idx < len(collection["metadatas"]):
                            collection["metadatas"].pop(idx)
                
                # Add new entries
                collection["ids"].extend(ids)
                collection["embeddings"].extend(embeddings)
                collection["documents"].extend(documents)
                collection["metadatas"].extend(metadatas)
                
                logger.info(f"   After: {len(collection['ids'])} vectors total")
                logger.info(f"   Shared store size: {len(ChromaVectorStore._shared_in_memory_store)} collections")
            else:
                # Using Chroma HTTP/persistent client
                logger.info(f"📝 Upserting to Chroma HTTP/persistent client: {collection_name}")
                if embeddings:
                    collection.upsert(
                        ids=ids,
                        embeddings=embeddings,
                        documents=documents,
                        metadatas=metadatas,
                    )
                else:
                    # If no embeddings provided, let Chroma generate them
                    collection.upsert(
                        ids=ids,
                        documents=documents,
                        metadatas=metadatas,
                    )
            
            kb_info = f" → KB {knowledge_base_id}" if knowledge_base_id else " → default"
            logger.info(
                f"✅ Stored {len(ids)} vectors in collection '{collection_name}'{kb_info}"
            )
            logger.info(f"📊 Collection now contains {len(collection['ids'])} total vectors")
            
            # Save to disk for persistence across processes
            ChromaVectorStore._save_to_disk()
            
        except Exception as e:
            logger.error(f"Failed to upsert chunks: {e}")
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
        # Always reload from disk before search to get latest vectors
        self._load_from_disk()
        
        collection = self._get_or_create_collection(knowledge_base_id)
        if collection is None:
            logger.warning("Failed to get collection - returning empty results")
            return []

        collection_name = self._get_collection_name(knowledge_base_id)
        search_info = f"KB {knowledge_base_id}" if knowledge_base_id else "All KBs (default collection)"

        try:
            formatted_results = []
            
            logger.info(f"🔎 Searching for collection: '{collection_name}'")
            logger.info(f"🔎 Available collections: {list(ChromaVectorStore._shared_in_memory_store.keys())}")
            
            # Check if collection exists
            if collection_name not in ChromaVectorStore._shared_in_memory_store:
                logger.warning(f"❌ Collection '{collection_name}' NOT FOUND in store!")
                return []
            
            logger.info(f"✅ Collection '{collection_name}' found with {len(collection['ids'])} vectors")
            if isinstance(collection, dict) and "ids" in collection:
                # Log available collections in store
                logger.debug(f"Available collections in store: {list(ChromaVectorStore._shared_in_memory_store.keys())}")
                logger.debug(f"Looking for collection: {collection_name}")
                logger.debug(f"Searching in-memory collection with {len(collection['ids'])} vectors")
                
                if not collection['ids']:
                    logger.info(f"🔍 Collection '{collection_name}' is empty - found 0 vectors from {search_info}")
                    return []
                
                # Check what KB IDs are actually in this collection
                if collection['metadatas']:
                    kb_ids_in_collection = set()
                    for m in collection['metadatas']:
                        if m.get('knowledge_base_id'):
                            kb_ids_in_collection.add(m.get('knowledge_base_id'))
                    logger.info(f"📋 KB IDs in collection: {kb_ids_in_collection}")
                    logger.info(f"🔎 Looking for KB ID: '{str(knowledge_base_id)}'")
                    
                    # Check if we're looking for a KB ID that exists in this collection
                    if knowledge_base_id:
                        kb_str = str(knowledge_base_id)
                        if kb_str in kb_ids_in_collection:
                            logger.info(f"✅ MATCH! Found KB ID {kb_str}")
                        else:
                            logger.warning(f"❌ NO MATCH! KB ID {kb_str} not in {kb_ids_in_collection}")
                
                matched_count = 0
                for i, doc_id in enumerate(collection["ids"]):
                    metadata = collection["metadatas"][i] if i < len(collection["metadatas"]) else {}
                    
                    # Apply filters with detailed logging
                    if organization_id and metadata.get("organization_id") != str(organization_id):
                        if i == 0:
                            logger.info(f"❌ Org filter rejected - expected {organization_id}, got {metadata.get('organization_id')}")
                        continue
                    if knowledge_base_id and metadata.get("knowledge_base_id") != str(knowledge_base_id):
                        if i == 0:
                            logger.info(f"❌ KB filter rejected - expected {knowledge_base_id}, got {metadata.get('knowledge_base_id')}")
                        continue
                    if upload_id and metadata.get("upload_id") != str(upload_id):
                        if i == 0:
                            logger.info(f"❌ Upload filter rejected - expected {upload_id}, got {metadata.get('upload_id')}")
                        continue
                    # NOTE: Department filter removed - PDFs don't have department data, all stored as "General"
                    # if department and metadata.get("department") != department:
                    #     if i == 0:
                    #         logger.info(f"❌ Department filter rejected - expected {department}, got {metadata.get('department')}")
                    #     continue
                    
                    matched_count += 1
                    
                    # Calculate similarity (simple dot product for now)
                    embedding = collection["embeddings"][i] if i < len(collection["embeddings"]) else []
                    similarity = 0.0
                    if embedding and len(embedding) == len(query_embedding):
                        # Cosine similarity
                        dot_product = sum(a * b for a, b in zip(embedding, query_embedding))
                        mag_a = sum(a * a for a in embedding) ** 0.5
                        mag_b = sum(b * b for b in query_embedding) ** 0.5
                        if mag_a > 0 and mag_b > 0:
                            similarity = dot_product / (mag_a * mag_b)
                    
                    formatted_results.append({
                        "chunk_id": metadata.get("chunk_id", doc_id),
                        "document_id": metadata.get("document_id"),
                        "organization_id": metadata.get("organization_id"),
                        "upload_id": metadata.get("upload_id"),
                        "knowledge_base_id": metadata.get("knowledge_base_id"),
                        "document_name": metadata.get("document_name"),
                        "upload_date": metadata.get("upload_date"),
                        "page_number": int(metadata.get("page_number", 1)) if metadata.get("page_number") else 1,
                        "chunk_index": int(metadata.get("chunk_index", 0)) if metadata.get("chunk_index") else 0,
                        "text": collection["documents"][i] if i < len(collection["documents"]) else "",
                        "embedding_model": metadata.get("embedding_model"),
                        "embedding_dimension": metadata.get("embedding_dimension"),
                        "score": similarity,
                        "author": metadata.get("author"),
                        "department": metadata.get("department"),
                        "tags": metadata.get("tags", "").split(",") if metadata.get("tags") else [],
                        "language": metadata.get("language"),
                        "created_at": metadata.get("created_at"),
                        "metadata": {},
                    })
                
                # Sort by similarity and limit
                logger.info(f"📊 Filtered results: {matched_count} vectors passed filters")
                formatted_results.sort(key=lambda x: x["score"], reverse=True)
                formatted_results = formatted_results[:limit]
            
            else:
                # Using Chroma HTTP/persistent client
                # Build where filter conditions
                where_conditions = []

                if organization_id:
                    where_conditions.append({
                        "organization_id": {"$eq": str(organization_id)}
                    })

                if knowledge_base_id:
                    where_conditions.append({
                        "knowledge_base_id": {"$eq": str(knowledge_base_id)}
                    })

                if upload_id:
                    where_conditions.append({
                        "upload_id": {"$eq": str(upload_id)}
                    })

                if department:
                    where_conditions.append({
                        "department": {"$eq": department}
                    })

                where_filter = None
                if where_conditions:
                    if len(where_conditions) == 1:
                        where_filter = where_conditions[0]
                    else:
                        where_filter = {"$and": where_conditions}

                # Query the collection
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=where_filter,
                )

                # Format results to match Qdrant format
                if results and results.get("ids") and len(results["ids"]) > 0:
                    for i, chunk_id in enumerate(results["ids"][0]):
                        metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                        distance = results["distances"][0][i] if results.get("distances") else 0.0
                        
                        # Convert distance to similarity score (cosine)
                        score = 1 - distance if distance is not None else 0.0
                        
                        formatted_results.append({
                            "chunk_id": metadata.get("chunk_id", chunk_id),
                            "document_id": metadata.get("document_id"),
                            "organization_id": metadata.get("organization_id"),
                            "upload_id": metadata.get("upload_id"),
                            "knowledge_base_id": metadata.get("knowledge_base_id"),
                            "document_name": metadata.get("document_name"),
                            "upload_date": metadata.get("upload_date"),
                            "page_number": int(metadata.get("page_number", 1)) if metadata.get("page_number") else 1,
                            "chunk_index": int(metadata.get("chunk_index", 0)) if metadata.get("chunk_index") else 0,
                            "text": results.get("documents", [[]])[0][i] if results.get("documents") else "",
                            "embedding_model": metadata.get("embedding_model"),
                            "embedding_dimension": metadata.get("embedding_dimension"),
                            "score": score,
                            "author": metadata.get("author"),
                            "department": metadata.get("department"),
                            "tags": metadata.get("tags", "").split(",") if metadata.get("tags") else [],
                            "language": metadata.get("language"),
                            "created_at": metadata.get("created_at"),
                            "metadata": {},
                        })

            logger.info(f"🔍 Found {len(formatted_results)} vectors from {search_info}")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching collection '{collection_name}': {e}")
            return []

    async def delete_vectors_by_upload(self, upload_id: uuid.UUID, knowledge_base_id: Optional[uuid.UUID] = None) -> int:
        """
        Delete all vectors for a specific upload from KB-specific or default collection.
        
        Used during per-KB reindexing to remove old vectors before re-uploading.
        """
        collection = self._get_or_create_collection(knowledge_base_id)
        if collection is None:
            logger.warning("Failed to get collection - skipping delete")
            return 0

        try:
            # If using in-memory store
            if isinstance(collection, dict) and "ids" in collection:
                # Find and remove entries with matching upload_id
                indices_to_remove = []
                for i, metadata in enumerate(collection["metadatas"]):
                    if metadata.get("upload_id") == str(upload_id):
                        indices_to_remove.append(i)
                
                # Remove in reverse order to preserve indices
                for i in sorted(indices_to_remove, reverse=True):
                    collection["ids"].pop(i)
                    if i < len(collection["embeddings"]):
                        collection["embeddings"].pop(i)
                    if i < len(collection["documents"]):
                        collection["documents"].pop(i)
                    if i < len(collection["metadatas"]):
                        collection["metadatas"].pop(i)
                
                kb_info = f" from KB {knowledge_base_id}" if knowledge_base_id else " from default"
                logger.info(f"🗑️ Deleted {len(indices_to_remove)} vectors for upload {upload_id}{kb_info}")
                
                # Save to disk
                ChromaVectorStore._save_to_disk()
                return len(indices_to_remove)
            else:
                # Using Chroma HTTP/persistent client
                collection.delete(
                    where={"upload_id": {"$eq": str(upload_id)}}
                )

                kb_info = f" from KB {knowledge_base_id}" if knowledge_base_id else " from default"
                logger.info(f"🗑️ Deleted vectors for upload {upload_id}{kb_info}")
                
                # Save to disk
                ChromaVectorStore._save_to_disk()
                return 1  # Chroma doesn't return count, so we return 1

        except Exception as e:
            logger.warning(f"Error deleting vectors for upload {upload_id}: {e}")
            return 0

    async def delete_collection(self, knowledge_base_id: uuid.UUID) -> bool:
        """
        Delete entire KB-specific collection from Chroma.
        
        Used when a Knowledge Base is deleted to clean up all associated vectors and collections.
        This ensures complete cleanup and prevents orphaned collections.
        """
        collection_name = self._get_collection_name(knowledge_base_id)

        try:
            # If using in-memory store
            if ChromaVectorStore._shared_in_memory_store and collection_name in ChromaVectorStore._shared_in_memory_store:
                del ChromaVectorStore._shared_in_memory_store[collection_name]
                if collection_name in self._collections:
                    del self._collections[collection_name]
                logger.info(f"✅ Deleted in-memory collection '{collection_name}' for KB {knowledge_base_id}")
                
                # CRITICAL: Save to disk to persist the deletion!
                ChromaVectorStore._save_to_disk()
                logger.info(f"💾 Saved updated store to disk after deleting KB {knowledge_base_id}")
                return True
            
            # Using Chroma HTTP/persistent client
            if self._client is None:
                logger.warning("Chroma client unavailable - skipping collection delete")
                return False

            # Delete the collection
            self._client.delete_collection(name=collection_name)
            
            # Remove from cache
            if collection_name in self._collections:
                del self._collections[collection_name]
            
            logger.info(f"✅ Deleted Chroma collection '{collection_name}' for KB {knowledge_base_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete Chroma collection '{collection_name}': {e}")
            return False
