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
                "result": aggregation_value or full_row_for_groupby,
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
            
            # 3. Extract result based on operation type
            result_value = None
            if results and len(results) > 0:
                # For GROUP_BY, return entire row as dict so formatter can extract date
                if plan.operation.value == "GROUP_BY":
                    result_value = dict(results[0])  # Return full row as dict
                else:
                    # For aggregations, extract the aggregation result
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
            
            # Get original filename from upload relationship
            filename = "unknown"
            try:
                if hasattr(schema, 'upload') and schema.upload:
                    filename = schema.upload.original_filename or schema.upload.filename or "unknown"
            except Exception as e:
                logger.warning(f"Could not get filename for {upload_id}: {e}")
            
            sources.append({
                "filename": filename,
                "upload_id": str(upload_id),
            })
        
        logger.info(f"Built provenance with {len(sources)} sources: {sources}")
        return sources


    def execute_raw_sql(
    self,
    sql: str,
    schemas: List[StructuredFileSchema],
    metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """PHASE 8: Execute validated raw SQL from Qwen generator"""
        import time
        start = time.perf_counter()

        try:
            results = self.store.query(sql, {})
            result_value = results[0] if results and len(results) > 0 else None

            # Build clean sources list with filenames
            sources = []
            for s in schemas:
                filename = "unknown"
                try:
                    if hasattr(s, 'upload') and s.upload:
                        filename = s.upload.original_filename or s.upload.filename or "unknown"
                except Exception as e:
                    logger.warning(f"Could not get filename for {s.upload_id}: {e}")
                
                sources.append({
                    "filename": filename,
                    "upload_id": str(s.upload_id),
                })
            
            logger.info(f"Raw SQL execution succeeded with {len(sources)} sources: {sources}")

            return {
                "result": result_value,
                "sql": sql,
                "sources": sources,
                "status": "success",
                "query_time_ms": (time.perf_counter() - start) * 1000,
                **(metadata or {})
            }
        except Exception as e:
            logger.error(f"Raw SQL execution failed: {e}")
            return {"result": None, "error": str(e), "status": "error", "sql": sql}

        
        return sources
