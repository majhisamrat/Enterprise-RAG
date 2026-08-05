"""
Session State Manager for Active Conversation Memory.

Manages real-time session context including:
- Current knowledge base
- Current document
- Current topic
- Conversation history
- Retrieved sources
- Entity tracking
"""

import uuid
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class RetrievedSource:
    """Represents a retrieved document chunk."""
    document_id: str
    document_name: str
    chunk_id: str
    page_number: int
    text_snippet: str
    relevance_score: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class SessionState:
    """Complete session state snapshot."""
    session_id: str
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    
    # Current context
    current_knowledge_base_id: Optional[str] = None
    current_knowledge_base_name: Optional[str] = None
    current_document_id: Optional[str] = None
    current_document_name: Optional[str] = None
    current_topic: Optional[str] = None
    current_entities: Dict[str, str] = field(default_factory=dict)  # Entity name -> value
    
    # Retrieved sources tracking
    last_retrieved_sources: List[RetrievedSource] = field(default_factory=list)
    
    # Last interaction
    last_user_question: Optional[str] = None
    last_rewritten_question: Optional[str] = None
    last_answer_summary: Optional[str] = None
    last_answer_full: Optional[str] = None
    
    # Metadata
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    conversation_turn: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['last_retrieved_sources'] = [s.to_dict() for s in self.last_retrieved_sources]
        data['last_activity'] = self.last_activity.isoformat()
        data['created_at'] = self.created_at.isoformat()
        return data


class SessionStateManager:
    """
    Manages active session state and context.
    
    Responsibilities:
    - Track current KB and document
    - Monitor topic and entities
    - Store retrieved sources
    - Manage answer summaries
    - Update on every interaction
    """
    
    def __init__(self):
        """Initialize session state manager."""
        # session_id -> SessionState
        self._sessions: Dict[str, SessionState] = {}
        logger.debug("SessionStateManager initialized")
    
    def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> SessionState:
        """
        Create a new session state.
        
        Args:
            session_id: Unique session identifier
            user_id: User who owns the session
            organization_id: Organization context
            
        Returns:
            New SessionState
        """
        state = SessionState(
            session_id=session_id,
            user_id=user_id,
            organization_id=organization_id,
        )
        self._sessions[session_id] = state
        logger.info(f"Created session state: {session_id}")
        return state
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session state by ID."""
        return self._sessions.get(session_id)
    
    def get_or_create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> SessionState:
        """Get existing session or create new one."""
        if session_id not in self._sessions:
            return self.create_session(session_id, user_id, organization_id)
        return self._sessions[session_id]
    
    def update_knowledge_base(
        self,
        session_id: str,
        kb_id: str,
        kb_name: str,
    ) -> None:
        """Update current knowledge base context."""
        state = self.get_session(session_id)
        if state:
            state.current_knowledge_base_id = kb_id
            state.current_knowledge_base_name = kb_name
            state.last_activity = datetime.now(timezone.utc)
            logger.debug(f"Updated KB for {session_id}: {kb_name}")
    
    def update_document(
        self,
        session_id: str,
        doc_id: str,
        doc_name: str,
    ) -> None:
        """Update current document context."""
        state = self.get_session(session_id)
        if state:
            state.current_document_id = doc_id
            state.current_document_name = doc_name
            state.last_activity = datetime.now(timezone.utc)
            logger.debug(f"Updated document for {session_id}: {doc_name}")
    
    def update_topic(self, session_id: str, topic: str) -> None:
        """Update detected topic."""
        state = self.get_session(session_id)
        if state:
            state.current_topic = topic
            state.last_activity = datetime.now(timezone.utc)
            logger.debug(f"Updated topic for {session_id}: {topic}")
    
    def update_entities(self, session_id: str, entities: Dict[str, str]) -> None:
        """Update detected entities."""
        state = self.get_session(session_id)
        if state:
            state.current_entities.update(entities)
            state.last_activity = datetime.now(timezone.utc)
            logger.debug(f"Updated entities for {session_id}: {len(entities)} items")
    
    def update_retrieved_sources(
        self,
        session_id: str,
        sources: List[Dict[str, Any]],
    ) -> None:
        """
        Update retrieved sources from retrieval results.
        
        Args:
            session_id: Session ID
            sources: List of retrieved document sources
        """
        state = self.get_session(session_id)
        if state:
            retrieved_sources = []
            for src in sources[:10]:  # Keep top 10
                retrieved_sources.append(RetrievedSource(
                    document_id=src.get("document_id", ""),
                    document_name=src.get("document_name", ""),
                    chunk_id=src.get("chunk_id", ""),
                    page_number=src.get("page_number", 1),
                    text_snippet=src.get("text_snippet", "")[:200],
                    relevance_score=src.get("relevance_score", 0.0),
                ))
            state.last_retrieved_sources = retrieved_sources
            
            # Update document if available
            if retrieved_sources:
                top_source = retrieved_sources[0]
                self.update_document(session_id, top_source.document_id, top_source.document_name)
            
            logger.debug(f"Updated sources for {session_id}: {len(retrieved_sources)} items")
    
    def update_interaction(
        self,
        session_id: str,
        user_question: str,
        rewritten_question: Optional[str] = None,
        answer: Optional[str] = None,
        answer_summary: Optional[str] = None,
    ) -> None:
        """
        Update session after an interaction.
        
        Args:
            session_id: Session ID
            user_question: Original user question
            rewritten_question: Query rewritten question (if applicable)
            answer: Full answer from LLM
            answer_summary: 1-2 sentence summary of answer
        """
        state = self.get_session(session_id)
        if state:
            state.last_user_question = user_question
            state.last_rewritten_question = rewritten_question
            state.last_answer_full = answer
            state.last_answer_summary = answer_summary
            state.conversation_turn += 1
            state.last_activity = datetime.now(timezone.utc)
            logger.debug(f"Updated interaction for {session_id}, turn {state.conversation_turn}")
    
    def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get a summary of current session context.
        
        Useful for logging and debugging.
        """
        state = self.get_session(session_id)
        if not state:
            return {}
        
        return {
            "session_id": session_id,
            "kb": state.current_knowledge_base_name,
            "document": state.current_document_name,
            "topic": state.current_topic,
            "entities": state.current_entities,
            "sources_count": len(state.last_retrieved_sources),
            "turn": state.conversation_turn,
            "last_activity": state.last_activity.isoformat() if state.last_activity else None,
        }
    
    def clear_session(self, session_id: str) -> None:
        """Clear session state."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Cleared session state: {session_id}")
    
    def cleanup_inactive_sessions(self, inactive_minutes: int = 60) -> int:
        """
        Clean up sessions inactive for specified minutes.
        
        Returns:
            Number of sessions cleaned
        """
        now = datetime.now(timezone.utc)
        to_remove = []
        
        for session_id, state in self._sessions.items():
            if state.last_activity:
                elapsed = (now - state.last_activity).total_seconds() / 60
                if elapsed > inactive_minutes:
                    to_remove.append(session_id)
        
        for session_id in to_remove:
            self.clear_session(session_id)
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} inactive sessions")
        
        return len(to_remove)


# Global session state manager
_session_manager: Optional[SessionStateManager] = None


def get_session_manager() -> SessionStateManager:
    """Get or create global session state manager."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionStateManager()
    return _session_manager
