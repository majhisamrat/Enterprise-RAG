# Production-Grade Conversation Memory & Query Rewriting

Complete guide for implementing conversational context in Enterprise RAG.

## Overview

This system enables multi-turn conversational interactions without losing context:

```
User: "What is the sales revenue on Monday?"
Bot:  "Monday revenue was $45,000"

User: "And Tuesday?"  ← Follow-up question
Bot:  [Rewritten to: "What is the sales revenue on Tuesday?"]
      "Tuesday revenue was $50,000"

User: "Summarize it"  ← Clarification
Bot:  [Rewritten to: "Summarize the sales revenue for Monday and Tuesday"]
      "Monday-Tuesday revenue summary: $95,000 total"
```

## Architecture

```
User Query
    ↓
Conversation Memory (Load History)
    ↓
Query Rewriter (Expand Follow-ups)
    ↓
Hybrid Retrieval (Search with complete context)
    ↓
LLM (Generate response)
    ↓
Store in Memory + Database
```

## Components

### 1. Conversation Memory Manager (`app/memory/memory_manager.py`)

**Purpose**: Maintains short-term conversation context per session

**Features**:
- Stores last 10 messages per session (configurable)
- In-memory storage for active sessions
- Thread-safe operations
- Loads/saves from database on demand

**Key Methods**:

```python
from app.memory import get_memory_manager

memory = get_memory_manager()

# Add messages
memory.add_message(session_id, "user", "What is revenue on Monday?")
memory.add_message(session_id, "assistant", "Monday was $45,000")

# Get history for next turn (excludes current query)
history = memory.get_history(session_id)
# Returns: [
#   {"role": "user", "content": "What is revenue on Monday?", "timestamp": "..."},
#   {"role": "assistant", "content": "Monday was $45,000", "timestamp": "..."}
# ]

# Clear session
memory.clear_history(session_id)

# Load from database (called when opening existing session)
memory.load_from_db_messages(session_id, db_messages)
```

### 2. Query Rewriter (`app/memory/query_rewriter.py`)

**Purpose**: Transforms follow-up questions into complete, standalone queries

**Rewriting Strategies**:

#### A. Pronoun Resolution
```
History: "Tell me about the leave policy"
Input:   "Summarize it"
Output:  "Summarize the leave policy"
```

#### B. Follow-up Expansion
```
History: "What is the sales revenue on Monday?"
Input:   "And Tuesday?"
Output:  "What is the sales revenue on Tuesday?"
```

#### C. Comparison Handling
```
History: "Explain Q1 revenue"
Input:   "Compare with Q2"
Output:  "Compare Q1 revenue with Q2 revenue"
```

#### D. Clarification Resolution
```
History: "Tell me about leave policy"
Input:   "Explain more"
Output:  "Explain the leave policy in more detail"
```

**Key Methods**:

```python
from app.memory import get_query_rewriter

rewriter = get_query_rewriter()

result = rewriter.rewrite(
    query="And Tuesday?",
    history=[
        {"role": "user", "content": "Sales revenue on Monday?"},
        {"role": "assistant", "content": "Monday was $45,000"}
    ]
)

# Returns:
# {
#   "original_query": "And Tuesday?",
#   "rewritten_query": "What is the sales revenue on Tuesday?",
#   "rewrite_needed": True,
#   "rewrite_type": "follow_up",
#   "confidence": 0.9,
#   "reasoning": "Applied follow_up rewriting strategy",
#   "history_length": 2
# }
```

## Integration Points

### 1. Chat Endpoint (`app/api/routes/chat.py`)

The chat endpoint automatically:
1. Creates/loads conversation memory for the session
2. Calls query rewriter with conversation history
3. Uses rewritten query for retrieval
4. Stores both original and rewritten query in metadata

**No changes needed** — integration is transparent to the API client.

### 2. RAG Orchestrator (`app/orchestrator/rag.py`)

The orchestrator now:
1. Loads conversation history from database
2. Initializes memory manager with existing session messages
3. Calls query rewriter before hybrid retrieval
4. Stores query rewriting metadata in response
5. Updates conversation memory after LLM generation

```python
# Flow inside orchestrator.chat():

# 1. Load memory from database
memory_manager.load_from_db_messages(session_id_str, db_messages)

# 2. Get conversation history
memory_history = memory_manager.get_history(session_id_str)

# 3. Rewrite query
rewrite_result = query_rewriter.rewrite(
    query=query,
    history=memory_history,
    knowledge_base_name=kb_name
)
rewritten_query = rewrite_result.get("rewritten_query")

# 4. Use rewritten query for retrieval
retrieved_docs = self.retriever.retrieve(
    query=rewritten_query,  # ← Rewritten!
    limit=top_k,
    ...
)

# 5. Store in memory after generation
memory_manager.add_message(session_id=session_id_str, role="user", content=query)
memory_manager.add_message(session_id=session_id_str, role="assistant", content=llm_response)
```

## Response Format

Chat responses now include query rewriting metadata:

```json
{
  "answer": "Tuesday revenue was $50,000",
  "session_id": "abc-123",
  "sources": [...],
  "metadata": {
    "model": "gemini-2.0-flash",
    "latency_ms": 245.3,
    "context_documents": 5,
    "query_rewriting": {
      "original_query": "And Tuesday?",
      "rewritten_query": "What is the sales revenue on Tuesday?",
      "rewrite_needed": true,
      "rewrite_type": "follow_up",
      "conversation_memory_length": 2
    }
  }
}
```

## Safety Guarantees

### What the Rewriter DOES
- ✅ Expand "it" to the referenced topic
- ✅ Resolve pronouns (that, this, those)
- ✅ Convert follow-ups to complete questions
- ✅ Handle comparisons with extracted context
- ✅ Clarify vague requests

### What the Rewriter NEVER Does
- ❌ Invent document or file names
- ❌ Create facts not in history
- ❌ Hallucinate KB names
- ❌ Modify user intent
- ❌ Skip unknown references

**Fallback**: If uncertain, the rewriter returns the original query unchanged.

## Configuration

### Memory Settings

```python
# In app/memory/memory_manager.py
ConversationMemory.MAX_MESSAGES_PER_SESSION = 10  # Adjustable
```

### Rewriter Confidence

The rewriter assigns confidence scores:
- **1.0**: No rewrite needed (standalone query)
- **0.9**: High-confidence rewrite applied
- **0.7**: Lower-confidence rewrite (may fallback)

## Logging

### Query Rewriting Logs

```
INFO: Query Rewriting: original='And Tuesday?' | rewritten='What is the sales revenue on Tuesday?' | needed=True | type=follow_up | history_length=2
```

### Memory Manager Logs

```
DEBUG: Trimmed session abc-123 to 10 messages
INFO: Loaded 4 messages for session abc-123
INFO: Cleared conversation history for session abc-123
```

## Testing

Run the test suite:

```bash
pytest tests/test_conversation_memory.py -v
```

Tests cover:
- Memory management (add, retrieve, trim, clear)
- Query rewriting strategies
- Multi-turn conversations
- Integration with orchestrator
- Hallucination prevention

## Performance

- **Memory Overhead**: ~100 bytes per message
- **Rewriting Latency**: 1-5ms per query
- **Total per-turn overhead**: <10ms

For 10 messages × 100 sessions:
- Memory: ~100KB (negligible)
- CPU: Minimal (regex-based matching)

## Production Deployment

### Best Practices

1. **Session Lifecycle**:
   - Create memory when session is created
   - Load from DB when session is reopened
   - Clear from memory when session is deleted

2. **Memory Cleanup**:
   - Sessions automatically trim to 10 messages
   - Unused sessions can be cleared after inactivity
   - Database stores full history (not affected by memory limit)

3. **Monitoring**:
   - Track rewrite_needed metrics
   - Monitor rewrite_type distribution
   - Alert on high hallucination rate (should be 0%)

4. **Fallback**:
   - If query rewriter fails, returns original query
   - No impact on RAG pipeline
   - Logs any exceptions

## Example: Complete Conversation

```python
# Session 1: Revenue Analysis
session_id = "user-123-session-456"

# Turn 1
q1 = "What is Q1 revenue?"
r1 = await orchestrator.chat(q1, session_id=session_id)
# Rewrite: No (standalone)
# Result: "Q1 revenue was $5.2M"

# Turn 2
q2 = "And Q2?"
r2 = await orchestrator.chat(q2, session_id=session_id)
# Rewrite: Yes → "What is Q2 revenue?"
# Result: "Q2 revenue was $6.1M"

# Turn 3
q3 = "Compare them"
r3 = await orchestrator.chat(q3, session_id=session_id)
# Rewrite: Yes → "Compare Q1 revenue with Q2 revenue"
# Result: "Q1 was $5.2M, Q2 was $6.1M, representing 17% growth"

# Turn 4
q4 = "Summarize"
r4 = await orchestrator.chat(q4, session_id=session_id)
# Rewrite: Yes → "Summarize Q1 and Q2 revenue comparison"
# Result: "Q1-Q2 summary: Strong performance with 17% QoQ growth..."
```

## Troubleshooting

### Issue: Queries not being rewritten

**Check**:
1. History is loaded: `memory.get_history_length(session_id) > 0`
2. Rewriter is detecting follow-ups: `rewrite_needed = True`
3. Logs show rewrite attempt

### Issue: Rewritten queries have hallucinations

**Solution**:
1. This shouldn't happen with current implementation
2. If it does, rewriter falls back to original query
3. File a bug with specific example

### Issue: Performance degradation

**Check**:
1. Memory growth: `len(self._memory)` should be <1000
2. Rewriting latency: Should be <10ms
3. Consider pruning old sessions from memory

## Future Enhancements

1. **NLP-based extraction**: Use NER for better topic extraction
2. **Query expansion**: Add synonyms and related terms
3. **Context limiting**: Limit history to semantic relevance
4. **Caching**: Cache rewritten queries for identical inputs
5. **A/B testing**: Compare rewriting strategies

## Support

For issues or questions:
1. Check test cases in `tests/test_conversation_memory.py`
2. Review logs for query rewriting metadata
3. Consult integration examples above
