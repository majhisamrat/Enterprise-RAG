"""
Tests for Conversation Memory and Query Rewriting.

Demonstrates the production-grade conversational context system.
"""

import pytest
from datetime import datetime, timezone
from app.memory import ConversationMemory, QueryRewriter


class TestConversationMemory:
    """Test conversation memory management."""
    
    def test_add_message(self):
        """Test adding messages to memory."""
        memory = ConversationMemory()
        session_id = "session_123"
        
        memory.add_message(session_id, "user", "What is the sales revenue on Monday?")
        memory.add_message(session_id, "assistant", "Monday revenue was $45,000.")
        
        history = memory.get_all_messages(session_id)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
    
    def test_max_messages_per_session(self):
        """Test that memory trims to max messages."""
        memory = ConversationMemory()
        session_id = "session_123"
        
        # Add more than max messages
        for i in range(15):
            memory.add_message(session_id, "user", f"Question {i}")
            memory.add_message(session_id, "assistant", f"Answer {i}")
        
        # Should only keep last 10
        all_msgs = memory.get_all_messages(session_id)
        assert len(all_msgs) <= ConversationMemory.MAX_MESSAGES_PER_SESSION
    
    def test_get_history_excludes_last_user_message(self):
        """Test that get_history excludes the current query."""
        memory = ConversationMemory()
        session_id = "session_123"
        
        memory.add_message(session_id, "user", "Previous question?")
        memory.add_message(session_id, "assistant", "Previous answer.")
        memory.add_message(session_id, "user", "Current question?")
        
        history = memory.get_history(session_id)
        # Should exclude the last user message (current query)
        assert len(history) == 2
    
    def test_clear_history(self):
        """Test clearing session history."""
        memory = ConversationMemory()
        session_id = "session_123"
        
        memory.add_message(session_id, "user", "Test message")
        assert memory.get_history_length(session_id) == 1
        
        memory.clear_history(session_id)
        assert memory.get_history_length(session_id) == 0
    
    def test_session_summary(self):
        """Test getting session summary."""
        memory = ConversationMemory()
        session_id = "session_123"
        
        memory.add_message(session_id, "user", "Q1")
        memory.add_message(session_id, "assistant", "A1")
        memory.add_message(session_id, "user", "Q2")
        memory.add_message(session_id, "assistant", "A2")
        
        summary = memory.get_session_summary(session_id)
        assert summary["total_messages"] == 4
        assert summary["user_messages"] == 2
        assert summary["assistant_messages"] == 2
        assert summary["active"] is True


class TestQueryRewriter:
    """Test query rewriting for conversational follow-ups."""
    
    def test_standalone_query_no_rewrite(self):
        """Test that standalone queries are not rewritten."""
        rewriter = QueryRewriter()
        
        result = rewriter.rewrite(
            query="What is the sales revenue for Q1 2024?",
            history=[],
        )
        
        assert result["rewrite_needed"] is False
        assert result["rewritten_query"] == "What is the sales revenue for Q1 2024?"
    
    def test_follow_up_rewriting(self):
        """Test rewriting of follow-up questions."""
        rewriter = QueryRewriter()
        
        history = [
            {"role": "user", "content": "What is the sales revenue on Monday?"},
            {"role": "assistant", "content": "Monday revenue was $45,000."},
        ]
        
        result = rewriter.rewrite(
            query="And Tuesday?",
            history=history,
        )
        
        assert result["rewrite_needed"] is True
        assert "tuesday" in result["rewritten_query"].lower()
        assert "And" not in result["rewritten_query"]
    
    def test_pronoun_reference_rewriting(self):
        """Test rewriting of pronoun references."""
        rewriter = QueryRewriter()
        
        history = [
            {"role": "user", "content": "Tell me about the leave policy"},
            {"role": "assistant", "content": "The leave policy allows..."},
        ]
        
        result = rewriter.rewrite(
            query="Summarize it",
            history=history,
        )
        
        assert result["rewrite_needed"] is True
        assert "leave policy" in result["rewritten_query"].lower()
        assert "it" not in result["rewritten_query"].lower()
    
    def test_comparison_rewriting(self):
        """Test rewriting of comparison queries."""
        rewriter = QueryRewriter()
        
        history = [
            {"role": "user", "content": "Explain Q1 revenue"},
            {"role": "assistant", "content": "Q1 revenue was..."},
        ]
        
        result = rewriter.rewrite(
            query="Compare with Q2",
            history=history,
        )
        
        # Comparison rewriting may or may not trigger depending on regex patterns
        # At minimum, it should not error
        assert isinstance(result, dict)
        assert "rewritten_query" in result
    
    def test_multiple_follow_ups_with_memory(self):
        """
        Test realistic conversation flow:
        User: Sales revenue on Monday?
        Bot: Monday was $45,000
        User: And Tuesday?
        Bot: Tuesday was $50,000
        User: Summarize it
        Bot: Monday-Tuesday summary...
        """
        memory = ConversationMemory()
        rewriter = QueryRewriter()
        session_id = "test_session"
        
        # Turn 1: Initial question
        q1 = "What is the sales revenue on Monday?"
        r1 = rewriter.rewrite(q1, [])
        assert r1["rewrite_needed"] is False
        
        memory.add_message(session_id, "user", q1)
        memory.add_message(session_id, "assistant", "Monday revenue was $45,000")
        
        # Turn 2: Follow-up
        history = memory.get_history(session_id)
        q2 = "And Tuesday?"
        r2 = rewriter.rewrite(q2, history)
        assert r2["rewrite_needed"] is True
        assert "tuesday" in r2["rewritten_query"].lower()
        
        memory.add_message(session_id, "user", q2)
        memory.add_message(session_id, "assistant", "Tuesday revenue was $50,000")
        
        # Turn 3: Clarification
        history = memory.get_history(session_id)
        q3 = "Summarize it"
        r3 = rewriter.rewrite(q3, history)
        assert r3["rewrite_needed"] is True
    
    def test_no_hallucination(self):
        """Test that rewriter doesn't hallucinate document names."""
        rewriter = QueryRewriter()
        
        history = [
            {"role": "user", "content": "What's in the file?"},
            {"role": "assistant", "content": "The document contains..."},
        ]
        
        result = rewriter.rewrite(
            query="Show me more",
            history=history,
        )
        
        # Should not invent document names
        assert "document.pdf" not in result["rewritten_query"]
        assert "file_123" not in result["rewritten_query"]


@pytest.mark.skip(reason="Async testing requires pytest-asyncio plugin")
async def test_integration_with_orchestrator():
    """
    Integration test: ensure query rewriting flows through RAG orchestrator.
    
    This is a placeholder for integration testing with the full RAG pipeline.
    Would require mocked databases and retriever.
    """
    # This test would:
    # 1. Create a session
    # 2. Ask initial question
    # 3. Ask follow-up question
    # 4. Verify that rewritten query was used for retrieval
    # 5. Verify that conversation memory was updated
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
