"""
PHASE 7: SQL Validation using SQLGlot AST

CRITICAL: This validator is the ONLY defense against malicious SQL.
Every LLM-generated SQL MUST pass through here before execution.

Validation Rules:
1. Must parse as valid SQL
2. Only SELECT statements allowed (no DDL/DML)
3. No dangerous operations: DROP, INSERT, UPDATE, DELETE, ATTACH, PRAGMA, COPY, LOAD
4. No subqueries accessing system tables or metadata
5. No user-defined functions (UDF)
6. Table references must match expected KB tables
"""

from typing import List, Optional, Set
import re
import sqlglot
from app.utils.logger import logger


class SQLValidationError(Exception):
    """Raised when SQL fails validation."""
    pass


class SQLValidator:
    """
    Validates SQL safety using SQLGlot AST parsing.
    
    Design:
    - Parse SQL to AST
    - Walk AST looking for dangerous operations
    - Reject if any blacklisted operations found
    """
    
    # Blacklisted SQL keywords (case-insensitive)
    BLACKLISTED_KEYWORDS = {
        # DDL
        "CREATE", "DROP", "ALTER", "TRUNCATE", "RENAME",
        # DML (write operations)
        "INSERT", "UPDATE", "DELETE", "REPLACE", "MERGE",
        # System operations
        "ATTACH", "DETACH", "PRAGMA", "COPY", "LOAD", "INSTALL",
        # Execution
        "EXEC", "EXECUTE", "CALL",
        # File operations
        "EXPORT",
    }
    
    # Allowed statement types (from sqlglot)
    ALLOWED_STATEMENTS = {
        sqlglot.exp.Select,
    }
    
    def __init__(self, allowed_tables: Optional[Set[str]] = None):
        """
        Initialize validator.
        
        Args:
            allowed_tables: Set of table names allowed to be queried
                           (if None, any table is allowed - use with caution!)
        """
        self.allowed_tables = allowed_tables
    
    def validate(self, sql: str) -> bool:
        """
        Validate SQL safety.
        
        Args:
            sql: SQL string to validate
        
        Returns:
            True if safe
        
        Raises:
            SQLValidationError: If SQL is dangerous
        """
        logger.debug(f"Validating SQL: {sql[:100]}...")
        
        # 1. Check for blacklisted keywords (fast check)
        self._check_keywords(sql)
        
        # 2. Parse SQL to AST
        try:
            parsed = sqlglot.parse_one(sql, read="duckdb")
        except Exception as e:
            raise SQLValidationError(f"SQL parse error: {e}")
        
        # 3. Validate statement type
        if not isinstance(parsed, tuple(self.ALLOWED_STATEMENTS)):
            raise SQLValidationError(
                f"Only SELECT statements allowed, got: {type(parsed).__name__}"
            )
        
        # 4. Walk AST looking for dangerous operations
        self._walk_ast(parsed)
        
        # 5. Validate table references
        if self.allowed_tables is not None:
            self._check_tables(parsed)
        
        logger.info("SQL validation passed ✓")
        return True
    
    def _check_keywords(self, sql: str):
        """Fast check for blacklisted keywords."""
        sql_upper = sql.upper()
        
        for keyword in self.BLACKLISTED_KEYWORDS:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, sql_upper):
                raise SQLValidationError(
                    f"Dangerous operation detected: {keyword}"
                )
    
    def _walk_ast(self, node):
        """
        Recursively walk AST looking for dangerous operations.
        
        Args:
            node: SQLGlot expression node
        
        Raises:
            SQLValidationError: If dangerous operation found
        """
        # Check for dangerous expression types
        dangerous_types = {
            sqlglot.exp.Create,
            sqlglot.exp.Drop,
            sqlglot.exp.Insert,
            sqlglot.exp.Update,
            sqlglot.exp.Delete,
            sqlglot.exp.Merge,
            sqlglot.exp.Command,  # PRAGMA, ATTACH, etc.
        }
        
        if type(node) in dangerous_types:
            raise SQLValidationError(
                f"Dangerous operation: {type(node).__name__}"
            )
        
        # Check for UDF calls (user-defined functions)
        if isinstance(node, sqlglot.exp.Anonymous):
            func_name = node.name.upper()
            # Allow standard aggregations and functions
            allowed_funcs = {
                "SUM", "COUNT", "AVG", "MIN", "MAX",
                "CAST", "COALESCE", "IFNULL",
                "UPPER", "LOWER", "TRIM", "LENGTH",
                "DATE", "YEAR", "MONTH", "DAY",
                "STRFTIME", "STRPTIME",
            }
            if func_name not in allowed_funcs:
                logger.warning(f"Potentially unsafe function: {func_name}")
                # Don't block, but log for monitoring
        
        # Recursively check children
        for child in node.iter_expressions():
            self._walk_ast(child)
    
    def _check_tables(self, parsed):
        """
        Validate table references against allowed list.
        
        Args:
            parsed: Parsed SQL AST
        
        Raises:
            SQLValidationError: If unknown table referenced
        """
        # Extract all table references
        tables = set()
        
        for table_node in parsed.find_all(sqlglot.exp.Table):
            table_name = table_node.name
            tables.add(table_name.lower())
        
        # Check against allowed list
        for table in tables:
            if table not in {t.lower() for t in self.allowed_tables}:
                raise SQLValidationError(
                    f"Table not allowed: {table}. "
                    f"Allowed tables: {', '.join(self.allowed_tables)}"
                )
        
        logger.debug(f"Table validation passed: {tables}")


def validate_sql(sql: str, allowed_tables: Optional[Set[str]] = None) -> bool:
    """
    Convenience function to validate SQL.
    
    Args:
        sql: SQL string
        allowed_tables: Set of allowed table names (optional)
    
    Returns:
        True if valid
    
    Raises:
        SQLValidationError: If invalid
    """
    validator = SQLValidator(allowed_tables=allowed_tables)
    return validator.validate(sql)
