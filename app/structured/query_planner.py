"""
PHASE 5: Schema-Aware Query Planner

Input: Rewritten query (from protected Query Rewriter) + available schemas in KB scope
Output: Validated JSON query plan (never raw SQL)

Whitelisted operations only: SUM, COUNT, AVG, MIN, MAX, GROUP BY, FILTER, ORDER BY

Safety: No LLM-generated SQL ever executes. Only structured plans compiled to safe SQL.
"""

import json
import re
from typing import Any, Dict, List, Optional
from enum import Enum
from app.structured.schema_discovery import SemanticRole
from app.db.models import StructuredFileSchema
from app.utils.logger import logger


class QueryOperation(str, Enum):
    """Whitelisted operations only."""
    SUM = "SUM"
    COUNT = "COUNT"
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"
    GROUP_BY = "GROUP_BY"
    FILTER = "FILTER"
    ORDER_BY = "ORDER_BY"


class DateOperator(str, Enum):
    """Date filter operators."""
    EQUALS = "EQUALS"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    BETWEEN = "BETWEEN"


class QueryPlan:
    """Validated query plan (safe, unambiguous)."""
    
    def __init__(
        self,
        operation: QueryOperation,
        semantic_metric: Optional[SemanticRole] = None,
        semantic_date: Optional[SemanticRole] = None,
        semantic_group_by: Optional[SemanticRole] = None,
        date_filter: Optional[Dict[str, Any]] = None,
        candidate_uploads: Optional[List[str]] = None,
    ):
        self.operation = operation
        self.semantic_metric = semantic_metric
        self.semantic_date = semantic_date
        self.semantic_group_by = semantic_group_by
        self.date_filter = date_filter
        self.candidate_uploads = candidate_uploads or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "operation": self.operation.value,
            "semantic_metric": self.semantic_metric.value if self.semantic_metric else None,
            "semantic_date": self.semantic_date.value if self.semantic_date else None,
            "semantic_group_by": self.semantic_group_by.value if self.semantic_group_by else None,
            "date_filter": self.date_filter,
            "candidate_uploads": self.candidate_uploads,
        }


class SchemaAwareQueryPlanner:
    """
    Plans structured queries from natural language.
    
    Strategy:
    1. Detect aggregation intent (SUM/COUNT/AVG/MIN/MAX)
    2. Identify semantic metric column
    3. Detect date filters
    4. Select compatible datasets from KB
    5. Build validated plan (never raw SQL)
    """
    
    # Aggregation patterns
    SUM_PATTERNS = [r"\bhow\s+much\b", r"\btotal\b", r"\bsum\b", r"\bsales\b"]
    COUNT_PATTERNS = [r"\bhow\s+many\b", r"\bcount\b", r"\bnumber\b", r"\bquantity\b"]
    AVG_PATTERNS = [r"\baverage\b", r"\bavg\b", r"\bmean\b"]
    MIN_PATTERNS = [r"\bminimum\b", r"\bmin\b", r"\blowest\b", r"\bleast\b"]
    MAX_PATTERNS = [r"\bmaximum\b", r"\bmax\b", r"\bhighest\b", r"\bmost\b"]
    
    # Metric keyword mapping
    METRIC_KEYWORDS = {
        SemanticRole.QUANTITY: [r"\bquantity\b", r"\bunits\b", r"\bsold\b", r"\bproducts?\b"],
        SemanticRole.REVENUE: [r"\brevenue\b", r"\bsales\b", r"\bincome\b", r"\bturnovere\b"],
        SemanticRole.COST: [r"\bcost\b", r"\bexpense\b", r"\bcogs\b"],
        SemanticRole.PRICE: [r"\bprice\b", r"\brate\b"],
        SemanticRole.PROFIT: [r"\bprofit\b", r"\bearnings\b"],
    }
    
    def __init__(self):
        """Initialize planner."""
        self.confidence_threshold = 0.7
    
    def plan(
        self,
        query: str,
        available_schemas: List[StructuredFileSchema],
    ) -> Optional[QueryPlan]:
        """
        Plan a structured query.
        
        Args:
            query: Rewritten query from Query Rewriter
            available_schemas: StructuredFileSchema records for KB
        
        Returns:
            QueryPlan if structured intent detected, else None
        """
        logger.info(f"Planning query: '{query}'")
        
        # 1. Detect aggregation operation
        operation = self._detect_operation(query)
        if operation is None:
            logger.debug("No aggregation intent detected → semantic route")
            return None
        
        # 2. Detect semantic metric
        metric = self._detect_metric(query)
        if metric is None:
            logger.debug(f"No metric detected for operation {operation} → fallback to semantic")
            return None
        
        # 3. Detect date filter
        date_filter = self._detect_date_filter(query)
        
        # 4. Select compatible uploads
        compatible_uploads = self._select_compatible_uploads(
            available_schemas, metric
        )
        
        if not compatible_uploads:
            logger.debug(f"No datasets have metric {metric.value} → semantic route")
            return None
        
        # 5. Build plan
        plan = QueryPlan(
            operation=operation,
            semantic_metric=metric,
            semantic_date=SemanticRole.DATE,  # Always try to filter by date
            date_filter=date_filter,
            candidate_uploads=compatible_uploads,
        )
        
        logger.success(f"Query plan: {operation.value} of {metric.value}")
        return plan
    
    def _detect_operation(self, query: str) -> Optional[QueryOperation]:
        """Detect aggregation operation from query."""
        query_lower = query.lower()
        
        for pattern in self.SUM_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryOperation.SUM
        
        for pattern in self.COUNT_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryOperation.COUNT
        
        for pattern in self.AVG_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryOperation.AVG
        
        for pattern in self.MIN_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryOperation.MIN
        
        for pattern in self.MAX_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryOperation.MAX
        
        return None
    
    def _detect_metric(self, query: str) -> Optional[SemanticRole]:
        """Detect which metric column the query is asking about."""
        query_lower = query.lower()
        
        for role, keywords in self.METRIC_KEYWORDS.items():
            for keyword in keywords:
                if re.search(keyword, query_lower):
                    logger.debug(f"Detected metric: {role.value}")
                    return role
        
        return None
    
    def _detect_date_filter(self, query: str) -> Optional[Dict[str, Any]]:
        """Detect date filters in query with resolution of ambiguous dates."""
        from datetime import datetime
        
        # Simple patterns for common date queries
        
        # "on August 15" or "on 15-08-26" or "august 8"
        date_match = re.search(r"(?:on\s+)?(\w+\s+\d+|\d+-\d+-\d+)", query, re.IGNORECASE)
        if date_match:
            date_str = date_match.group(1).strip()
            resolved_date = self._resolve_date(date_str, query)
            if resolved_date:
                return {
                    "operator": DateOperator.EQUALS.value,
                    "value": resolved_date,
                    "original": date_str,
                }
        
        # "from X to Y" (date range)
        range_match = re.search(
            r"from\s+([^t]+?)\s+to\s+(.+?)(?:\?|$)",
            query,
            re.IGNORECASE,
        )
        if range_match:
            start_date = range_match.group(1).strip()
            end_date = range_match.group(2).strip()
            return {
                "operator": DateOperator.BETWEEN.value,
                "start": self._resolve_date(start_date, query),
                "end": self._resolve_date(end_date, query),
            }
        
        return None
    
    def _resolve_date(self, date_str: str, context_query: str) -> Optional[str]:
        """
        Resolve ambiguous dates to ISO format (YYYY-MM-DD).
        
        Examples:
        - "August 8" → "2026-08-08" (assuming current year from context)
        - "08-08-26" → "2026-08-08" (YY assumed from context)
        - "8/8" → "2026-08-08"
        
        Strategy:
        1. Try parsing with common patterns
        2. If month/day without year: infer year from context (default to 2026 for this system)
        3. If ambiguous YY format: assume 20xx
        
        Args:
            date_str: Date string to resolve
            context_query: Full query for context clues
        
        Returns:
            ISO date string (YYYY-MM-DD) or None if unresolvable
        """
        from datetime import datetime
        import dateutil.parser as dateparser
        
        # Clean the input
        date_str = date_str.strip().lower()
        
        # Extract year hint from context if present
        year_match = re.search(r'\b(20\d{2})\b', context_query)
        context_year = int(year_match.group(1)) if year_match else 2026  # Default to 2026
        
        try:
            # Try parsing with dateutil (handles many formats)
            parsed = dateparser.parse(date_str, default=datetime(context_year, 1, 1))
            if parsed:
                # If only month/day provided, dateutil uses default year
                # Check if we need to override year
                if parsed.year == 1900 or len(date_str) < 6:  # Short format without year
                    parsed = parsed.replace(year=context_year)
                
                return parsed.strftime("%Y-%m-%d")
        except Exception as e:
            logger.debug(f"Date parsing failed for '{date_str}': {e}")
        
        # Manual pattern matching as fallback
        
        # Pattern: "Month Day" (e.g., "August 8", "aug 15")
        month_day_match = re.match(r'(\w+)\s+(\d+)', date_str)
        if month_day_match:
            month_str = month_day_match.group(1)
            day = int(month_day_match.group(2))
            
            month_map = {
                'jan': 1, 'january': 1,
                'feb': 2, 'february': 2,
                'mar': 3, 'march': 3,
                'apr': 4, 'april': 4,
                'may': 5,
                'jun': 6, 'june': 6,
                'jul': 7, 'july': 7,
                'aug': 8, 'august': 8,
                'sep': 9, 'sept': 9, 'september': 9,
                'oct': 10, 'october': 10,
                'nov': 11, 'november': 11,
                'dec': 12, 'december': 12,
            }
            
            month = month_map.get(month_str[:3])
            if month:
                try:
                    date_obj = datetime(context_year, month, day)
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    pass
        
        # Pattern: "M/D" or "M-D" (e.g., "8/8", "08-08")
        slash_date = re.match(r'(\d{1,2})[/-](\d{1,2})$', date_str)
        if slash_date:
            month = int(slash_date.group(1))
            day = int(slash_date.group(2))
            try:
                date_obj = datetime(context_year, month, day)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        # Pattern: "YY-MM-DD" or "YY/MM/DD" (e.g., "26-08-08")
        yy_date = re.match(r'(\d{2})[/-](\d{1,2})[/-](\d{1,2})$', date_str)
        if yy_date:
            yy = int(yy_date.group(1))
            mm = int(yy_date.group(2))
            dd = int(yy_date.group(3))
            
            # Assume 20xx for years 00-99
            yyyy = 2000 + yy
            
            try:
                date_obj = datetime(yyyy, mm, dd)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        logger.warning(f"Could not resolve date: '{date_str}'")
        return None
    
    def _select_compatible_uploads(
        self,
        available_schemas: List[StructuredFileSchema],
        metric: SemanticRole,
    ) -> List[str]:
        """
        Select uploads that have the required metric.
        
        Incompatible datasets (missing metric) are excluded.
        """
        from app.structured.column_resolver import resolve_semantic_column
        
        compatible = []
        
        for schema in available_schemas:
            # Check if this schema has the metric column
            col_name = resolve_semantic_column(metric, schema)
            if col_name is not None:
                compatible.append(str(schema.upload_id))
                logger.debug(f"Upload {schema.upload_id} is compatible (has {metric.value})")
            else:
                logger.debug(f"Upload {schema.upload_id} incompatible (missing {metric.value})")
        
        return compatible
