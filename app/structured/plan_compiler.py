"""
PHASE 6: Plan-to-SQL Compiler

Converts validated QueryPlan → parameterized DuckDB SQL

CRITICAL SAFETY RULES:
1. Only whitelisted operations (SUM/COUNT/AVG/MIN/MAX/GROUP BY/FILTER/ORDER BY)
2. Resolve semantic fields to physical columns via column_resolver
3. Return parameterized SQL (no string interpolation)
4. Reject anything outside whitelist with ValueError
"""

from typing import Any, Dict, List, Optional, Tuple
import re
from app.structured.query_planner import QueryPlan, QueryOperation, DateOperator
from app.structured.column_resolver import resolve_semantic_column
from app.structured.schema_discovery import SemanticRole
from app.db.models import StructuredFileSchema
from app.utils.logger import logger


class SafeSQLCompiler:
    """
    Compiles validated query plans to safe, parameterized SQL.
    
    Output format: (sql_string, params_dict)
    - sql_string uses ? for parameters
    - params_dict maps parameter names to values
    """
    
    def __init__(self):
        """Initialize compiler."""
        pass
    
    def compile(
        self,
        plan: QueryPlan,
        schemas: Dict[str, StructuredFileSchema],
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Compile a QueryPlan to SQL.
        
        Args:
            plan: Validated QueryPlan
            schemas: Dict mapping upload_id→StructuredFileSchema
        
        Returns:
            (sql_string, params_dict) for parameterized execution
        
        Raises:
            ValueError: If plan outside whitelist or resolution fails
        """
        logger.info(f"Compiling plan: {plan.operation.value}")
        
        # Validate operation is whitelisted
        allowed_ops = {
            QueryOperation.SUM,
            QueryOperation.COUNT,
            QueryOperation.AVG,
            QueryOperation.MIN,
            QueryOperation.MAX,
        }
        
        if plan.operation not in allowed_ops:
            raise ValueError(f"Operation not whitelisted: {plan.operation}")
        
        # Build SELECT clause based on operation
        select_clause = self._build_select(plan)
        
        # Build FROM clause (UNION across compatible uploads)
        from_clause, table_list = self._build_from(plan, schemas)
        
        # Build WHERE clause (date filters)
        where_clause, params = self._build_where(plan, schemas)
        
        # Combine into final SQL
        sql = f"{select_clause}\n{from_clause}"
        if where_clause:
            sql += f"\n{where_clause}"
        
        logger.debug(f"Compiled SQL:\n{sql}\nParams: {params}")
        return sql, params
    
    def _build_select(self, plan: QueryPlan) -> str:
        """Build SELECT clause."""
        if plan.operation == QueryOperation.COUNT:
            return "SELECT COUNT(*) AS result"
        elif plan.operation == QueryOperation.SUM:
            return "SELECT SUM(metric_value) AS result"
        elif plan.operation == QueryOperation.AVG:
            return "SELECT AVG(metric_value) AS result"
        elif plan.operation == QueryOperation.MIN:
            return "SELECT MIN(metric_value) AS result"
        elif plan.operation == QueryOperation.MAX:
            return "SELECT MAX(metric_value) AS result"
        else:
            raise ValueError(f"Unknown operation: {plan.operation}")
    
    def _build_from(
        self,
        plan: QueryPlan,
        schemas: Dict[str, StructuredFileSchema],
    ) -> Tuple[str, List[str]]:
        """
        Build FROM clause with UNION of compatible tables.
        
        Each table SELECT-aliased to canonical schema columns:
        - metric_value (from resolved metric column)
        - date_value (from resolved date column, if filtering)
        """
        selects = []
        table_list = []
        
        for upload_id in plan.candidate_uploads:
            schema = schemas.get(upload_id)
            if not schema:
                logger.warning(f"Schema not found for upload {upload_id}")
                continue
            
            # Resolve metric column
            metric_col = resolve_semantic_column(plan.semantic_metric, schema)
            if not metric_col:
                logger.warning(f"Cannot resolve metric in upload {upload_id}")
                continue
            
            # Resolve date column if filtering
            date_col = None
            if plan.date_filter:
                date_col = resolve_semantic_column(SemanticRole.DATE, schema)
            
            # Get table name
            table_name = self._get_table_name(upload_id, schema)
            if not table_name:
                continue
            
            table_list.append(table_name)
            
            # Build per-table SELECT with column aliasing
            if date_col:
                select = f"SELECT {metric_col} AS metric_value, {date_col} AS date_value FROM {table_name}"
            else:
                select = f"SELECT {metric_col} AS metric_value FROM {table_name}"
            
            selects.append(select)
        
        if not selects:
            raise ValueError("No compatible tables found")
        
        # Union all selects
        from_clause = "\nUNION ALL\n".join(selects)
        
        return from_clause, table_list
    
    def _build_where(
        self,
        plan: QueryPlan,
        schemas: Dict[str, StructuredFileSchema],
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Build WHERE clause for date filtering.
        
        Uses parameterized queries (no string interpolation).
        """
        if not plan.date_filter:
            return "", {}
        
        params = {}
        conditions = []
        
        # Check operator
        operator = plan.date_filter.get("operator")
        
        if operator == DateOperator.EQUALS.value:
            # WHERE date_value = ?
            params["filter_date"] = plan.date_filter.get("value")
            conditions.append("date_value = ?")
        
        elif operator == DateOperator.BETWEEN.value:
            # WHERE date_value BETWEEN ? AND ?
            params["start_date"] = plan.date_filter.get("start")
            params["end_date"] = plan.date_filter.get("end")
            conditions.append("date_value BETWEEN ? AND ?")
        
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
            return where_clause, params
        
        return "", {}
    
    def _get_table_name(self, upload_id: str, schema: StructuredFileSchema) -> Optional[str]:
        """
        Get DuckDB table name for this upload.
        
        Convention: kb_{kb_short}_upload_{upload_short}[_sheet]
        """
        try:
            kb_short = str(schema.knowledge_base_id).replace('-', '')[:8]
            upload_short = str(upload_id).replace('-', '')[:8]
            sheet_suffix = f"_{schema.sheet_name}" if schema.sheet_name else ""
            return f"kb_{kb_short}_upload_{upload_short}{sheet_suffix}"
        except Exception as e:
            logger.warning(f"Could not generate table name: {e}")
            return None
