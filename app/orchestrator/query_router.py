"""
Query Router - Intelligent Query Classification and Routing

Determines whether a query should be processed as:
1. Structured Query (CSV/Excel/Database)
2. Unstructured Query (PDF/Documents)
3. Hybrid Query (Both)

This is the critical component that enables the query agent to understand
query intent and route to the appropriate processing pipeline.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from app.db.models import StructuredFileSchema
from app.utils.logger import logger
import re


def route_query(query: str) -> str:
    """
    Simple route function that returns routing type.
    
    Args:
        query: User's natural language query
    
    Returns:
        "structured", "unstructured", "hybrid", or "unknown"
    """
    router = QueryRouter()
    result = router.route(query, has_structured_data=True, has_unstructured_data=True)
    return result["query_type"]


class QueryType(Enum):
    """Query classification types."""
    STRUCTURED = "structured"  # CSV, Excel, Database - requires SQL
    UNSTRUCTURED = "unstructured"  # PDF, Documents - semantic search
    HYBRID = "hybrid"  # Both - query both sources
    UNKNOWN = "unknown"


class QueryRouter:
    """
    Intelligent router that understands user intent and routes to appropriate processor.
    
    Key capabilities:
    1. Detect structured query patterns (aggregation, filtering, dates)
    2. Detect unstructured query patterns (semantic, keyword, document search)
    3. Understand ambiguous queries and make smart routing decisions
    4. Consider available data sources
    5. Fallback gracefully
    """
    
    # Structured query indicators
    STRUCTURED_KEYWORDS = {
        # Raw data retrieval
        'give me the data', 'show me the data', 'data on', 'data for', 'data of',
        'get me the data', "what's the data",
        
        # Aggregation queries
        'total', 'sum', 'count', 'average', 'avg', 'max', 'maximum', 'min', 'minimum',
        'highest', 'lowest', 'least', 'most', 'best', 'worst', 'top', 'bottom',
        
        # Date-based queries
        'on', 'date', 'day', 'month', 'year', 'when', 'which day', 'which date',
        'august', 'september', 'october', 'november', 'december', 'january',
        'february', 'march', 'april', 'may', 'june', 'july',
        
        # Analytical queries
        'breakdown', 'details', 'analysis', 'report', 'metrics', 'statistics',
        'how many', 'how much', 'what is', 'give me', 'show me', 'calculate',
        
        # Comparison queries
        'vs', 'versus', 'compared', 'difference', 'greater', 'less', 'between',
        'range', 'period', 'more', 'fewer',
        
        # Data-specific queries
        'product', 'revenue', 'sales', 'cost', 'price', 'quantity', 'units',
        'units sold', 'sold', 'purchased', 'stock',
    }
    
    # Unstructured query indicators
    UNSTRUCTURED_KEYWORDS = {
        # Document search
        'find', 'search', 'look', 'locate', 'where', 'what',
        'about', 'regarding', 'concerning', 'mention',
        
        # Content queries
        'content', 'text', 'section', 'page', 'paragraph', 'chapter',
        'document', 'file', 'article', 'paper', 'report', 'note',
        
        # Semantic queries
        'meaning', 'explain', 'describe', 'tell', 'what is', 'why',
        'how', 'which', 'who', 'list', 'summarize', 'summary',
        
        # Contextual queries
        'context', 'background', 'history', 'overview', 'introduction',
    }
    
    def __init__(self):
        """Initialize the query router."""
        self.logger = logger
    
    def route(
        self,
        query: str,
        has_structured_data: bool = False,
        has_unstructured_data: bool = False,
        structured_schemas: Optional[List[StructuredFileSchema]] = None,
        unstructured_schemas: Optional[List] = None,
    ) -> Dict[str, Any]:
        """
        Route a query to appropriate processor(s).
        
        Args:
            query: User's natural language query
            has_structured_data: Whether structured data (CSV/Excel/DB) is available
            has_unstructured_data: Whether unstructured data (PDF/Documents) is available
            structured_schemas: Available structured data schemas
            unstructured_schemas: Available unstructured data schemas
        
        Returns:
            {
                "query_type": QueryType,
                "confidence": float (0.0-1.0),
                "should_use_structured": bool,
                "should_use_unstructured": bool,
                "reasoning": str,
                "detected_intent": str,
                "potential_metrics": List[str],
                "potential_filters": Dict[str, Any],
            }
        """
        self.logger.info(f"Routing query: '{query}'")
        
        # Step 1: Analyze query text
        query_lower = query.lower()
        structured_score = self._calculate_structured_score(query_lower)
        unstructured_score = self._calculate_unstructured_score(query_lower)
        
        self.logger.debug(f"Scores - Structured: {structured_score:.2f}, Unstructured: {unstructured_score:.2f}")
        
        # Step 2: Classify query type
        query_type, confidence = self._classify_query(structured_score, unstructured_score)
        
        # Step 3: Determine routing decision
        should_use_structured, should_use_unstructured = self._make_routing_decision(
            query_type,
            has_structured_data,
            has_unstructured_data,
            structured_score,
            unstructured_score,
        )
        
        # Step 4: Extract intent and metadata
        intent = self._extract_intent(query_lower)
        metrics = self._extract_metrics(query_lower, structured_schemas)
        filters = self._extract_filters(query_lower)
        
        result = {
            "query_type": query_type.value,
            "confidence": confidence,
            "should_use_structured": should_use_structured,
            "should_use_unstructured": should_use_unstructured,
            "reasoning": self._generate_reasoning(
                query_type,
                confidence,
                has_structured_data,
                has_unstructured_data,
                structured_score,
                unstructured_score,
            ),
            "detected_intent": intent,
            "potential_metrics": metrics,
            "potential_filters": filters,
        }
        
        self.logger.info(f"Routing decision: {result['query_type']} (confidence: {confidence:.2f})")
        
        return result
    
    def _calculate_structured_score(self, query_lower: str) -> float:
        """Calculate how likely this is a structured query (0.0-1.0)."""
        score = 0.0
        
        # Check for structured keywords
        structured_matches = sum(
            1 for keyword in self.STRUCTURED_KEYWORDS 
            if keyword in query_lower
        )
        score += min(0.5, structured_matches * 0.1)
        
        # Check for date patterns (strong indicator of structured query)
        date_patterns = [
            r'\b\d{1,2}\b',  # Day numbers
            r'\b(august|september|october|november|december|january|february|march|april|may|june|july)\b',
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',  # Date format
            r'\b(on|between|from|to)\s+(.*?)\s+(and|to)\b',  # Date ranges
        ]
        for pattern in date_patterns:
            if re.search(pattern, query_lower):
                score += 0.15
                break
        
        # Check for numeric/metric patterns (strong indicator)
        if re.search(r'\b(how many|how much|total|sum|count|average)\b', query_lower):
            score += 0.2
        
        # Check for "which day/date" pattern (very strong structured indicator)
        if re.search(r'\b(which\s+(day|date)|which\s+\w+\s+(do|have|had))\b', query_lower):
            score += 0.3
        
        # Penalize if too many unstructured keywords
        unstructured_matches = sum(
            1 for keyword in self.UNSTRUCTURED_KEYWORDS 
            if keyword in query_lower
        )
        score -= min(0.2, unstructured_matches * 0.05)
        
        return min(1.0, max(0.0, score))
    
    def _calculate_unstructured_score(self, query_lower: str) -> float:
        """Calculate how likely this is an unstructured query (0.0-1.0)."""
        score = 0.0
        
        # Check for unstructured keywords
        unstructured_matches = sum(
            1 for keyword in self.UNSTRUCTURED_KEYWORDS 
            if keyword in query_lower
        )
        score += min(0.5, unstructured_matches * 0.1)
        
        # Check for content/semantic patterns
        if re.search(r'\b(explain|describe|tell|summarize|meaning|what is)\b', query_lower):
            score += 0.2
        
        # Check for document search patterns
        if re.search(r'\b(find|search|locate|mention|where)\b', query_lower):
            score += 0.15
        
        # Penalize if many structured keywords present
        structured_matches = sum(
            1 for keyword in self.STRUCTURED_KEYWORDS 
            if keyword in query_lower
        )
        score -= min(0.2, structured_matches * 0.05)
        
        return min(1.0, max(0.0, score))
    
    def _classify_query(self, structured_score: float, unstructured_score: float) -> tuple[QueryType, float]:
        """Classify query based on scores."""
        # Clear winner
        if structured_score > unstructured_score + 0.2:
            return QueryType.STRUCTURED, structured_score
        elif unstructured_score > structured_score + 0.2:
            return QueryType.UNSTRUCTURED, unstructured_score
        # Ambiguous - might need both
        elif structured_score > 0.4 and unstructured_score > 0.4:
            avg_score = (structured_score + unstructured_score) / 2
            return QueryType.HYBRID, avg_score
        # Very low scores - unknown
        elif structured_score < 0.2 and unstructured_score < 0.2:
            return QueryType.UNKNOWN, max(structured_score, unstructured_score)
        # Close call - use higher score
        else:
            if structured_score >= unstructured_score:
                return QueryType.STRUCTURED, structured_score
            else:
                return QueryType.UNSTRUCTURED, unstructured_score
    
    def _make_routing_decision(
        self,
        query_type: QueryType,
        has_structured_data: bool,
        has_unstructured_data: bool,
        structured_score: float,
        unstructured_score: float,
    ) -> tuple[bool, bool]:
        """Decide whether to route to structured and/or unstructured processors."""
        should_use_structured = False
        should_use_unstructured = False
        
        if query_type == QueryType.STRUCTURED:
            should_use_structured = has_structured_data
            # If structured data unavailable but unstructured exists, try it
            if not should_use_structured and has_unstructured_data:
                should_use_unstructured = True
        
        elif query_type == QueryType.UNSTRUCTURED:
            should_use_unstructured = has_unstructured_data
            # If unstructured data unavailable but structured exists, try it
            if not should_use_unstructured and has_structured_data:
                should_use_structured = True
        
        elif query_type == QueryType.HYBRID:
            # Try both if available
            should_use_structured = has_structured_data
            should_use_unstructured = has_unstructured_data
            
            # If only one available, use that
            if not has_structured_data and has_unstructured_data:
                should_use_unstructured = True
            elif not has_unstructured_data and has_structured_data:
                should_use_structured = True
        
        elif query_type == QueryType.UNKNOWN:
            # Unknown query - try to use available data
            should_use_structured = has_structured_data
            should_use_unstructured = has_unstructured_data
        
        return should_use_structured, should_use_unstructured
    
    def _extract_intent(self, query_lower: str) -> str:
        """Extract semantic intent from query."""
        intents = []
        
        if 'total' in query_lower or 'sum' in query_lower:
            intents.append("aggregate_sum")
        if 'how many' in query_lower or 'count' in query_lower:
            intents.append("count")
        if 'average' in query_lower or 'avg' in query_lower:
            intents.append("calculate_average")
        if 'highest' in query_lower or 'best' in query_lower or 'max' in query_lower:
            intents.append("find_maximum")
        if 'lowest' in query_lower or 'worst' in query_lower or 'min' in query_lower:
            intents.append("find_minimum")
        if 'which day' in query_lower or 'which date' in query_lower:
            intents.append("temporal_analysis")
        if 'details' in query_lower or 'breakdown' in query_lower:
            intents.append("detailed_analysis")
        if 'compare' in query_lower or 'vs' in query_lower:
            intents.append("comparison")
        if 'find' in query_lower or 'search' in query_lower:
            intents.append("semantic_search")
        if 'explain' in query_lower or 'describe' in query_lower:
            intents.append("explanation")
        
        return ",".join(intents) if intents else "unknown"
    
    def _extract_metrics(self, query_lower: str, schemas: Optional[List[StructuredFileSchema]] = None) -> List[str]:
        """Extract potential metric columns from query."""
        metrics = []
        
        # Common metric keywords
        metric_keywords = {
            'sales': ['Total Revenue', 'Revenue', 'Sales Amount', 'Total Sales'],
            'cost': ['Total Cost', 'Cost', 'Unit Cost', 'Cost Per Unit'],
            'revenue': ['Total Revenue', 'Revenue', 'Income'],
            'price': ['Price', 'Unit Price', 'Amount'],
            'units': ['Units', 'Units Sold', 'Quantity'],
            'profit': ['Profit', 'Net Profit', 'Gross Profit'],
            'amount': ['Total Amount', 'Amount'],
        }
        
        for keyword, cols in metric_keywords.items():
            if keyword in query_lower:
                metrics.extend(cols)
        
        # Also check available schemas for column names
        if schemas:
            for schema in schemas:
                if isinstance(schema.columns, list):
                    for col_meta in schema.columns:
                        if isinstance(col_meta, dict):
                            col_name = col_meta.get("original_name", "")
                            semantic_role = col_meta.get("semantic_role", "").lower()
                            if semantic_role == "metric" or any(kw in col_name.lower() for kw in metric_keywords.keys()):
                                if col_name not in metrics:
                                    metrics.append(col_name)
        
        return list(set(metrics))  # Remove duplicates
    
    def _extract_filters(self, query_lower: str) -> Dict[str, Any]:
        """Extract potential filter conditions from query."""
        filters = {}
        
        # Date filter
        date_match = re.search(
            r'\b(on|for|during|in|between)\s+(\w+\s+)?\d{1,2}',
            query_lower
        )
        if date_match:
            filters["date"] = "extracted"
        
        # Category filter
        category_keywords = ['product', 'category', 'type', 'region', 'department']
        for keyword in category_keywords:
            if keyword in query_lower:
                filters["category_type"] = keyword
                break
        
        # Range filter
        if 'between' in query_lower or 'range' in query_lower or 'from' in query_lower:
            filters["has_range"] = True
        
        return filters
    
    def _generate_reasoning(
        self,
        query_type: QueryType,
        confidence: float,
        has_structured: bool,
        has_unstructured: bool,
        structured_score: float,
        unstructured_score: float,
    ) -> str:
        """Generate human-readable reasoning for routing decision."""
        reasons = []
        
        reasons.append(f"Query classified as {query_type.value} (confidence: {confidence:.0%})")
        
        if query_type == QueryType.STRUCTURED:
            reasons.append("Contains aggregation/date/metric keywords typical of database queries")
        elif query_type == QueryType.UNSTRUCTURED:
            reasons.append("Contains semantic/search keywords typical of document queries")
        elif query_type == QueryType.HYBRID:
            reasons.append("Contains both structured and unstructured query indicators")
        
        if has_structured:
            reasons.append(f"Structured data available (score: {structured_score:.2f})")
        if has_unstructured:
            reasons.append(f"Unstructured data available (score: {unstructured_score:.2f})")
        
        if not has_structured and not has_unstructured:
            reasons.append("WARNING: No data sources available")
        
        return " → ".join(reasons)
