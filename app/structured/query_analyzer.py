"""
PHASE 5.5: Query Analysis Agent

Parses natural language queries into structured analysis.
This layer sits between user query and SQL generator.

Goals:
1. Classify operation type (COUNT, SUM, AVG, MAX, MIN, GROUP BY)
2. Identify metrics and filter columns
3. Extract temporal filters (dates)
4. Determine aggregation scope
5. Pass structured plan to SQL generator
"""

from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field, asdict
from app.db.models import StructuredFileSchema
from app.llm.model_router import get_model
from app.utils.logger import logger
import json
import re


class OperationType(Enum):
    """Supported SQL operations."""
    COUNT = "COUNT"
    SUM = "SUM"
    AVG = "AVG"
    MAX = "MAX"
    MIN = "MIN"
    GROUP_BY = "GROUP_BY"
    DISTINCT = "DISTINCT"
    SELECT_ALL = "SELECT_ALL"  # NEW: Return all columns/rows without aggregation
    UNKNOWN = "UNKNOWN"


@dataclass
class FilterCondition:
    """Represents a WHERE clause condition."""
    column: str  # Physical column name
    operator: str  # "=", ">", "<", "LIKE", "IN", etc.
    value: Any
    semantic_role: Optional[str] = None  # "date", "category", etc.


@dataclass
class QueryAnalysis:
    """Structured analysis of a natural language query."""
    original_query: str
    operation: OperationType
    metrics: List[str] = field(default_factory=list)  # Physical column names
    group_by_columns: List[str] = field(default_factory=list)
    filters: List[FilterCondition] = field(default_factory=list)
    order_by: Optional[Dict[str, str]] = None  # {"column": "DESC"} or {"column": "ASC"}
    limit: Optional[int] = None
    semantic_intent: str = ""  # "find_best_sales_date", "total_revenue", etc.
    confidence: float = 1.0
    
    def to_dict(self):
        """Convert to dictionary for logging."""
        return {
            "original_query": self.original_query,
            "operation": self.operation.value,
            "metrics": self.metrics,
            "group_by": self.group_by_columns,
            "filters": [{"column": f.column, "op": f.operator, "value": f.value} for f in self.filters],
            "order_by": self.order_by,
            "limit": self.limit,
            "intent": self.semantic_intent,
            "confidence": self.confidence,
        }


class QueryAnalysisAgent:
    """
    Analyzes natural language queries to extract structured information.
    
    Uses LLM to classify queries and extract key components.
    """
    
    def __init__(self):
        """Initialize with LLM for query understanding."""
        self.llm = get_model("codegen")  # Use codegen model for structure extraction
    
    def analyze(
        self,
        query: str,
        schemas: List[StructuredFileSchema],
    ) -> QueryAnalysis:
        """
        Analyze a query and return structured analysis.
        
        Args:
            query: Natural language question
            schemas: Available schemas with column info
        
        Returns:
            QueryAnalysis object with operation, metrics, filters, etc.
        """
        logger.info(f"Analyzing query: '{query}'")
        
        # Build schema context for LLM
        schema_context = self._build_schema_context(schemas)
        
        # Generate analysis via LLM
        analysis_json = self._generate_analysis(query, schema_context)
        
        # Parse analysis
        analysis = self._parse_analysis(analysis_json, query, schemas)
        
        logger.info(f"Query analysis: {analysis.to_dict()}")
        
        return analysis
    
    def _build_schema_context(self, schemas: List[StructuredFileSchema]) -> str:
        """Build schema info for LLM."""
        context = "Available columns:\n\n"
        
        for schema in schemas:
            context += f"Table: {self._get_table_name(schema)}\n"
            
            columns_list = schema.columns if isinstance(schema.columns, list) else []
            
            for col_meta in columns_list:
                if isinstance(col_meta, dict):
                    col_name = col_meta.get("original_name", "unknown")
                    col_type = col_meta.get("data_type", "unknown")
                    semantic_role = col_meta.get("semantic_role", "unknown")
                    context += f"  - {col_name} ({col_type}) [role: {semantic_role}]\n"
        
        return context
    
    def _generate_analysis(self, query: str, schema_context: str) -> str:
        """Use LLM to analyze query structure."""
        prompt = f"""Analyze this database query and extract structured information.

{schema_context}

QUERY PATTERN RECOGNITION - MASTER REFERENCE:

RAW DATA RETRIEVAL QUERIES (show all columns):
- "give me the data of [DATE]" → Filter by DATE, return ALL columns (no aggregation)
- "show me the data for [DATE]" → Filter by DATE, return ALL columns (no aggregation)
- "data on [DATE]" → Filter by DATE, return ALL columns (no aggregation)
- "get me the data of [DATE]" → Filter by DATE, return ALL columns (no aggregation)
- "what's the data for [DATE]?" → Filter by DATE, return ALL columns (no aggregation)

DATE QUERIES (with specific date mentioned - aggregation):
- "cost/sales/revenue details on [DATE]" → Filter by DATE, SUM/MAX relevant metrics
- "cost/sales/revenue on [DATE]" → Filter by DATE, SUM/MAX relevant metrics
- "[METRIC] on [DATE]" → Filter by DATE, return metric value
- "how much [METRIC] on [DATE]?" → Filter by DATE, SUM/MAX relevant metrics
- "give me [METRIC] details on [DATE]" → Filter by DATE, detailed breakdown
- "what's the [METRIC] on [DATE]?" → Filter by DATE, exact value
- "find [METRIC] for [DATE]" → Filter by DATE, exact value

AGGREGATION QUERIES:
- "which day/date do best" → GROUP BY Date, MAX(metric), ORDER BY DESC, LIMIT 1
- "which day/date have best" → GROUP BY Date, MAX(metric), ORDER BY DESC, LIMIT 1
- "which day/date do worst" → GROUP BY Date, MIN(metric), ORDER BY ASC, LIMIT 1
- "best [METRIC]" → MAX operation with ORDER BY DESC
- "worst [METRIC]" → MIN operation with ORDER BY ASC
- "total/sum [METRIC]" → SUM operation
- "how many" → COUNT or SUM (depending on context)
- "average [METRIC]" → AVG operation
- "highest [METRIC]" → MAX operation
- "lowest [METRIC]" → MIN operation

BREAKDOWN/DETAIL QUERIES:
- "details on [DATE]" → Filter by DATE, show all metrics
- "breakdown of [METRIC]" → GROUP BY relevant column, show metric details
- "give me [info] on [DATE]" → Filter by DATE, detailed output

RETURN ONLY VALID JSON (no markdown, no explanation):
{{
  "operation": "SUM|COUNT|AVG|MAX|MIN|GROUP_BY|DISTINCT|SELECT_ALL",
  "metrics": ["Physical Column Names to aggregate - ALL relevant columns if SELECT_ALL"],
  "group_by": ["Columns to group by - especially Date for 'which day' queries"],
  "filters": [
    {{"column": "Physical Name", "operator": "=|>|<|LIKE|IN", "value": "value", "role": "date|category|etc"}}
  ],
  "order_by": {{"column": "Physical Name", "direction": "ASC|DESC"}},
  "limit": null,
  "semantic_intent": "brief description of what user wants",
  "date_filter": {{"column": "Date column name", "values": ["exact dates or month-day patterns"]}}
}}

CRITICAL RULES:
1. If query contains "give me the data" or "show me the data" → Use SELECT_ALL operation (no aggregation)
2. For SELECT_ALL operation → Include ALL available columns in metrics list
3. If query mentions a DATE → Add date filter with LIKE operator
4. For "[METRIC] details on [DATE]" → Filter by date AND include ALL relevant metrics
5. For date queries without explicit aggregation → Use SUM for costs/revenue
6. For "which day" queries → Must use GROUP_BY operation with ORDER BY
7. Always extract ALL metric columns mentioned or implied in the query
8. Date values can be "august 29", "08-29", "29", "august", etc.

EXAMPLES:
User Query: "Total cost ?"
JSON: {{"operation": "SUM", "metrics": ["Total Cost"], "filters": [], "semantic_intent": "get total cost"}}

User Query: "give me the data of august 18"
JSON: {{"operation": "SELECT_ALL", "metrics": ["Date", "Day", "How Many", "Total Revenue", "Total Cost", "Total Profit"], "filters": [{{"column": "Date", "operator": "LIKE", "value": "%18%"}}], "date_filter": {{"column": "Date", "values": ["august 18", "18"]}}, "semantic_intent": "get all data for august 18"}}

User Query: "give me cost details on august 29 ?"
JSON: {{"operation": "SUM", "metrics": ["Total Cost", "Unit Cost", "Cost"], "filters": [{{"column": "Date", "operator": "LIKE", "value": "%29%"}}], "date_filter": {{"column": "Date", "values": ["august 29", "29"]}}, "semantic_intent": "get cost details for august 29"}}

User Query: "which day have best sales?"
JSON: {{"operation": "GROUP_BY", "metrics": ["Total Revenue", "Revenue"], "group_by": ["Date"], "order_by": {{"column": "Total Revenue", "direction": "DESC"}}, "limit": 1, "semantic_intent": "find the day with highest sales"}}

User Query: "{query}"

JSON (start with {{):"""
        
        try:
            response = self.llm.generate(prompt)
            raw_response = response.answer.strip()
            logger.debug(f"Raw LLM analysis response (first 300 chars): {raw_response[:300]}")
            return raw_response
        except Exception as e:
            logger.error(f"Analysis generation failed: {e}")
            return "{}"
    
    def _parse_analysis(
        self,
        analysis_json: str,
        original_query: str,
        schemas: List[StructuredFileSchema],
    ) -> QueryAnalysis:
        """Parse LLM-generated analysis into structured form."""
        
        try:
            # Extract JSON - find opening { and match braces to find closing }
            start_idx = analysis_json.find('{')
            if start_idx == -1:
                logger.debug(f"No opening brace found in analysis response: {analysis_json[:200]}")
                data = {}
            else:
                # Find matching closing brace
                brace_count = 0
                end_idx = start_idx
                for i in range(start_idx, len(analysis_json)):
                    if analysis_json[i] == '{':
                        brace_count += 1
                    elif analysis_json[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                
                json_str = analysis_json[start_idx:end_idx]
                logger.debug(f"Extracted JSON string (length {len(json_str)}): {json_str[:500]}")
                data = json.loads(json_str)
                logger.debug(f"Successfully parsed analysis JSON: {data}")
        except Exception as e:
            logger.warning(f"Failed to parse analysis JSON: {e}\nRaw response (first 500 chars): {analysis_json[:500]}")
            data = {}
        
        # Map operation
        op_str = data.get("operation", "UNKNOWN").upper()
        try:
            operation = OperationType[op_str]
        except KeyError:
            operation = OperationType.UNKNOWN
        
        # Build filters from analysis
        filters = []
        if "filters" in data:
            for f in data["filters"]:
                if isinstance(f, dict):
                    filters.append(FilterCondition(
                        column=f.get("column", ""),
                        operator=f.get("operator", "="),
                        value=f.get("value"),
                        semantic_role=f.get("role"),
                    ))
        
        # Handle date filters specially - MORE ROBUST DATE EXTRACTION
        date_filter_info = data.get("date_filter", {})
        if date_filter_info and date_filter_info.get("values"):
            date_col = date_filter_info.get("column", "Date")
            for date_val in date_filter_info["values"]:
                # Convert "august 29" or "08-29" to LIKE pattern
                # Extract numeric parts for flexible matching
                numeric_parts = re.findall(r'\d+', str(date_val))
                
                if numeric_parts:
                    # If we have numbers like "29", create patterns for day matching
                    for num_part in numeric_parts:
                        filters.append(FilterCondition(
                            column=date_col,
                            operator="LIKE",
                            value=f"%{num_part}%",  # Flexible pattern matching
                            semantic_role="date",
                        ))
                else:
                    # Fall back to literal matching if no numbers
                    filters.append(FilterCondition(
                        column=date_col,
                        operator="LIKE",
                        value=f"%{date_val}%",
                        semantic_role="date",
                    ))
        
        # IMPORTANT: Also try to extract dates from original query as fallback
        if not date_filter_info or not date_filter_info.get("values"):
            date_col = "Date"  # Default date column name
            extracted_dates = self._extract_dates_from_query_text(original_query)
            for date_val in extracted_dates:
                filters.append(FilterCondition(
                    column=date_col,
                    operator="LIKE",
                    value=f"%{date_val}%",
                    semantic_role="date",
                ))
                logger.info(f"Extracted date from query text: {date_val}")
        
        # Order by
        order_by = None
        if "order_by" in data and isinstance(data["order_by"], dict):
            order_by = {
                data["order_by"].get("column"): data["order_by"].get("direction", "DESC")
            }
        
        return QueryAnalysis(
            original_query=original_query,
            operation=operation,
            metrics=data.get("metrics", []),
            group_by_columns=data.get("group_by", []),
            filters=filters,
            order_by=order_by,
            limit=data.get("limit"),
            semantic_intent=data.get("semantic_intent", ""),
            confidence=0.95,  # LLM-based analysis
        )
    
    def _extract_dates_from_query_text(self, query: str) -> List[str]:
        """Extract date patterns from query text as fallback."""
        dates = []
        query_lower = query.lower()
        
        # Month names and their numbers
        months = {
            'january': '01', 'jan': '01',
            'february': '02', 'feb': '02',
            'march': '03', 'mar': '03',
            'april': '04', 'apr': '04',
            'may': '05',
            'june': '06', 'jun': '06',
            'july': '07', 'jul': '07',
            'august': '08', 'aug': '08',
            'september': '09', 'sep': '09',
            'october': '10', 'oct': '10',
            'november': '11', 'nov': '11',
            'december': '12', 'dec': '12',
        }
        
        # Extract explicit dates like "august 29"
        for month_name, month_num in months.items():
            if month_name in query_lower:
                # Look for day number after month
                pattern = rf'{month_name}\s+(\d+)'
                matches = re.finditer(pattern, query_lower)
                for match in matches:
                    day = match.group(1).zfill(2)
                    dates.append(day)  # Extract just the day
                    logger.info(f"Found date pattern: {month_name} {day}")
        
        # Extract numeric dates like "29" (day of month)
        numeric_dates = re.findall(r'\b(\d{1,2})\b', query)
        for num_date in numeric_dates:
            if 1 <= int(num_date) <= 31:  # Valid day range
                dates.append(num_date)
        
        return list(set(dates))  # Remove duplicates
    
    def _get_table_name(self, schema: StructuredFileSchema) -> str:
        """Get table name from schema."""
        try:
            kb_short = str(schema.knowledge_base_id).replace('-', '')[:8]
            upload_short = str(schema.upload_id).replace('-', '')[:8]
            sheet_suffix = f"_{schema.sheet_name}" if schema.sheet_name else ""
            return f"kb_{kb_short}_upload_{upload_short}{sheet_suffix}"
        except Exception:
            return "unknown_table"
