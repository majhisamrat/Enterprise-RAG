"""
PHASE 7: Structured Query Executor

Executes validated query plans via DuckDB.
Returns results with full provenance (which files contributed, which columns mapped).
"""

from typing import Any, Dict, List, Optional
import uuid
from app.structured.query_planner import QueryPlan
from app.structured.plan_compiler import SafeSQLCompiler
from app.structured.duckdb_store import StructuredDataStore
from app.structured.column_resolver import resolve_semantic_column
from app.db.models import StructuredFileSchema
from app.utils.logger import logger


class StructuredQueryExecutor:
    """Executes compiled query plans and returns results with provenance."""
    
    def __init__(self):
        self.compiler = SafeSQLCompiler()
        self.store = StructuredDataStore()
    
    def execute(
        self,
        plan: QueryPlan,
        schemas: Dict[str, StructuredFileSchema],
    ) -> Dict[str, Any]:
        """
        Execute a query plan.
        
        Args:
            plan: Validated QueryPlan
            schemas: Dict mapping upload_id→StructuredFileSchema
        
        Returns:
            {
                "result": aggregation_value,
                "operation": "SUM" (etc),
                "semantic_metric": "quantity",
                "sources": [
                    {
                        "upload_id": "...",
                        "filename": "sales1.csv",
                        "physical_metric": "Quantity",
                        "rows_matched": 1,
                    },
                    ...
                ],
                "query_time_ms": 123,
            }
        """
        logger.info(f"Executing plan: {plan.operation.value}")
        
        try:
            # 1. Compile plan to SQL
            sql, params = self.compiler.compile(plan, schemas)
            
            # 2. Execute via DuckDB
            results = self.store.query(sql, params)
            
            # 3. Extract result
            result_value = None
            if results and len(results) > 0:
                result_value = results[0].get("result")
            
            # 4. Build provenance
            sources = self._build_provenance(plan, schemas)
            
            # 5. Return with metadata
            return {
                "result": result_value,
                "operation": plan.operation.value,
                "semantic_metric": plan.semantic_metric.value if plan.semantic_metric else None,
                "sources": sources,
                "status": "success",
            }
        
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {
                "result": None,
                "operation": plan.operation.value,
                "error": str(e),
                "status": "error",
            }
    
    def _build_provenance(
        self,
        plan: QueryPlan,
        schemas: Dict[str, StructuredFileSchema],
    ) -> List[Dict[str, Any]]:
        """Build source attribution for results."""
        sources = []
        
        for upload_id in plan.candidate_uploads:
            schema = schemas.get(upload_id)
            if not schema:
                continue
            
            # Get original filename
            filename = "unknown"
            if schema.upload:
                filename = schema.upload.original_filename or "unknown"
            
            # Get physical metric column
            physical_metric = None
            if plan.semantic_metric:
                physical_metric = resolve_semantic_column(plan.semantic_metric, schema)
            
            sources.append({
                "upload_id": str(upload_id),
                "filename": filename,
                "semantic_metric": plan.semantic_metric.value if plan.semantic_metric else None,
                "physical_metric": physical_metric,
                "sheet_name": schema.sheet_name,
                "schema_version": schema.schema_version,
            })
        
        return sources
