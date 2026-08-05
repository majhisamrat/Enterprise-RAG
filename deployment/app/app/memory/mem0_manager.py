"""
Mem0 Long-Term Memory Manager.

Integrates with Mem0 API for persistent user memory.
Stores only meaningful long-term patterns, not temporary context.

Suitable for storage:
- User preferences
- Frequently accessed documents
- Frequently asked topics
- User role and department
- Preferred language and style

NOT suitable for storage:
- Chat messages
- Retrieval chunks
- Document contents
- Temporary session context
"""

import logging
from typing import Optional, Dict, List, Any
import asyncio
import os

logger = logging.getLogger(__name__)


class Mem0Manager:
    """
    Manages long-term memory using Mem0 API.
    
    Mem0 is used ONLY for persistent user-level patterns,
    not for session-specific or temporary context.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Mem0 manager.
        
        Args:
            api_key: Mem0 API key (from settings if not provided)
        """
        # Try to get from parameter, then from environment, then from settings
        if api_key:
            self.api_key = api_key
        else:
            try:
                from app.config.settings import settings
                self.api_key = settings.MEM0_API_KEY or os.getenv("MEM0_API_KEY")
            except ImportError:
                # Fallback if settings import fails
                self.api_key = os.getenv("MEM0_API_KEY")
        
        self.enabled = bool(self.api_key)
        
        # Try to import mem0
        self.mem0_client = None
        if self.enabled:
            try:
                from mem0 import MemoryClient
                self.mem0_client = MemoryClient(api_key=self.api_key)
                logger.info("Mem0 client initialized successfully")
            except ImportError:
                logger.warning("Mem0 SDK not installed. Install with: pip install mem0ai")
                self.enabled = False
            except Exception as e:
                logger.warning(f"Failed to initialize Mem0 client: {e}")
                self.enabled = False
    
    async def add_memory(
        self,
        user_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Add a memory to Mem0.
        
        This should be called ONLY for meaningful, long-term information.
        Examples:
        - "User prefers concise answers"
        - "User frequently accesses Finance documents"
        - "User is from Engineering department"
        
        Args:
            user_id: User identifier
            message: Memory message (natural language description)
            metadata: Optional metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.mem0_client:
            logger.debug("Mem0 is disabled, skipping add_memory")
            return False
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._add_memory_sync,
                user_id,
                message,
                metadata
            )
            logger.debug(f"Added memory for user {user_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to add memory to Mem0: {e}")
            return False
    
    def _add_memory_sync(
        self,
        user_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Synchronous add memory (for thread pool execution)."""
        if not self.mem0_client:
            return
        
        try:
            self.mem0_client.add(
                messages=[message],
                user_id=user_id,
                metadata=metadata or {}
            )
        except Exception as e:
            logger.warning(f"Mem0 add failed: {e}")
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search user's long-term memories.
        
        Args:
            user_id: User identifier
            query: Search query (natural language)
            limit: Maximum results
            
        Returns:
            List of relevant memories
        """
        if not self.enabled or not self.mem0_client:
            logger.debug("Mem0 is disabled, returning empty memories")
            return []
        
        try:
            # Run in thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._search_memories_sync,
                user_id,
                query,
                limit
            )
            return results or []
        except Exception as e:
            logger.warning(f"Failed to search memories in Mem0: {e}")
            return []
    
    def _search_memories_sync(
        self,
        user_id: str,
        query: str,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Synchronous search memories (for thread pool execution)."""
        if not self.mem0_client:
            return []
        
        try:
            results = self.mem0_client.search(
                query=query,
                user_id=user_id,
                limit=limit
            )
            # Normalize results format
            if isinstance(results, list):
                return results
            elif isinstance(results, dict):
                return results.get("results", [])
            return []
        except Exception as e:
            logger.warning(f"Mem0 search failed: {e}")
            return []
    
    async def get_user_memories(
        self,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get all memories for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of all user memories
        """
        if not self.enabled or not self.mem0_client:
            return []
        
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._get_user_memories_sync,
                user_id
            )
            return results or []
        except Exception as e:
            logger.warning(f"Failed to get user memories: {e}")
            return []
    
    def _get_user_memories_sync(self, user_id: str) -> List[Dict[str, Any]]:
        """Synchronous get memories (for thread pool execution)."""
        if not self.mem0_client:
            return []
        
        try:
            results = self.mem0_client.get(user_id=user_id)
            if isinstance(results, list):
                return results
            elif isinstance(results, dict):
                return results.get("results", [])
            return []
        except Exception as e:
            logger.warning(f"Mem0 get failed: {e}")
            return []
    
    async def delete_memory(
        self,
        user_id: str,
        memory_id: str,
    ) -> bool:
        """
        Delete a specific memory.
        
        Args:
            user_id: User identifier
            memory_id: Memory identifier
            
        Returns:
            True if successful
        """
        if not self.enabled or not self.mem0_client:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._delete_memory_sync,
                user_id,
                memory_id
            )
            logger.debug(f"Deleted memory {memory_id} for user {user_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to delete memory: {e}")
            return False
    
    def _delete_memory_sync(self, user_id: str, memory_id: str) -> None:
        """Synchronous delete memory."""
        if not self.mem0_client:
            return
        
        try:
            self.mem0_client.delete(memory_id=memory_id, user_id=user_id)
        except Exception as e:
            logger.warning(f"Mem0 delete failed: {e}")


# Global instance
_mem0_manager: Optional[Mem0Manager] = None


def get_mem0_manager() -> Mem0Manager:
    """Get or create global Mem0 manager."""
    global _mem0_manager
    if _mem0_manager is None:
        _mem0_manager = Mem0Manager()
    return _mem0_manager
