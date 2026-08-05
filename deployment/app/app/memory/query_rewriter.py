"""
Production-grade Query Rewriter for conversational RAG.

Rewrites follow-up questions into standalone, complete queries by:
- Reading conversation history
- Resolving pronouns and references
- Expanding context-dependent queries
- Never hallucinating or inventing information

Examples:
  History: "sales revenue on monday? -> Monday revenue was $45,000"
  Query:   "And Tuesday?"
  Rewrite: "What is the sales revenue on Tuesday?"

  History: "Tell me about leave policy"
  Query:   "Summarize it"
  Rewrite: "Summarize the leave policy"
"""

import re
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Classification of query types for rewriting strategy."""
    STANDALONE = "standalone"
    FOLLOW_UP = "follow_up"
    PRONOUN_REF = "pronoun_ref"
    COMPARISON = "comparison"
    CLARIFICATION = "clarification"


class QueryRewriter:
    """
    Intelligent query rewriter for conversational RAG.
    
    Strategies:
    1. Detect if query is already standalone (no rewrite needed)
    2. Resolve pronouns ("it", "that", "those") to previous context
    3. Expand follow-ups ("And Tuesday?" -> "What about Tuesday?")
    4. Handle comparisons ("Compare with Q2" -> "Compare Q1 with Q2")
    5. Clarifications ("Explain more" -> "Explain [previous_topic] in more detail")
    
    Safety:
    - Never invents document names
    - Never creates facts not in history
    - Only resolves explicit references
    - Falls back to original query if uncertain
    """
    
    def __init__(self):
        """Initialize query rewriter with pattern definitions."""
        self._pronoun_patterns = {
            r"^it\b": "it_reference",
            r"^that\b": "that_reference",
            r"^those\b": "those_reference",
            r"^this\b": "this_reference",
        }
        
        self._follow_up_patterns = {
            r"^and\s+": "conjunction_follow_up",
            r"^what\s+about\s+": "what_about_follow_up",
            r"^how\s+about\s+": "how_about_follow_up",
            r"^what\s+else": "what_else",
            r"^any\s+other": "any_other",
        }
        
        self._comparison_patterns = {
            r"compare\s+with": "compare_with",
            r"compare\s+to": "compare_to",
            r"versus": "versus",
            r"vs\.?": "vs",
            r"vs\b": "vs",
        }
        
        self._clarification_patterns = {
            r"explain\s+more": "explain_more",
            r"tell\s+me\s+more": "tell_more",
            r"more\s+details": "more_details",
            r"elaborate": "elaborate",
            r"summarize\s+it": "summarize_ref",
            r"sum\s+it\s+up": "sum_ref",
        }
    
    def rewrite(
        self,
        query: str,
        history: List[Dict[str, Any]],
        knowledge_base_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Rewrite a query using conversation history.
        
        Args:
            query: Current user query
            history: List of previous messages (role, content, timestamp)
            knowledge_base_name: Name of selected KB for context
            
        Returns:
            Dictionary containing:
            - original_query: Original query text
            - rewritten_query: Rewritten query (same as original if no rewrite needed)
            - rewrite_needed: Boolean indicating if rewrite was applied
            - rewrite_type: Type of rewriting applied
            - confidence: Confidence score (0-1)
            - reasoning: Explanation of rewrite decision
            - history_length: Number of messages used
        """
        result = {
            "original_query": query,
            "rewritten_query": query,
            "rewrite_needed": False,
            "rewrite_type": None,
            "confidence": 1.0,
            "reasoning": "Query is already standalone",
            "history_length": len(history),
        }
        
        # Clean query
        cleaned_query = query.strip().lower()
        
        # Check if query is already standalone
        if self._is_standalone(cleaned_query, history):
            logger.debug(f"Query is standalone, no rewrite needed: {query}")
            return result
        
        # Attempt to rewrite
        if not history:
            logger.debug("No history available for rewriting")
            return result
        
        # Get last user and assistant messages
        user_context = self._get_last_user_message(history)
        assistant_context = self._get_last_assistant_message(history)
        
        if not user_context:
            return result
        
        # Detect query type and apply rewriting strategy
        query_type = self._detect_query_type(cleaned_query)
        
        if query_type == QueryType.PRONOUN_REF:
            rewritten = self._rewrite_pronoun_reference(
                cleaned_query,
                user_context,
                assistant_context,
            )
        elif query_type == QueryType.FOLLOW_UP:
            rewritten = self._rewrite_follow_up(cleaned_query, user_context)
        elif query_type == QueryType.COMPARISON:
            rewritten = self._rewrite_comparison(cleaned_query, user_context)
        elif query_type == QueryType.CLARIFICATION:
            rewritten = self._rewrite_clarification(
                cleaned_query,
                user_context,
                assistant_context,
            )
        else:
            rewritten = None
        
        # Update result if rewriting succeeded
        if rewritten and rewritten != cleaned_query:
            result["rewritten_query"] = rewritten
            result["rewrite_needed"] = True
            result["rewrite_type"] = query_type.value
            result["confidence"] = 0.9
            result["reasoning"] = f"Applied {query_type.value} rewriting strategy"
            logger.info(
                f"Query rewritten ({query_type.value}): "
                f"'{query}' -> '{rewritten}'"
            )
        
        return result
    
    def _is_standalone(self, query: str, history: List[Dict[str, Any]]) -> bool:
        """
        Check if query is already standalone (doesn't need rewriting).
        
        Standalone queries:
        - Have complete subject and predicate
        - Don't start with pronouns or follow-up markers
        - Are not pure follow-ups
        """
        if not query:
            return False
        
        # Check for follow-up markers at start
        for pattern in self._follow_up_patterns.keys():
            if re.match(pattern, query):
                return False
        
        # Check for pronoun references at start
        for pattern in self._pronoun_patterns.keys():
            if re.match(pattern, query):
                return False
        
        # Check for clarification patterns
        for pattern in self._clarification_patterns.keys():
            if re.match(pattern, query):
                return False
        
        # Query appears to be standalone
        return True
    
    def _detect_query_type(self, query: str) -> QueryType:
        """Detect the type of follow-up query."""
        # Check order matters: be specific first
        
        # Pronouns
        for pattern in self._pronoun_patterns.keys():
            if re.match(pattern, query):
                return QueryType.PRONOUN_REF
        
        # Clarifications
        for pattern in self._clarification_patterns.keys():
            if re.search(pattern, query):
                return QueryType.CLARIFICATION
        
        # Comparisons
        for pattern in self._comparison_patterns.keys():
            if re.search(pattern, query):
                return QueryType.COMPARISON
        
        # Follow-ups
        for pattern in self._follow_up_patterns.keys():
            if re.match(pattern, query):
                return QueryType.FOLLOW_UP
        
        return QueryType.STANDALONE
    
    def _rewrite_pronoun_reference(
        self,
        query: str,
        user_context: str,
        assistant_context: Optional[str],
    ) -> Optional[str]:
        """Rewrite pronoun references like 'it', 'that', 'those'."""
        # Extract the main topic from user context
        topic = self._extract_topic(user_context)
        
        if not topic:
            logger.debug(f"Could not extract topic for pronoun rewriting: {query}")
            return None
        
        # Replace pronouns with extracted topic
        rewritten = re.sub(r"^it\b", f"the {topic}", query, flags=re.IGNORECASE)
        rewritten = re.sub(r"^that\b", f"the {topic}", rewritten, flags=re.IGNORECASE)
        rewritten = re.sub(r"^those\b", f"the {topic}", rewritten, flags=re.IGNORECASE)
        rewritten = re.sub(r"^this\b", f"the {topic}", rewritten, flags=re.IGNORECASE)
        
        return rewritten if rewritten != query else None
    
    def _rewrite_follow_up(self, query: str, user_context: str) -> Optional[str]:
        """Rewrite follow-up questions like 'And Tuesday?'."""
        # Remove follow-up markers
        rewritten = re.sub(r"^and\s+", "", query, flags=re.IGNORECASE).strip()
        rewritten = re.sub(r"^what\s+about\s+", "", rewritten, flags=re.IGNORECASE).strip()
        rewritten = re.sub(r"^how\s+about\s+", "", rewritten, flags=re.IGNORECASE).strip()
        
        if not rewritten or rewritten == query:
            return None
        
        # Extract template from previous query
        template = self._extract_template(user_context)
        
        if template:
            # Try to fill template with new context
            # Remove trailing ? from rewritten if it exists, then add template and ?
            rewritten_clean = rewritten.rstrip("?").strip()
            rewritten = f"{template} {rewritten_clean}?"
        else:
            # If no template, still format nicely
            rewritten_clean = rewritten.rstrip("?").strip()
            # Try to infer a generic question format
            if not rewritten_clean.startswith(("what", "how", "when", "where", "why", "who")):
                rewritten = f"What about {rewritten_clean}?"
        
        return rewritten
    
    def _rewrite_comparison(self, query: str, user_context: str) -> Optional[str]:
        """Rewrite comparison queries like 'Compare with Q2'."""
        topic = self._extract_topic(user_context)
        
        if not topic:
            return None
        
        # Extract what to compare with
        comparison_term = re.search(r"(?:with|to|versus|vs\.?)\s+(\w+)", query)
        
        if comparison_term:
            compared_to = comparison_term.group(1)
            return f"Compare {topic} with {compared_to}"
        
        return None
    
    def _rewrite_clarification(
        self,
        query: str,
        user_context: str,
        assistant_context: Optional[str],
    ) -> Optional[str]:
        """Rewrite clarification queries like 'Summarize it'."""
        topic = self._extract_topic(user_context)
        
        if not topic:
            return None
        
        # Handle specific clarification patterns
        if re.search(r"summarize\s+it|sum\s+it\s+up", query, flags=re.IGNORECASE):
            return f"Summarize {topic}"
        
        if re.search(r"explain\s+more|tell\s+me\s+more", query, flags=re.IGNORECASE):
            return f"Explain {topic} in more detail"
        
        if re.search(r"more\s+details|elaborate", query, flags=re.IGNORECASE):
            return f"Provide more details about {topic}"
        
        return None
    
    def _extract_topic(self, text: str) -> Optional[str]:
        """
        Extract the main topic/subject from a question.
        
        This is a simple heuristic. In production, could use NLP/NER.
        """
        if not text:
            return None
        
        text = text.strip()
        
        # Remove question marks
        text = text.rstrip("?")
        
        # Common patterns: "What is <topic>?", "Tell me about <topic>"
        patterns = [
            r"(?:what is|about|regarding|on|in)\s+(.+?)(?:\?|$)",
            r"(?:tell me about|explain|describe)\s+(.+?)(?:\?|$)",
            r"^([^?]*?)(?:\?|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                topic = match.group(1).strip()
                # Clean up common words
                topic = re.sub(r"^(?:the|a|an)\s+", "", topic, flags=re.IGNORECASE)
                if topic and len(topic) > 2:
                    return topic
        
        return None
    
    def _extract_template(self, text: str) -> Optional[str]:
        """Extract query template from previous user query."""
        # Simple template extraction
        # e.g., "sales revenue on Monday?" -> "sales revenue on"
        # e.g., "What is the sales revenue on Monday?" -> "What is the sales revenue on"
        
        if not text:
            return None
        
        text = text.strip().rstrip("?").strip()
        
        # Pattern 1: Formal question with verb
        # "What is the sales revenue on Monday?" -> "What is the sales revenue on"
        patterns = [
            r"(what is|what are|tell me about|explain|describe|list|show)\s+(.+?)\s+(?:on|in|for|during|at)\s+\w+",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                verb = match.group(1)
                subject = match.group(2)
                return f"{verb} {subject}"
        
        # Pattern 2: Simple query with date/time reference
        # "sales on monday?" -> "sales on"
        # "revenue for Q1?" -> "revenue for"
        match = re.search(r"^(.+?)\s+(?:on|in|for|during|at)\s+\w+", text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 3: Just extract everything except the last word (likely the date/time)
        words = text.split()
        if len(words) > 1:
            # Remove last word (likely the date/time reference)
            template = " ".join(words[:-1])
            if len(template) > 2:
                return template
        
        return None
    
    def rewrite_with_state(
        self,
        query: str,
        history: List[Dict[str, Any]],
        knowledge_base_name: Optional[str] = None,
        document_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Rewrite query using conversation history AND session state context.
        
        This version preserves KB and document context in rewrites.
        
        Args:
            query: Current user query
            history: List of previous messages
            knowledge_base_name: Current knowledge base name
            document_name: Current document name (from last retrieval)
            
        Returns:
            Dictionary with rewritten query and metadata
        """
        result = self.rewrite(query, history, knowledge_base_name)
        
        # Enhance rewrite with document/KB context
        rewritten = result.get("rewritten_query", query)
        rewrite_needed = result.get("rewrite_needed", False)
        
        if rewrite_needed or not result.get("rewrite_needed"):
            # For follow-ups without explicit rewrite, still add context
            # e.g., "And Tuesday?" -> "What is the sales revenue on Tuesday in Weekly_Sales_Report.pdf?"
            
            if document_name and not self._mentions_document(rewritten, document_name):
                # Add document context if it's a follow-up or clarification
                if self._is_contextual_query(rewritten):
                    rewritten = f"{rewritten} in {document_name}"
            
            if knowledge_base_name and not self._mentions_kb(rewritten, knowledge_base_name):
                # Add KB context if not already present
                if self._is_contextual_query(rewritten) and not document_name:
                    rewritten = f"{rewritten} in {knowledge_base_name}"
        
        # Only update if we added context
        if rewritten != result.get("rewritten_query"):
            result["rewritten_query"] = rewritten
            result["rewrite_needed"] = True
            if not result.get("rewrite_type"):
                result["rewrite_type"] = "context_enhanced"
        
        return result
    
    def _mentions_document(self, query: str, document_name: str) -> bool:
        """Check if query already mentions the document."""
        return document_name.lower() in query.lower()
    
    def _mentions_kb(self, query: str, kb_name: str) -> bool:
        """Check if query already mentions the KB."""
        return kb_name.lower() in query.lower()
    
    def _is_contextual_query(self, query: str) -> bool:
        """Check if query needs document/KB context (not a generic question)."""
        generic_questions = [
            "what is ai",
            "how does it work",
            "explain",
            "define",
        ]
        
        query_lower = query.lower()
        for generic in generic_questions:
            if query_lower.startswith(generic):
                return False
        
        return True
    
    def _get_last_user_message(self, history: List[Dict[str, Any]]) -> Optional[str]:
        """Get the last user message from history."""
        for msg in reversed(history):
            if msg.get("role") == "user":
                return msg.get("content")
        return None
    
    def _get_last_assistant_message(self, history: List[Dict[str, Any]]) -> Optional[str]:
        """Get the last assistant message from history."""
        for msg in reversed(history):
            if msg.get("role") == "assistant":
                return msg.get("content")
        return None


# Global rewriter instance
query_rewriter = QueryRewriter()


def get_query_rewriter() -> QueryRewriter:
    """Get the global query rewriter instance."""
    return query_rewriter
