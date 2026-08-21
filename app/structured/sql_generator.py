"""
PHASE 6: LLM-Based SQL Generator (Qwen Fallback)

When query planner cannot handle complex analytical queries,
fall back to Qwen Coder for SQL generation.

CRITICAL SAFETY:
1. Generated SQL MUST pass through SQLValidator before execution
2. Only SELECT statements allowed
3. No DDL/DML operations (DROP/INSERT/UPDATE/DELETE)
4. No ATTACH/PRAGMA/COPY commands
"""

from typing import Any, Dict, List, Optional, Tuple
import re
from app.llm.model_router import get_model
from app.db.models import StructuredFileSchema
from app.utils.logger import logger
from app.structured.query_analyzer import QueryAnalysisAgent, QueryAnalysis


class LLMSQLGenerator:
    """
    Generates SQL using Qwen Coder for complex analytical queries.
    
    Uses codegen-optimized model with low temperature for deterministic output.
    """
    
    def __init__(self):
        """Initialize SQL generator with LLM and analysis agent."""
        self.llm = get_model("codegen")
        self.analyzer = QueryAnalysisAgent()  # NEW: Query analysis agent
    
    def generate(
        self,
        query: str,
        schemas: List[StructuredFileSchema],
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate SQL from natural language query.
        
        NEW: Uses QueryAnalysisAgent to understand query first.
        
        Args:
            query: Natural language question
            schemas: Available schemas (for table structure context)
        
        Returns:
            (sql_string, metadata) where metadata includes analysis, etc.
        
        Raises:
            ValueError: If generation fails or output invalid
        """
        logger.info(f"Generating SQL via LLM for query: '{query}'")
        
        # STEP 1: Analyze query structure
        analysis = self.analyzer.analyze(query, schemas)
        logger.info(f"Query analysis: {analysis.to_dict()}")
        
        # STEP 1.5: Extract date from query if analysis didn't find it
        # This is a CRITICAL FALLBACK for when QueryAnalysisAgent fails
        extracted_date = None
        if not analysis.filters or len(analysis.filters) == 0:
            extracted_date = self._extract_date_from_query(query)
            if extracted_date:
                logger.info(f"Extracted date from query: {extracted_date}")
        
        # STEP 2: Build enhanced prompt with analysis
        prompt = self._build_prompt_with_analysis(query, schemas, analysis, extracted_date)
        
        # STEP 3: Generate SQL
        try:
            response = self.llm.generate(prompt)
            raw_sql = response.answer.strip()
            
            # Extract SQL from markdown code blocks if present
            sql = self._extract_sql(raw_sql)
            
            logger.debug(f"Generated SQL:\n{sql}")
            
            return sql, {
                "model": response.model_name,
                "tokens": response.total_tokens,
                "method": "llm_codegen_with_analysis",
                "analysis": analysis.to_dict(),  # Include analysis in metadata
                "extracted_date_fallback": extracted_date,
            }
        
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            raise ValueError(f"Failed to generate SQL: {e}")
    
    def _build_prompt_with_analysis(
        self,
        query: str,
        schemas: List[StructuredFileSchema],
        analysis: QueryAnalysis,
        extracted_date: Optional[str] = None,
    ) -> str:
        """
        Build prompt with pre-analyzed query structure.
        This guides the LLM to generate correct SQL.
        """
        schema_context = "Available tables and columns:\n\n"
        table_names = []
        
        for schema in schemas:
            table_name = self._get_table_name(schema)
            table_names.append(table_name)
            schema_context += f"Table: {table_name}\n"
            schema_context += f"Columns:\n"
            
            columns_list = schema.columns if isinstance(schema.columns, list) else []
            
            for col_meta in columns_list:
                if isinstance(col_meta, dict):
                    col_name = col_meta.get("original_name", "unknown")
                    col_type = col_meta.get("data_type", "unknown")
                    semantic_role = col_meta.get("semantic_role", "unknown")
                    quoted_name = f'"{col_name}"' if ' ' in col_name else col_name
                    schema_context += f"  - {quoted_name} ({col_type}) [semantic: {semantic_role}]\n"
            
            schema_context += "\n"
        
        # Build instructions for handling multiple tables
        multiple_tables_instruction = ""
        if len(table_names) > 1:
            multiple_tables_instruction = f"""
CRITICAL - MULTIPLE TABLES:
You have {len(table_names)} tables from the same Knowledge Base:
{chr(10).join(f'- {tn}' for tn in table_names)}

YOU MUST:
1. Query ALL tables (not just one!)
2. Use UNION ALL to combine results from all tables
3. Example: SELECT col FROM table1 WHERE filter UNION ALL SELECT col FROM table2 WHERE filter
4. For aggregations (SUM, COUNT): Use subquery with UNION ALL then aggregate the results
5. Example for SUM: SELECT SUM(revenue) FROM (SELECT "Total Revenue" FROM table1 UNION ALL SELECT "Total Revenue" FROM table2) AS combined
6. This ensures you get data from ALL uploaded files in this KB, not just one file
"""
        else:
            multiple_tables_instruction = f"""
Single table: {table_names[0]}
"""
        
        # Build GROUP BY instruction for "which day" queries
        group_by_instruction = ""
        if analysis.operation.value == "GROUP_BY" and analysis.group_by_columns:
            group_by_instruction = f"""
GROUP BY QUERY DETECTED:
- Group by: {', '.join(analysis.group_by_columns)}
- Aggregate metric: {', '.join(analysis.metrics) if analysis.metrics else 'auto-detect'}
- Order: {analysis.order_by if analysis.order_by else 'by aggregate DESC'}
- Limit: {analysis.limit if analysis.limit else '1'}

IMPORTANT: Do NOT use dayname() or to_date() functions - they require proper DATE types
Since dates are VARCHAR, just group by the raw Date column and sort by the aggregate metric

Example pattern:
SELECT {', '.join(analysis.group_by_columns)}, SUM(metric) as total
FROM table
GROUP BY {', '.join(analysis.group_by_columns)}
ORDER BY total DESC
LIMIT {analysis.limit or 1}
"""
        
        # Build analysis-guided prompt with strong date filtering guidance
        date_extraction_hint = ""
        if extracted_date:
            date_extraction_hint = f"""
FALLBACK DATE EXTRACTION:
Analysis didn't extract date, but found in query: {extracted_date}
If generating WHERE clause, use: WHERE "Date" LIKE '{extracted_date}-%'
"""
        
        prompt = f"""You are a DuckDB SQL expert. Generate a SELECT query based on this analysis.

{schema_context}
{multiple_tables_instruction}
{group_by_instruction}
{date_extraction_hint}

CRITICAL DATE HANDLING:
- Dates are stored as VARCHAR in format "DD-MM-YYYY" (e.g., "04-08-2026" for August 4, 2026)
- NEVER use EXTRACT() or date_part() on VARCHAR columns
- NEVER use dayname(), to_date() or other date conversion functions on VARCHAR dates
- ALWAYS use string matching for dates:
  * For specific day/month: WHERE "Date" LIKE 'DD-MM-%' to match that day/month across all years
  * For exact date: WHERE "Date" = 'DD-MM-YYYY'
  * For month range: WHERE SUBSTR("Date", 4, 2) = 'MM'
- When grouping by date: Just use GROUP BY "Date" directly (it's already VARCHAR)
- Example: "which day have best revenue?" → GROUP BY "Date", ORDER BY SUM DESC, LIMIT 1

QUERY PATTERN DETECTION:
- If query contains "which day" or "best sales/revenue": Generate GROUP BY query
  * SELECT "Date", SUM(metric) FROM table GROUP BY "Date" ORDER BY SUM(metric) DESC LIMIT 1
- If query contains "total/sum": Generate SUM query
- If query contains "how many": Generate COUNT or SUM query
- If query contains "average": Generate AVG query

QUERY ANALYSIS (already parsed):
- Operation: {analysis.operation.value}
- Metrics to retrieve: {', '.join(analysis.metrics) if analysis.metrics else 'auto-detect from query'}
- Group by columns: {', '.join(analysis.group_by_columns) if analysis.group_by_columns else 'auto-detect from query'}
- Filters identified: {len(analysis.filters)}
- Filter details: {[f"{f.column} {f.operator} {f.value}" for f in analysis.filters] if analysis.filters else 'NONE - Check user query for date/numeric filters!'}
- Order by: {analysis.order_by}
- Limit: {analysis.limit}
- Intent: {analysis.semantic_intent}

CRITICAL: If no filters were extracted by analysis, LOOK FOR dates/numbers in the user query and add WHERE clause!
User Query Contains Dates? Look for month names (august, january, etc) or date patterns (06-08, 2026-08-06, etc)

INSTRUCTIONS:
1. YOU MUST RETURN ONLY SQL - NOTHING ELSE
2. DO NOT INCLUDE <think>, <analysis>, or any tags
3. DO NOT EXPLAIN OR SHOW THINKING
4. Start immediately with SELECT
5. If query asks "which day", use GROUP BY "Date" and ORDER BY aggregate DESC with LIMIT 1
6. Use the operation type: {analysis.operation.value}
7. Include all identified metrics and filters
8. If operation is GROUP_BY or query asks "which": Include GROUP BY clause and ORDER BY for ranking
9. Include ORDER BY and LIMIT if specified
10. NEVER use EXTRACT(), date_part(), dayname(), or to_date() on VARCHAR date columns
11. IF MULTIPLE TABLES: Always UNION ALL to combine all tables (this is critical!)

Original User Query: {query}

RESPONSE: Start immediately with SELECT:
"""
        return prompt
    
    def _extract_sql(self, raw_output: str) -> str:
        """
        Extract SQL from LLM output (handles markdown code blocks and thinking tags).
        
        Args:
            raw_output: Raw LLM response (may include <think> tags)
        
        Returns:
            Cleaned SQL string
        """
        sql = raw_output.strip()
        
        # Remove <think>...</think> tags (Qwen thinks through problems)
        # Use case-insensitive and handle multiline
        sql = re.sub(r'<think>.*?</think>', '', sql, flags=re.DOTALL | re.IGNORECASE)
        sql = re.sub(r'<Think>.*?</Think>', '', sql, flags=re.DOTALL)
        
        # Remove analysis/explanation blocks
        sql = re.sub(r'#+\s+Analysis.*?(?=SELECT|$)', '', sql, flags=re.DOTALL | re.IGNORECASE)
        sql = re.sub(r'Thinking Process:.*?(?=SELECT|$)', '', sql, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove markdown code blocks
        # Pattern: ```sql ... ``` or ``` ... ```
        code_block_match = re.search(r'```(?:sql)?\s*(.*?)\s*```', sql, re.DOTALL)
        if code_block_match:
            sql = code_block_match.group(1)
        
        # Extract only the SELECT statement (find first SELECT, take from there)
        select_match = re.search(r'SELECT\s+.*', sql, re.DOTALL | re.IGNORECASE)
        if select_match:
            sql = select_match.group(0)
        
        # Clean up
        sql = sql.strip()
        
        # Remove trailing semicolon (optional in DuckDB)
        if sql.endswith(';'):
            sql = sql[:-1].strip()
        
        # Remove any remaining XML/HTML-like tags
        sql = re.sub(r'<[^>]+>', '', sql).strip()
        
        return sql
    
    def _get_table_name(self, schema: StructuredFileSchema) -> str:
        """Get DuckDB table name for a schema."""
        try:
            kb_short = str(schema.knowledge_base_id).replace('-', '')[:8]
            upload_short = str(schema.upload_id).replace('-', '')[:8]
            sheet_suffix = f"_{schema.sheet_name}" if schema.sheet_name else ""
            return f"kb_{kb_short}_upload_{upload_short}{sheet_suffix}"
        except Exception as e:
            logger.warning(f"Could not generate table name: {e}")
            return "unknown_table"
    
    def _extract_date_from_query(self, query: str) -> Optional[str]:
        """
        Extract date from query as fallback when QueryAnalysisAgent fails.
        
        Supports:
        - "6 august" → "06-08"
        - "august 6" → "06-08"
        - "on 6 august" → "06-08"
        - "revenue on august 6" → "06-08"
        
        Returns:
            "DD-MM" format string or None if not found
        """
        import re
        
        query_lower = query.lower()
        
        # Month name to number mapping
        months = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }
        
        # Pattern 1: "6 august" or "august 6"
        for month_name, month_num in months.items():
            # Try "6 august" pattern
            match = re.search(rf'(\d{1,2})\s+{month_name}', query_lower)
            if match:
                day = match.group(1).zfill(2)
                return f"{day}-{month_num}"
            
            # Try "august 6" pattern
            match = re.search(rf'{month_name}\s+(\d{1,2})', query_lower)
            if match:
                day = match.group(1).zfill(2)
                return f"{day}-{month_num}"
        
        return None
