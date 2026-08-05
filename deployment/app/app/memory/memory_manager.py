"""
Production-grade Conversation Memory Manager for RAG Systems.

Maintains short-term conversation context for multi-turn interactions.
Stores only the last 10 messages per session to prevent context bloat.
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ConversationMessage:
    """Lightweight representation of a conversation message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationMessage":
        """Create from dictionary."""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=timestamp or datetime.now(timezone.utc),
        )


class ConversationMemory:
    """
    Conversation memory manager with Mem0 integration.
    
    - Stores conversation history per session (in-memory cache)
    - Persists to Mem0 for cross-session access
    - Maintains only the last 10 messages per session in local cache
    - Provides efficient retrieval for context building
    - Thread-safe operations
    """
    
    MAX_MESSAGES_PER_SESSION = 10
    
    def __init__(self):
        """Initialize in-memory storage for active sessions."""
        # session_id -> List[ConversationMessage]
        self._memory: Dict[str, List[ConversationMessage]] = {}
        logger.debug("ConversationMemory initialized")
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Add a message to conversation memory.
        
        Stores in local cache only (trimmed to MAX_MESSAGES_PER_SESSION).
        Database persistence is handled by ChatRepository.
        
        Args:
            session_id: Unique session identifier
            role: "user" or "assistant"
            content: Message content
            timestamp: Message timestamp (defaults to now)
            user_id: User ID (not used - kept for backwards compatibility)
        """
        if not session_id:
            logger.warning("Cannot add message: session_id is empty")
            return
        
        if role not in ("user", "assistant"):
            logger.warning(f"Invalid role: {role}. Must be 'user' or 'assistant'")
            return
        
        timestamp = timestamp or datetime.now(timezone.utc)
        message = ConversationMessage(role=role, content=content, timestamp=timestamp)
        
        if session_id not in self._memory:
            self._memory[session_id] = []
        
        self._memory[session_id].append(message)
        
        # Trim to max messages in local cache
        if len(self._memory[session_id]) > self.MAX_MESSAGES_PER_SESSION:
            self._memory[session_id] = self._memory[session_id][-self.MAX_MESSAGES_PER_SESSION:]
            logger.debug(f"Trimmed session {session_id} to {self.MAX_MESSAGES_PER_SESSION} messages")

    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Returns only the most recent messages (excluding the current query).
        Useful for building context for query rewriting.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of conversation messages as dictionaries
        """
        if session_id not in self._memory:
            return []
        
        messages = self._memory[session_id]
        if not messages:
            return []
        
        # Remove the last user message (current query) from history
        # to avoid circular reference
        history = messages[:-1] if messages[-1].role == "user" else messages
        
        return [msg.to_dict() for msg in history]
    
    def get_all_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all conversation messages for a session.
        
        Includes the current query.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of all conversation messages
        """
        if session_id not in self._memory:
            return []
        
        return [msg.to_dict() for msg in self._memory[session_id]]
    
    def clear_history(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        if session_id in self._memory:
            del self._memory[session_id]
            logger.info(f"Cleared conversation history for session {session_id}")
    
    def get_history_length(self, session_id: str) -> int:
        """Get number of messages in conversation history."""
        return len(self._memory.get(session_id, []))
    
    def trim_history(self, session_id: str, max_messages: Optional[int] = None) -> None:
        """
        Manually trim conversation history to specified length.
        
        Args:
            session_id: Unique session identifier
            max_messages: Maximum messages to keep (defaults to MAX_MESSAGES_PER_SESSION)
        """
        max_messages = max_messages or self.MAX_MESSAGES_PER_SESSION
        
        if session_id not in self._memory:
            return
        
        if len(self._memory[session_id]) > max_messages:
            self._memory[session_id] = self._memory[session_id][-max_messages:]
            logger.debug(f"Trimmed session {session_id} to {max_messages} messages")
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary statistics for a session."""
        messages = self._memory.get(session_id, [])
        user_msgs = [m for m in messages if m.role == "user"]
        assistant_msgs = [m for m in messages if m.role == "assistant"]
        
        return {
            "session_id": session_id,
            "total_messages": len(messages),
            "user_messages": len(user_msgs),
            "assistant_messages": len(assistant_msgs),
            "active": len(messages) > 0,
            "first_message_time": messages[0].timestamp.isoformat() if messages else None,
            "last_message_time": messages[-1].timestamp.isoformat() if messages else None,
        }
    
    def load_from_db_messages(
        self,
        session_id: str,
        db_messages: List[Dict[str, Any]],
    ) -> None:
        """
        Load conversation history from database messages.
        
        This is called when a user opens an existing session.
        Takes the last MAX_MESSAGES_PER_SESSION from the database.
        
        Args:
            session_id: Unique session identifier
            db_messages: List of message dictionaries from database
        """
        if not db_messages:
            return
        
        # Take only the most recent messages
        messages_to_load = db_messages[-self.MAX_MESSAGES_PER_SESSION:]
        
        self._memory[session_id] = []
        for msg in messages_to_load:
            try:
                self.add_message(
                    session_id=session_id,
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                    timestamp=msg.get("timestamp"),
                )
            except Exception as e:
                logger.warning(f"Failed to load message into memory: {e}")
        
        logger.info(f"Loaded {len(self._memory[session_id])} messages for session {session_id}")


# Global memory manager instance
memory_manager = ConversationMemory()


def get_memory_manager() -> ConversationMemory:
    """Get the global memory manager instance."""
    return memory_manager
