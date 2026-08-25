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
                # For MIN/MAX, also try to fetch the full row with that value
                elif plan.operation.value in ["MIN", "MAX"]:
                    agg_value = results[0].get("result")
                    result_value = agg_value
                    # Try to fetch full row that has this value
                    try:
                        logger.info(f"Fetching full row for {plan.operation.value} value: {agg_value}")
                        full_row = self._fetch_full_row_for_value(plan, schemas, agg_value)
                        if full_row:
                            logger.info(f"Got full row: {full_row}")
                            result_value = full_row
                        else:
                            logger.info(f"No full row found for {plan.operation.value}")
                    except Exception as e:
                        logger.warning(f"Could not fetch full row for {plan.operation.value}: {e}")
                else:
                    # For other aggregations, extract the aggregation result
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
    
    def _fetch_full_row_for_value(
        self,
        plan: QueryPlan,
        schemas: Dict[str, StructuredFileSchema],
        agg_value: Any,
    ) -> Optional[Dict[str, Any]]:
        """Fetch the full row that contains the min/max value."""
        from app.structured.column_resolver import resolve_semantic_column
        
        try:
            # Find the metric column across all tables
            for upload_id in plan.candidate_uploads:
                schema = schemas.get(upload_id)
                if not schema:
                    continue
                
                metric_col = resolve_semantic_column(plan.semantic_metric, schema)
                if not metric_col:
                    logger.warning(f"Could not resolve metric column for {plan.semantic_metric}")
                    continue
                
                table_name = self._get_table_name(upload_id, schema)
                if not table_name:
                    logger.warning(f"Could not get table name for {upload_id}")
                    continue
                
                try:
                    # For MIN/MAX, use ORDER BY to get the row with min/max value
                    # This handles floating point precision issues better than exact matching
                    if plan.operation.value == "MIN":
                        sql = f"SELECT * FROM {table_name} ORDER BY {metric_col} ASC LIMIT 1"
                    else:  # MAX
                        sql = f"SELECT * FROM {table_name} ORDER BY {metric_col} DESC LIMIT 1"
                    
                    logger.info(f"Fetching full row with SQL: {sql}")
                    # Execute without parameters for ORDER BY queries
                    result = self.store.conn.execute(sql).fetchall()
                    if result and len(result) > 0:
                        # Convert to dict
                        columns = [desc[0] for desc in self.store.conn.description]
                        row_dict = dict(zip(columns, result[0]))
                        logger.info(f"Fetched full row for {plan.operation.value}: {row_dict}")
                        return row_dict
                except Exception as e:
                    logger.warning(f"Failed to fetch full row from {table_name}: {e}")
                    continue
            
            logger.warning(f"Could not fetch full row for {plan.operation.value} value {agg_value} from any upload")
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch full row: {e}")
            return None
    
    def _get_table_name(self, upload_id: Any, schema: StructuredFileSchema) -> Optional[str]:
        """Get DuckDB table name for an upload."""
        try:
            from uuid import UUID
            if isinstance(upload_id, str):
                upload_id = UUID(upload_id)
            elif not isinstance(upload_id, UUID):
                upload_id = UUID(str(upload_id))
            
            kb_id = schema.knowledge_base_id
            if isinstance(kb_id, str):
                kb_id = UUID(kb_id)
            elif not isinstance(kb_id, UUID):
                kb_id = UUID(str(kb_id))
            
            kb_short = str(kb_id).replace('-', '')[:8]
            upload_short = str(upload_id).replace('-', '')[:8]
            sheet_suffix = f"_{schema.sheet_name}" if hasattr(schema, 'sheet_name') and schema.sheet_name else ""
            return f"kb_{kb_short}_upload_{upload_short}{sheet_suffix}"
        except Exception as e:
            logger.warning(f"Could not build table name for {upload_id}: {e}")
            return None
    
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
