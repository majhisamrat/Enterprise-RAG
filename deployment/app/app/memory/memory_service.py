"""
Memory Service - Thin Orchestrator for Conversational Retrieval.

Minimal wrapper around core memory components:
- Session State: Active conversation context
- Conversation Memory: Last 8 messages
- Query Rewriter: Rewrite follow-ups with context
- Topic Tracker: Auto-detect topics (optional)

NO Mem0 for conversation (only long-term preferences).
NO unlimited history.
NO multi-layer complexity.
"""

import logging
from typing import Dict, List, Optional, Any

from app.memory.session_state import get_session_manager, SessionState
from app.memory.topic_tracker import get_topic_tracker
from app.memory.memory_manager import get_memory_manager

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Lightweight memory service for conversational RAG.
    
    Provides:
    - Session initialization and context tracking
    - Conversation history (last 8 messages only)
    - Query rewriting based on ConversationState
    """
    
    def __init__(self):
        """Initialize memory service."""
        self.session_manager = get_session_manager()
        self.topic_tracker = get_topic_tracker()
        self.conversation_memory = get_memory_manager()
        logger.debug("MemoryService initialized (lightweight mode)")
    
    async def initialize_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> SessionState:
        """
        Initialize a new session.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            organization_id: Organization identifier
            
        Returns:
            SessionState
        """
        session_state = self.session_manager.create_session(
            session_id,
            user_id,
            organization_id
        )
        logger.debug(f"Initialized session {session_id}")
        return session_state
    
    async def process_interaction(
        self,
        session_id: str,
        user_id: str,
        user_question: str,
        retrieved_documents: Optional[List[Dict[str, Any]]] = None,
        answer: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Process an interaction and update memory.
        
        Args:
            session_id: Session ID
            user_id: User ID
            user_question: User's question
            retrieved_documents: Retrieved documents
            answer: LLM's answer
            conversation_history: Conversation history
            
        Returns:
            Interaction metadata
        """
        session_state = self.session_manager.get_or_create_session(session_id, user_id)
        
        # Detect topic and entities
        topic, category, _ = self.topic_tracker.detect_topic(user_question)
        if topic:
            self.session_manager.update_topic(session_id, topic)
        
        entities = self.topic_tracker.extract_entities(user_question, category)
        if entities:
            self.session_manager.update_entities(session_id, entities)
        
        # Update retrieved sources
        if retrieved_documents:
            self.session_manager.update_retrieved_sources(session_id, retrieved_documents)
        
        # Update interaction
        answer_summary = self._create_answer_summary(answer) if answer else None
        self.session_manager.update_interaction(
            session_id,
            user_question=user_question,
            answer=answer,
            answer_summary=answer_summary,
        )
        
        # Store in short-term memory
        self.conversation_memory.add_message(session_id, "user", user_question)
        if answer:
            self.conversation_memory.add_message(session_id, "assistant", answer)
        
        return {
            "topic": topic,
            "category": category.value if category else None,
            "entities": entities,
            "context_summary": self.session_manager.get_context_summary(session_id),
            "stored_in_mem0": False,  # No longer storing conversation in Mem0
        }
    
    async def update_long_term_memory(
        self,
        user_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update long-term preferences in Mem0 (OPTIONAL).
        
        Only store user preferences, not conversation.
        
        Args:
            user_id: User identifier
            message: Memory message
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        # This is optional - only call if you want long-term preferences
        # For now, just log the request
        logger.debug(f"Long-term memory update requested for {user_id}: {message}")
        return True
    
    async def update_session_context(
        self,
        session_id: str,
        knowledge_base_id: Optional[str] = None,
        knowledge_base_name: Optional[str] = None,
    ) -> None:
        """
        Update session context (KB or document).
        
        Args:
            session_id: Session ID
            knowledge_base_id: KB ID
            knowledge_base_name: KB name
        """
        if knowledge_base_id and knowledge_base_name:
            self.session_manager.update_knowledge_base(
                session_id,
                knowledge_base_id,
                knowledge_base_name
            )
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get current session context summary."""
        return self.session_manager.get_context_summary(session_id)
    
    def _create_answer_summary(self, answer: str, max_length: int = 200) -> str:
        """
        Create a short summary of the answer.
        
        Args:
            answer: Full answer text
            max_length: Maximum summary length
            
        Returns:
            Summary text (1-2 sentences)
        """
        if not answer:
            return ""
        
        # Simple strategy: take first 1-2 sentences
        sentences = answer.split(". ")
        summary = sentences[0]
        
        if len(sentences) > 1 and len(summary) < max_length:
            summary += ". " + sentences[1]
        
        return summary[:max_length] + ("..." if len(summary) > max_length else "")
    
    def cleanup_session(self, session_id: str) -> None:
        """Clean up session on logout."""
        self.session_manager.clear_session(session_id)
        self.conversation_memory.clear_history(session_id)
        logger.info(f"Cleaned up session {session_id}")


# Global memory service
_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """Get or create global memory service."""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
