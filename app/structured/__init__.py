"""
ATLAS Structured Query System

Modules:
- schema_discovery: Detect columns, types, semantic roles
- duckdb_store: Per-tenant OLAP storage
- column_resolver: Map semantic→physical columns
- query_planner: Build validated query plans
- plan_compiler: Convert plans to safe SQL
- structured_executor: Execute via DuckDB, return with provenance
"""

from app.structured.schema_discovery import SchemaDiscoveryEngine, SemanticRole, ColumnMetadata
from app.structured.duckdb_store import StructuredDataStore
from app.structured.column_resolver import resolve_semantic_column
from app.structured.query_planner import SchemaAwareQueryPlanner, QueryPlan
from app.structured.plan_compiler import SafeSQLCompiler
from app.structured.structured_executor import StructuredQueryExecutor

__all__ = [
    "SchemaDiscoveryEngine",
    "SemanticRole",
    "ColumnMetadata",
    "StructuredDataStore",
    "resolve_semantic_column",
    "SchemaAwareQueryPlanner",
    "QueryPlan",
    "SafeSQLCompiler",
    "StructuredQueryExecutor",
]
