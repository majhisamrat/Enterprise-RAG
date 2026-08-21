"""
PHASE 3: DuckDB Structured Data Store

Per-tenant OLAP storage for CSV/XLSX row data.
Enables fast SUM/AVG/COUNT/GROUP BY queries without vector DB.

Design:
- One DuckDB database per knowledge base (or global with table namespacing)
- Table naming: kb_{kb_id}_upload_{upload_id}
- Supports parameterized queries only (no raw LLM SQL)
"""

import uuid
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import duckdb
from app.config import settings
from app.utils.logger import logger


class StructuredDataStore:
    """
    OLAP data store using DuckDB.
    
    Lifecycle:
    1. write_table(upload_id, kb_id, dataframe) → creates table, returns table_name
    2. query(sql, params) → executes parameterized query
    3. delete_table(table_name) → removes table (on re-ingest)
    """
    
    def __init__(self):
        """Initialize DuckDB connection manager."""
        self.db_dir = Path(settings.DUCKDB_PATH or "data/duckdb")
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_dir / "structured_data.duckdb"
        self._conn = None
    
    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """Lazy-load DuckDB connection."""
        if self._conn is None:
            self._conn = duckdb.connect(str(self.db_path))
            logger.info(f"Connected to DuckDB: {self.db_path}")
        return self._conn
    
    def write_table(
        self,
        upload_id: uuid.UUID,
        kb_id: uuid.UUID,
        dataframe: pd.DataFrame,
        sheet_name: Optional[str] = None,
    ) -> str:
        """
        Write DataFrame rows to DuckDB table.
        
        Table naming embeds KB and upload ID for isolation.
        
        Args:
            upload_id: Upload identifier
            kb_id: Knowledge base identifier
            dataframe: Data to persist
            sheet_name: Optional sheet name (for XLSX)
        
        Returns:
            Table name created
        
        Raises:
            ValueError: If dataframe exceeds size limits
        """
        # Size cap: 100MB or 1M rows
        max_size_mb = getattr(settings, 'STRUCTURED_MAX_SIZE_MB', 100)
        max_rows = getattr(settings, 'STRUCTURED_MAX_ROWS', 1_000_000)
        
        if len(dataframe) > max_rows:
            raise ValueError(
                f"Dataframe exceeds row limit: {len(dataframe)} > {max_rows}"
            )
        
        # Estimate size in MB
        size_mb = dataframe.memory_usage(deep=True).sum() / (1024 ** 2)
        if size_mb > max_size_mb:
            raise ValueError(
                f"Dataframe exceeds size limit: {size_mb:.1f} MB > {max_size_mb} MB"
            )
        
        # Generate table name
        kb_short = str(kb_id).replace('-', '')[:8]
        upload_short = str(upload_id).replace('-', '')[:8]
        sheet_suffix = f"_{sheet_name}" if sheet_name else ""
        table_name = f"kb_{kb_short}_upload_{upload_short}{sheet_suffix}"
        
        # Ensure table doesn't exist
        try:
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        except Exception as e:
            logger.warning(f"Could not drop table {table_name}: {e}")
        
        # Create table from dataframe
        try:
            # DuckDB's create method
            self.conn.from_df(dataframe).create(table_name)
            
            logger.success(
                f"Created DuckDB table '{table_name}': "
                f"{len(dataframe)} rows, {len(dataframe.columns)} columns"
            )
            
            return table_name
        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            raise
    
    def query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute parameterized DuckDB query.
        
        CRITICAL: Only called by safe SQL compiler, never from LLM.
        
        Args:
            sql: Parameterized SQL query (use ? for params)
            params: Dict of parameter values
        
        Returns:
            List of result rows as dicts
        
        Raises:
            ValueError: If query syntax invalid or tables don't exist
        """
        params = params or {}
        
        try:
            # DuckDB native parameterization
            if params:
                # Convert dict params to positional for DuckDB
                param_list = [params.get(k) for k in sorted(params.keys())]
                result = self.conn.execute(sql, param_list).fetchall()
            else:
                result = self.conn.execute(sql).fetchall()
            
            # Convert to dict list
            columns = [desc[0] for desc in self.conn.description]
            dict_results = [dict(zip(columns, row)) for row in result]
            
            logger.debug(f"Query returned {len(dict_results)} rows")
            return dict_results
        
        except Exception as e:
            logger.error(f"Query execution failed: {e}\nSQL: {sql}")
            raise ValueError(f"Query failed: {e}")
    
    def delete_table(self, table_name: str) -> bool:
        """Delete a table (on re-ingest)."""
        try:
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            logger.info(f"Deleted DuckDB table: {table_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete table {table_name}: {e}")
            return False
    
    def list_tables(self) -> List[str]:
        """List all tables in DuckDB."""
        try:
            result = self.conn.execute(
                "SELECT name FROM information_schema.tables WHERE table_schema='main'"
            ).fetchall()
            return [row[0] for row in result]
        except Exception as e:
            logger.warning(f"Could not list tables: {e}")
            return []
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get schema and row count for a table."""
        try:
            # Get row count
            count_result = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            row_count = count_result[0] if count_result else 0
            
            # Get column info
            columns_result = self.conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
            columns = []
            for col in columns_result:
                columns.append({
                    "name": col[1],
                    "type": col[2],
                    "notnull": col[3],
                    "default": col[4],
                })
            
            return {
                "table_name": table_name,
                "row_count": row_count,
                "columns": columns,
                "column_count": len(columns),
            }
        except Exception as e:
            logger.warning(f"Could not get table info for {table_name}: {e}")
            return {}
    
    def close(self):
        """Close DuckDB connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            logger.info("Closed DuckDB connection")
