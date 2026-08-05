# Multi-Layer Memory Architecture for Enterprise RAG

## Overview

A production-grade three-layer memory system that enables ChatGPT/Claude-style conversation memory while maintaining retrieval accuracy.

```
                    User Query

                        ↓

            Session State Manager
        (Active Conversation Context)

                    ↓

        ┌───────────────┬───────────────┐

        ↓               ↓               ↓

    Short-Term      Mem0            Context
    Memory          (Long-Term)      Builder
    (10 msgs)       (Preferences)    (Unified)

        ↓               ↓               ↓

        └───────────────┬───────────────┘

                    ↓

            Query Rewriter

                    ↓

            Hybrid Retrieval

                    ↓

            Reranker + LLM

                    ↓

        Response + Memory Update
```

## Three-Layer Architecture

### Layer 1: Session State (Active Conversation)

**What it stores**:
- Current knowledge base
- Current document  
- Current topic (auto-detected)
- Current entities (day, Q1, etc.)
- Last retrieved sources (top 10)
- Last user question
- Last rewritten question
- Last answer summary (1-2 sentences)
- Conversation turn count

**Lifetime**: Session duration (cleared on logout)

**Example**:
```python
session_state = {
    "session_id": "abc-123",
    "current_knowledge_base": "Weekly Sales",
    "current_document": "Weekly_Sales_Report.pdf",
    "current_topic": "Sales Revenue",
    "current_entities": {
        "day": "Monday",
        "amount": "$68,540"
    },
    "last_retrieved_sources": [
        {"name": "Weekly_Sales_Report.pdf", "page": 1, "score": 0.95},
        {"name": "Weekly_Sales_Report.pdf", "page": 2, "score": 0.87},
    ],
    "last_user_question": "sales on tuesday ?",
    "last_rewritten_question": "sales tuesday?",
    "conversation_turn": 2,
}
```

**Updated after every interaction with:**
- Retrieved sources
- Detected topic & entities
- User question
- Answer summary

### Layer 2: Mem0 Long-Term Memory

**What it stores**:
- User preferences (concise answers, structured format, etc.)
- Frequently accessed documents
- Frequently accessed topics
- User role and department
- Preferred language/style
- Behavioral patterns

**Lifetime**: Persistent (across sessions)

**Examples of what to store**:
```
"User prefers concise bullet-point answers"
"User frequently accesses Finance documents"
"User is from Sales department"
"User prefers reports in Excel format"
"User usually starts with 'sales on...'"
```

**Examples of what NOT to store**:
```
❌ "and tuesday ?"  (temporary context)
❌ Full chat history (use Session State)
❌ Retrieved document contents
❌ Retrieval chunks
❌ Temporary entities
```

**Usage pattern**:
- Only store after detecting a meaningful pattern
- Search Mem0 with user query to extract preferences
- Use in context building to personalize behavior

### Layer 3: Context Builder

**What it does**:
Combines Session State + Mem0 into unified agent context.

**Builds**:
```python
context = {
    "session": {
        "kb": "Weekly Sales",
        "document": "Report.pdf",
        "topic": "Sales Revenue",
        "turn": 2
    },
    "long_term_memory": {
        "preferences": ["concise answers", "bullet points"],
        "patterns": ["frequently asks about revenue"]
    },
    "conversation": {
        "last_question": "sales on tuesday ?",
        "last_answer_summary": "Tuesday sales were $68,540",
        "history": [...]
    },
    "knowledge": {
        "sources_count": 3,
        "top_source": "Weekly_Sales_Report.pdf"
    }
}
```

**Used by**:
- Query Rewriter (to rewrite follow-ups intelligently)
- LLM Generator (to personalize responses)
- Logging (to track session context)

## Key Components

### 1. SessionStateManager (`app/memory/session_state.py`)

**Manages active session context**.

```python
from app.memory import get_session_manager

session_manager = get_session_manager()

# Create new session
session = session_manager.create_session(
    session_id="abc-123",
    user_id="user-456",
    organization_id="org-789"
)

# Update context
session_manager.update_knowledge_base("abc-123", "kb-1", "Weekly Sales")
session_manager.update_document("abc-123", "doc-1", "Report.pdf")
session_manager.update_topic("abc-123", "Sales Revenue")
session_manager.update_entities("abc-123", {"day": "Monday", "amount": "$45,000"})

# Update retrieved sources
session_manager.update_retrieved_sources("abc-123", retrieved_docs)

# Update after interaction
session_manager.update_interaction(
    "abc-123",
    user_question="sales on tuesday ?",
    rewritten_question="sales tuesday?",
    answer="Tuesday sales were $68,540",
    answer_summary="Tuesday sales: $68,540"
)

# Get context summary
context = session_manager.get_context_summary("abc-123")
# Returns: {"session_id": "...", "kb": "Weekly Sales", "topic": "Sales Revenue", ...}
```

### 2. TopicTracker (`app/memory/topic_tracker.py`)

**Automatically detects conversation topics and entities**.

```python
from app.memory import get_topic_tracker

topic_tracker = get_topic_tracker()

# Detect topic
topic, category, confidence = topic_tracker.detect_topic("What is the sales revenue on Monday?")
# Returns: ("Sales Revenue", TopicCategory.SALES, 0.92)

# Extract entities
entities = topic_tracker.extract_entities("sales on tuesday", TopicCategory.SALES)
# Returns: {"day": "Tuesday"}
```

**Supported topics**:
- Sales Revenue
- Financial Reports
- Leave Policy
- Employee Handbook
- Meeting Notes
- Contracts
- And many more...

**Auto-detected entities**:
- Days (Monday, Tuesday, etc.)
- Quarters (Q1, Q2, Q3, Q4)
- Months
- Amounts ($45,000)
- Roles (Engineer, Manager, etc.)

### 3. Mem0Manager (`app/memory/mem0_manager.py`)

**Manages long-term user memory using Mem0 API**.

```python
from app.memory import get_mem0_manager

mem0 = get_mem0_manager()

# Add a long-term memory
await mem0.add_memory(
    user_id="user-123",
    message="User prefers concise bullet-point answers"
)

# Search memories
memories = await mem0.search_memories(
    user_id="user-123",
    query="user preferences and patterns",
    limit=10
)

# Get all memories for a user
all_memories = await mem0.get_user_memories("user-123")

# Delete a memory
await mem0.delete_memory("user-123", "memory-id")
```

**Environment setup**:
```bash
export MEM0_API_KEY="your-mem0-api-key"
```

### 4. ContextBuilder (`app/memory/context_builder.py`)

**Builds unified context from all layers**.

```python
from app.memory import get_context_builder

builder = get_context_builder()

# Build complete context
context = builder.build_context(
    session_state=session,
    mem0_memories=memories,
    conversation_history=history
)

# Get summary for logging
summary = builder.build_context_summary(context)
# Returns: "KB: Weekly Sales | Doc: Report.pdf | Topic: Revenue | Memories: 5 | History: 8 msgs"

# Extract for query rewriter
rewriter_context = builder.extract_context_for_rewriter(context)

# Extract for LLM
llm_context = builder.extract_context_for_llm(context)
```

### 5. MemoryService (Orchestrator) (`app/memory/memory_service.py`)

**Central coordinator for all memory operations**.

```python
from app.memory import get_memory_service

memory_service = get_memory_service()

# Initialize session
await memory_service.initialize_session(
    session_id="abc-123",
    user_id="user-456"
)

# Process interaction (main method)
result = await memory_service.process_interaction(
    session_id="abc-123",
    user_question="sales on tuesday ?",
    retrieved_documents=[...],
    answer="Tuesday sales were $68,540",
    conversation_history=[...]
)
# Returns: {
#   "rewritten_query": "sales tuesday?",
#   "rewrite_needed": True,
#   "topic": "Sales Revenue",
#   "entities": {"day": "Tuesday"},
#   "context": {...},
#   "context_summary": "KB: Weekly Sales | Topic: Revenue..."
# }

# Update long-term memory (only for meaningful info)
await memory_service.update_long_term_memory(
    user_id="user-456",
    message="User frequently asks about sales data"
)

# Cleanup on logout
memory_service.cleanup_session("abc-123")
```

## Integration with RAG Pipeline

### Before (Original)

```
User Query
    ↓
Hybrid Retrieval
    ↓
LLM
```

### After (With Multi-Layer Memory)

```
User Query
    ↓
Session State Manager (current KB, doc, topic)
    ↓
Mem0 Loader (user preferences)
    ↓
Context Builder (unified context)
    ↓
Query Rewriter (using full context)
    ↓
Hybrid Retrieval (with rewritten query)
    ↓
Reranker
    ↓
LLM (with full context)
    ↓
Memory Update (session + Mem0)
    ↓
Response
```

## Query Rewriting Examples

### Example 1: Simple Follow-up

```
Turn 1:
  User:     "sales on tuesday ?"
  Topic:    "Sales Revenue"
  Document: "Weekly_Sales_Report.pdf"

Turn 2:
  User:     "and thursday ?"
  Session:  Topic="Sales Revenue", Doc="Weekly_Sales_Report.pdf"
  Rewrite:  "sales thursday ?"  ← Uses session context
  Result:   "Thursday sales were $72,100"
```

### Example 2: Source Reference

```
Turn 1:
  User:     "What is the leave policy?"
  Retrieved: ["HR_Handbook.pdf", "Leave_Policy.docx"]
  Session:  Topic="Leave Policy", Sources=[...]

Turn 2:
  User:     "Explain Source 2"
  Session:  Sources available, Source 2 = "Leave_Policy.docx"
  Action:   Directly reference Source 2 without re-searching
  Result:   Explains Source 2 using cached reference
```

### Example 3: Comparison

```
Turn 1:
  User:     "Q1 revenue"
  Topic:    "Sales Revenue"

Turn 2:
  User:     "Compare with Q2"
  Session:  Topic="Sales Revenue", Last Question="Q1 revenue"
  Rewrite:  "Compare Q1 revenue with Q2 revenue"
  Result:   Side-by-side comparison
```

## Memory Priority

When making decisions, memory priority is:

1. **Session State** (highest)
   - Current KB, document, topic
   - Last retrieved sources
   - Current conversation context

2. **Mem0** (middle)
   - User preferences
   - Behavioral patterns
   - Frequently accessed resources

3. **RAG Retrieval** (lowest)
   - Retrieved documents
   - Ranked results

## Logging & Monitoring

### Comprehensive Logging

Every interaction logs:
```
Query Rewriting: original='and thursday ?' | rewritten='sales thursday ?' | needed=True | type=follow_up | history_length=2
Memory Update: topic=Sales Revenue | rewrite=True | context=[KB: Weekly Sales | Doc: Report.pdf | Topic: Sales Revenue | Memories: 3 | History: 4 msgs]
Session Context: turn=2, kb=Weekly Sales, document=Report.pdf, topic=Sales Revenue, sources=5
```

### Metrics to Track

- `rewrite_needed`: % of queries requiring rewriting (expect 30-40%)
- `topic_detection_accuracy`: % of correct topic detection
- `memory_hit_rate`: % of queries using long-term memory
- `source_reuse_rate`: % of "Explain Source X" without re-search
- `session_turn_count`: Average turns per session

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Session creation | <1ms | In-memory |
| Topic detection | 2-5ms | Keyword matching |
| Entity extraction | 1-3ms | Regex-based |
| Context building | 3-5ms | Combining layers |
| Mem0 search | 200-500ms | API call (optional) |
| Query rewriting | 2-5ms | Using session context |
| Total overhead | <20ms | Per interaction |

## Configuration

### Session Limits

```python
# In app/memory/session_state.py
SessionStateManager.MAX_MESSAGES_PER_SESSION = 10  # Stored in memory
# Full history still in database
```

### Topic Detection

```python
# In app/memory/topic_tracker.py
TopicTracker.MIN_CONFIDENCE = 0.5  # Minimum confidence for topic detection
```

### Mem0 Settings

```bash
# Enable/disable in environment
export MEM0_API_KEY="your-key"  # If not set, Mem0 is disabled gracefully
```

## Best Practices

### What to Store in Session State

✅ **Store**:
- Current KB and document
- Detected topic
- Entities (day, quarter, amount)
- Retrieved sources (top 10)
- Last question and answer

### What to Store in Mem0

✅ **Store**:
- "User prefers concise answers"
- "User frequently accesses Finance documents"
- "User is from Sales department"
- "User works with Excel files"

❌ **Don't Store**:
- Every chat message
- Retrieval chunks
- Document contents
- Temporary context

### When to Update Mem0

- After detecting a meaningful pattern (after ~3 similar queries)
- User explicitly provides preference
- System detects behavioral change
- Not on every single interaction

## Troubleshooting

### Issue: Memory not updating

**Check**:
1. Is session_id being passed?
2. Is `process_interaction()` being called?
3. Check logs for memory update messages

### Issue: Topic detection incorrect

**Check**:
1. Confidence threshold (default 0.5)
2. Keywords in `TopicTracker.TOPIC_KEYWORDS`
3. Add domain-specific keywords

### Issue: Mem0 not working

**Check**:
1. Is `MEM0_API_KEY` set?
2. Check logs for "Mem0 disabled"
3. Mem0 gracefully disables on error (no impact)

### Issue: Rewriting too aggressive/weak

**Check**:
1. Session context available?
2. Memory history length > 0?
3. Adjust template patterns in query_rewriter

## Future Enhancements

1. **Semantic similarity** - Filter history by semantic relevance
2. **Caching** - Cache rewritten queries  for identical inputs
3. **Multi-language** - Support multilingual conversations
4. **User segmentation** - Different strategies for different user types
5. **A/B testing** - Compare different rewriting strategies
6. **Analytics** - Dashboard for memory metrics

---

**Status**: Production-ready  
**Date**: August 4, 2026  
**Architecture Version**: 3.0 (Multi-layer)
