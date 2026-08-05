"""
Conversation Memory and Query Rewriting module.

Provides production-grade conversational context management for RAG systems.

Three-Layer Architecture:
1. Session State - Active conversation context
2. Mem0 Integration - Long-term user preferences ONLY (not conversation)
3. Context Builder - Unified context for RAG pipeline
"""

# Short-term memory
from app.memory.memory_manager import (
    ConversationMemory,
    ConversationMessage,
    get_memory_manager,
    memory_manager,
)

# Query rewriting
from app.memory.query_rewriter import (
    QueryRewriter,
    QueryType,
    get_query_rewriter,
    query_rewriter,
)

# Session state management
from app.memory.session_state import (
    SessionState,
    SessionStateManager,
    get_session_manager,
    RetrievedSource,
)

# Topic tracking
from app.memory.topic_tracker import (
    TopicTracker,
    TopicCategory,
    get_topic_tracker,
)

# Mem0 integration (for long-term preferences ONLY)
from app.memory.mem0_manager import (
    Mem0Manager,
    get_mem0_manager,
)

# Context building
from app.memory.context_builder import (
    ContextBuilder,
    get_context_builder,
)

# Main orchestrator
from app.memory.memory_service import (
    MemoryService,
    get_memory_service,
)

__all__ = [
    # Short-term memory
    "ConversationMemory",
    "ConversationMessage",
    "get_memory_manager",
    "memory_manager",
    
    # Query rewriting
    "QueryRewriter",
    "QueryType",
    "get_query_rewriter",
    "query_rewriter",
    
    # Session state
    "SessionState",
    "SessionStateManager",
    "get_session_manager",
    "RetrievedSource",
    
    # Topic tracking
    "TopicTracker",
    "TopicCategory",
    "get_topic_tracker",
    
    # Mem0 integration (long-term preferences only)
    "Mem0Manager",
    "get_mem0_manager",
    
    # Context building
    "ContextBuilder",
    "get_context_builder",
    
    # Main service
    "MemoryService",
    "get_memory_service",
]
