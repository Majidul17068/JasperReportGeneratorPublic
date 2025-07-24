#!/usr/bin/env python3
"""
OpenAI Query Generator for Intelligent JRXML Reports
"""

import openai
from typing import Dict, List, Any, Tuple
from config import Config
from database import DatabaseAnalyzer

class OpenAIQueryGenerator:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.model = Config.OPENAI_MODEL
        self.db_analyzer = DatabaseAnalyzer()

    def generate_sql_query(self, user_request: str) -> Tuple[str, str, Dict]:
        # Step 1: Extract table names from user request
        table_names = self._extract_table_names_from_request(user_request)
        # Step 2: Get focused schema summary for those tables
        schema_summary = self.db_analyzer.get_table_schema_summary(table_names)
        # Step 3: Build system prompt
        system_prompt = f"""You are an expert SQL query generator for PostgreSQL with knowledge of the following database schema:\n\nDATABASE SCHEMA KNOWLEDGE:\n{schema_summary}\n\nYour capabilities:\n1. Understand any table name, column name, or relationship mentioned in the request\n2. Generate complex SQL queries with proper JOINs, WHERE clauses, GROUP BY, ORDER BY, etc.\n3. Handle any type of filtering, aggregation, or calculation\n4. Use appropriate data types and handle date/time operations correctly\n5. Optimize queries for performance\n6. Handle multiple tables and complex relationships\n\nGuidelines for SQL generation:\n- Use proper table aliases for readability\n- Include appropriate WHERE clauses for filtering\n- Use aggregate functions (SUM, COUNT, AVG, MIN, MAX) when needed\n- Handle date filtering with proper date functions\n- Use CASE statements for conditional logic\n- Include ORDER BY for meaningful results\n- Use LIMIT for large result sets\n- Handle NULL values appropriately\n- Use proper JOIN types (INNER, LEFT, RIGHT, FULL) based on requirements\n\nQuery patterns you can handle:\n- Simple SELECT with WHERE conditions\n- Complex multi-table JOINs\n- Aggregations with GROUP BY\n- Subqueries and CTEs\n- Window functions\n- Date range filtering\n- Text search and pattern matching\n- Conditional aggregations\n- Ranking and sorting\n\nUser Request: \"{user_request}\"\n\nPlease analyze the request and generate an optimized PostgreSQL query that:\n1. Identifies the correct tables and columns\n2. Uses appropriate JOINs if multiple tables are needed\n3. Applies proper filtering conditions\n4. Includes necessary aggregations if requested\n5. Orders results appropriately\n6. Limits results if needed for performance\n\nReturn only the SQL query, no explanations in the query itself."""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                ],
                max_tokens=800,
                temperature=0.2,
            )
            ai_text = response.choices[0].message["content"]
            sql_query, explanation = self._parse_openai_response(ai_text)
            sql_query = self._sanitize_sql(sql_query)
            sql_query = self._optimize_query(sql_query, user_request)
            metadata = {
                "user_request": user_request,
                "tables_used": self._extract_tables_from_query(sql_query),
                "query_type": self._classify_query_type(user_request),
                "ai_model": self.model,
                "complexity": self._assess_query_complexity(sql_query)
            }
            return sql_query, explanation, metadata
        except Exception as e:
            error_msg = f"Error generating SQL query with OpenAI: {str(e)}"
            return "", error_msg, {"error": error_msg}

    def _sanitize_sql(self, sql_query: str) -> str:
        # Remove triple backticks and any markdown artifacts
        sql_query = sql_query.replace('```sql', '').replace('```', '')
        return sql_query.strip()

    def _parse_openai_response(self, response: str) -> Tuple[str, str]:
        lines = response.split('\n')
        sql_query = ""
        explanation = ""
        in_sql = False
        for line in lines:
            line = line.strip()
            if line.upper().startswith(('SELECT', 'WITH', 'WITH RECURSIVE')):
                in_sql = True
                sql_query += line + " "
            elif in_sql and line and not line.startswith('--'):
                if line.upper().startswith(('FROM', 'WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'INTERSECT', 'EXCEPT')):
                    sql_query += line + " "
                elif line.endswith(';'):
                    sql_query += line
                    in_sql = False
                else:
                    sql_query += line + " "
            elif not in_sql and line:
                explanation += line + "\n"
        return sql_query.strip(), explanation.strip()

    # The rest of the helper methods (_optimize_query, _extract_table_names_from_request, etc.)
    # can be copied from the Gemini version, as they are not model-specific.
    def _optimize_query(self, sql_query: str, user_request: str) -> str:
        if "LIMIT" not in sql_query.upper() and not self._is_aggregation_query(sql_query):
            tables = self._extract_tables_from_query(sql_query)
            for table in tables:
                if self.db_analyzer._get_table_row_count(table) > 10000:
                    sql_query = sql_query.rstrip(';') + " LIMIT 1000;"
                    break
        if "ORDER BY" not in sql_query.upper() and not self._is_aggregation_query(sql_query):
            order_column = self._suggest_order_column(sql_query)
            if order_column:
                sql_query = sql_query.rstrip(';') + f" ORDER BY {order_column} DESC;"
        return sql_query

    def _is_aggregation_query(self, sql_query: str) -> bool:
        aggregation_functions = ['SUM(', 'COUNT(', 'AVG(', 'MIN(', 'MAX(', 'GROUP BY']
        return any(func in sql_query.upper() for func in aggregation_functions)

    def _suggest_order_column(self, sql_query: str) -> str:
        common_order_columns = ['id', 'created_at', 'updated_at', 'date', 'timestamp', 'name', 'code']
        tables = self._extract_tables_from_query(sql_query)
        for table in tables:
            try:
                columns = self.db_analyzer.get_table_columns(table)
                for col in columns:
                    if any(order_col in col.lower() for order_col in common_order_columns):
                        return f"{table}.{col}"
            except:
                continue
        return ""

    def _extract_tables_from_query(self, query: str) -> List[str]:
        import re
        tables = re.findall(r'(?:FROM|JOIN)\s+(\w+\.?\w*)', query, re.IGNORECASE)
        return list(set(tables))

    def _classify_query_type(self, request: str) -> str:
        request_lower = request.lower()
        if any(word in request_lower for word in ['sum', 'total', 'amount', 'sales', 'revenue', 'cost', 'price']):
            return "aggregation"
        elif any(word in request_lower for word in ['count', 'number', 'how many', 'quantity']):
            return "counting"
        elif any(word in request_lower for word in ['average', 'avg', 'mean', 'median']):
            return "average"
        elif any(word in request_lower for word in ['list', 'show', 'display', 'get', 'find', 'search']):
            return "listing"
        elif any(word in request_lower for word in ['compare', 'difference', 'vs', 'versus']):
            return "comparison"
        elif any(word in request_lower for word in ['trend', 'over time', 'monthly', 'yearly', 'daily']):
            return "trend_analysis"
        else:
            return "general"

    def _assess_query_complexity(self, sql_query: str) -> str:
        complexity_score = 0
        if 'JOIN' in sql_query.upper():
            complexity_score += 2
        if 'GROUP BY' in sql_query.upper():
            complexity_score += 1
        if 'HAVING' in sql_query.upper():
            complexity_score += 1
        if 'UNION' in sql_query.upper():
            complexity_score += 2
        if 'WITH' in sql_query.upper():
            complexity_score += 2
        if 'CASE' in sql_query.upper():
            complexity_score += 1
        if 'SUBQUERY' in sql_query.upper() or '(' in sql_query:
            complexity_score += 1
        if complexity_score >= 4:
            return "high"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "low" 