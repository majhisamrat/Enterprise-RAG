"""
Context Builder for Building Complete Agent Context.

Combines:
- Session State
- Mem0 Long-term Memory
- RAG Retrieval Context

Builds comprehensive context for query rewriting and LLM generation.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import asdict

from app.memory.session_state import SessionState
from app.memory.topic_tracker import TopicTracker

logger = logging.getLogger(__name__)


class ContextBuilder:
    """
    Builds complete context for RAG interactions.
    
    Combines session state, long-term memory, and retrieval context
    into a structured context object used for query rewriting and LLM generation.
    """
    
    def __init__(self, topic_tracker: Optional[TopicTracker] = None):
        """
        Initialize context builder.
        
        Args:
            topic_tracker: Optional topic tracker (creates default if not provided)
        """
        self.topic_tracker = topic_tracker or TopicTracker()
    
    def build_context(
        self,
        session_state: SessionState,
        mem0_memories: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Build complete agent context.
        
        Args:
            session_state: Current session state
            mem0_memories: Long-term memories from Mem0
            conversation_history: Recent conversation history
            
        Returns:
            Complete context dictionary
        """
        context = {
            "session": self._build_session_context(session_state),
            "long_term_memory": self._build_memory_context(mem0_memories),
            "conversation": self._build_conversation_context(
                session_state,
                conversation_history
            ),
            "knowledge": self._build_knowledge_context(session_state),
        }
        
        logger.debug(f"Built context for session {session_state.session_id}")
        return context
    
    def _build_session_context(self, session_state: SessionState) -> Dict[str, Any]:
        """Build session state context."""
        return {
            "session_id": session_state.session_id,
            "current_kb": session_state.current_knowledge_base_name,
            "current_document": session_state.current_document_name,
            "current_topic": session_state.current_topic,
            "current_entities": session_state.current_entities,
            "turn_number": session_state.conversation_turn,
        }
    
    def _build_memory_context(
        self,
        mem0_memories: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Build long-term memory context."""
        memories = mem0_memories or []
        
        context = {
            "available": len(memories) > 0,
            "count": len(memories),
            "memories": [],
        }
        
        if memories:
            # Extract relevant memory categories
            preferences = []
            patterns = []
            
            for mem in memories[:10]:  # Top 10 memories
                text = mem.get("content") if isinstance(mem, dict) else str(mem)
                
                if any(kw in text.lower() for kw in ["prefer", "like", "favorite", "usually"]):
                    preferences.append(text)
                else:
                    patterns.append(text)
            
            context["preferences"] = preferences
            context["patterns"] = patterns
            context["memories"] = [str(m) for m in memories[:5]]
        
        return context
    
    def _build_conversation_context(
        self,
        session_state: SessionState,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Build conversation context."""
        history = conversation_history or []
        
        return {
            "last_user_question": session_state.last_user_question,
            "last_rewritten_question": session_state.last_rewritten_question,
            "last_answer_summary": session_state.last_answer_summary,
            "history_length": len(history),
            "recent_history": history[-5:] if history else [],  # Last 5 messages
        }
    
    def _build_knowledge_context(
        self,
        session_state: SessionState,
    ) -> Dict[str, Any]:
        """Build knowledge/retrieval context."""
        sources = session_state.last_retrieved_sources
        
        return {
            "sources_available": len(sources) > 0,
            "sources_count": len(sources),
            "top_source": {
                "name": sources[0].document_name,
                "page": sources[0].page_number,
                "relevance": sources[0].relevance_score,
            } if sources else None,
            "all_sources": [
                {
                    "name": s.document_name,
                    "page": s.page_number,
                    "relevance": s.relevance_score,
                    "snippet": s.text_snippet[:100],
                }
                for s in sources[:5]
            ],
        }
    
    def build_context_summary(
        self,
        context: Dict[str, Any],
    ) -> str:
        """
        Build a natural language summary of context.
        
        Useful for logging and debugging.
        
        Args:
            context: Complete context dictionary
            
        Returns:
            Human-readable context summary
        """
        parts = []
        
        # Session summary
        session = context.get("session", {})
        if session.get("current_kb"):
            parts.append(f"KB: {session['current_kb']}")
        if session.get("current_document"):
            parts.append(f"Doc: {session['current_document']}")
        if session.get("current_topic"):
            parts.append(f"Topic: {session['current_topic']}")
        
        # Memory summary
        memory = context.get("long_term_memory", {})
        if memory.get("count", 0) > 0:
            parts.append(f"Memories: {memory['count']}")
        
        # Conversation summary
        conv = context.get("conversation", {})
        if conv.get("history_length", 0) > 0:
            parts.append(f"History: {conv['history_length']} msgs")
        
        # Knowledge summary
        knowledge = context.get("knowledge", {})
        if knowledge.get("sources_count", 0) > 0:
            parts.append(f"Sources: {knowledge['sources_count']}")
        
        return " | ".join(parts) if parts else "No context"
    
    def extract_context_for_rewriter(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract only the parts needed for query rewriting.
        
        Args:
            context: Complete context
            
        Returns:
            Minimal context for rewriter
        """
        return {
            "current_kb": context.get("session", {}).get("current_kb"),
            "current_topic": context.get("session", {}).get("current_topic"),
            "current_document": context.get("session", {}).get("current_document"),
            "last_question": context.get("conversation", {}).get("last_user_question"),
            "last_summary": context.get("conversation", {}).get("last_answer_summary"),
        }
    
    def extract_context_for_llm(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract context needed for LLM generation.
        
        Args:
            context: Complete context
            
        Returns:
            LLM-relevant context
        """
        return {
            "session": context.get("session"),
            "preferences": context.get("long_term_memory", {}).get("preferences", []),
            "recent_history": context.get("conversation", {}).get("recent_history", []),
            "available_sources": context.get("knowledge", {}).get("sources_count", 0),
        }


# Global builder instance
_context_builder: Optional[ContextBuilder] = None


def get_context_builder() -> ContextBuilder:
    """Get or create global context builder."""
    global _context_builder
    if _context_builder is None:
        _context_builder = ContextBuilder()
    return _context_builder
