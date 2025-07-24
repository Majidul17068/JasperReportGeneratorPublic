#!/usr/bin/env python3
"""
Enhanced Database Analyzer for AI-powered JRXML Generation
"""

from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.engine import Engine
from typing import Dict, List, Any, Optional
import pandas as pd
from config import Config

class DatabaseAnalyzer:
    def __init__(self):
        """Initialize database connection and analyzer"""
        self.engine: Engine = create_engine(Config.DATABASE_URL)
        self.metadata = MetaData()
        self.inspector = inspect(self.engine)
        
    def get_comprehensive_schema_info(self) -> Dict[str, Any]:
        """
        Get comprehensive database schema information for AI understanding
        Returns detailed information about tables, columns, relationships, and constraints
        """
        schema_info = {
            "database_name": self.engine.url.database,
            "tables": {},
            "relationships": [],
            "constraints": {},
            "summary": {}
        }
        
        try:
            # Get all tables from all schemas
            all_tables = []
            for schema_name in self.inspector.get_schema_names():
                if schema_name not in ['information_schema', 'pg_catalog', 'pg_toast']:
                    schema_tables = self.inspector.get_table_names(schema=schema_name)
                    all_tables.extend([f"{schema_name}.{table}" for table in schema_tables])
            
            schema_info["summary"]["total_tables"] = len(all_tables)
            schema_info["summary"]["schemas"] = [s for s in self.inspector.get_schema_names() if s not in ['information_schema', 'pg_catalog', 'pg_toast']]
            
            for table_name in all_tables:
                table_info = self._analyze_table(table_name)
                schema_info["tables"][table_name] = table_info
                
                # Get foreign key relationships
                if '.' in table_name:
                    schema, table = table_name.split('.', 1)
                    try:
                        foreign_keys = self.inspector.get_foreign_keys(table, schema=schema)
                    except:
                        foreign_keys = []
                else:
                    try:
                        foreign_keys = self.inspector.get_foreign_keys(table_name)
                    except:
                        foreign_keys = []
                
                for fk in foreign_keys:
                    relationship = {
                        "from_table": table_name,
                        "to_table": fk["referred_table"],
                        "from_columns": fk["constrained_columns"],
                        "to_columns": fk["referred_columns"],
                        "relationship_type": "foreign_key"
                    }
                    schema_info["relationships"].append(relationship)
                
                # Get primary keys
                if '.' in table_name:
                    schema, table = table_name.split('.', 1)
                    try:
                        primary_keys = self.inspector.get_pk_constraint(table, schema=schema)
                    except:
                        primary_keys = {"constrained_columns": []}
                else:
                    try:
                        primary_keys = self.inspector.get_pk_constraint(table_name)
                    except:
                        primary_keys = {"constrained_columns": []}
                
                if primary_keys["constrained_columns"]:
                    schema_info["constraints"][table_name] = {
                        "primary_key": primary_keys["constrained_columns"],
                        "unique_constraints": [],
                        "check_constraints": []
                    }
            
            # Get sample data for understanding data types and values
            schema_info["sample_data"] = self._get_sample_data_for_tables(all_tables[:5])  # First 5 tables
            
            return schema_info
            
        except Exception as e:
            print(f"Error analyzing schema: {e}")
            return schema_info
    
    def _analyze_table(self, table_name: str) -> Dict[str, Any]:
        """Analyze a single table in detail"""
        try:
            if '.' in table_name:
                schema, table = table_name.split('.', 1)
                columns = self.inspector.get_columns(table, schema=schema)
                indexes = self.inspector.get_indexes(table, schema=schema)
            else:
                columns = self.inspector.get_columns(table_name)
                indexes = self.inspector.get_indexes(table_name)
            
            table_info = {
                "name": table_name,
                "columns": {},
                "indexes": indexes,
                "row_count": self._get_table_row_count(table_name),
                "description": self._get_table_description(table_name)
            }
            
            for column in columns:
                col_name = column["name"]
                table_info["columns"][col_name] = {
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                    "default": column["default"],
                    "primary_key": column.get("primary_key", False),
                    "unique": column.get("unique", False),
                    "sample_values": self._get_column_sample_values(table_name, col_name),
                    "description": self._get_column_description(table_name, col_name)
                }
            
            return table_info
            
        except Exception as e:
            print(f"Error analyzing table {table_name}: {e}")
            return {"name": table_name, "error": str(e)}
    
    def _get_table_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.scalar()
        except:
            return 0
    
    def _get_table_description(self, table_name: str) -> str:
        """Get table description from comments or metadata"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT obj_description(c.oid) 
                    FROM pg_class c 
                    WHERE c.relname = '{table_name}'
                """))
                return result.scalar() or f"Table containing {table_name} data"
        except:
            return f"Table containing {table_name} data"
    
    def _get_column_description(self, table_name: str, column_name: str) -> str:
        """Get column description from comments or metadata"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT col_description(c.oid, cols.ordinal_position::int)
                    FROM pg_class c
                    JOIN pg_attribute cols ON cols.attrelid = c.oid
                    WHERE c.relname = '{table_name}' AND cols.attname = '{column_name}'
                """))
                return result.scalar() or f"Column {column_name} in {table_name}"
        except:
            return f"Column {column_name} in {table_name}"
    
    def _get_column_sample_values(self, table_name: str, column_name: str, limit: int = 5) -> List[Any]:
        """Get sample values from a column"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT DISTINCT {column_name} 
                    FROM {table_name} 
                    WHERE {column_name} IS NOT NULL 
                    LIMIT {limit}
                """))
                return [row[0] for row in result.fetchall()]
        except:
            return []
    
    def _get_sample_data_for_tables(self, table_names: List[str]) -> Dict[str, Any]:
        """Get sample data for understanding table contents"""
        sample_data = {}
        for table_name in table_names[:3]:  # Limit to 3 tables to avoid too much data
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())
                    sample_data[table_name] = df.to_dict('records')
            except Exception as e:
                sample_data[table_name] = {"error": str(e)}
        return sample_data
    
    def get_ai_optimized_schema_summary(self) -> str:
        """
        Get a comprehensive schema summary optimized for AI understanding
        This provides the AI with complete database knowledge
        """
        schema_info = self.get_comprehensive_schema_info()
        
        summary = f"""DATABASE SCHEMA ANALYSIS for {schema_info['database_name']}

TOTAL TABLES: {schema_info['summary']['total_tables']}

DETAILED TABLE INFORMATION:
"""
        
        for table_name, table_info in schema_info['tables'].items():
            if 'error' in table_info:
                continue
                
            summary += f"\nTABLE: {table_name}"
            summary += f"\n- Row Count: {table_info.get('row_count', 'Unknown')}"
            summary += f"\n- Description: {table_info.get('description', 'No description')}"
            
            # Add columns
            summary += "\n- COLUMNS:"
            for col_name, col_info in table_info['columns'].items():
                summary += f"\n  * {col_name}: {col_info['type']}"
                if col_info['primary_key']:
                    summary += " (PRIMARY KEY)"
                if col_info['unique']:
                    summary += " (UNIQUE)"
                if not col_info['nullable']:
                    summary += " (NOT NULL)"
                if col_info['sample_values']:
                    summary += f" - Sample values: {col_info['sample_values'][:3]}"
                summary += f" - {col_info['description']}"
            
            # Add indexes
            if table_info.get('indexes'):
                summary += "\n- INDEXES:"
                for idx in table_info['indexes']:
                    summary += f"\n  * {idx['name']}: {idx['column_names']}"
            
            summary += "\n"
        
        # Add relationships
        if schema_info['relationships']:
            summary += "\nTABLE RELATIONSHIPS:\n"
            for rel in schema_info['relationships']:
                summary += f"- {rel['from_table']}.{rel['from_columns']} -> {rel['to_table']}.{rel['to_columns']}\n"
        
        # Add constraints
        summary += "\nCONSTRAINTS:\n"
        for table_name, constraints in schema_info['constraints'].items():
            if 'primary_key' in constraints:
                summary += f"- {table_name} Primary Key: {constraints['primary_key']}\n"
        
        # Add sample data insights
        if schema_info.get('sample_data'):
            summary += "\nSAMPLE DATA INSIGHTS:\n"
            for table_name, data in schema_info['sample_data'].items():
                if isinstance(data, list) and data:
                    summary += f"- {table_name}: Contains {len(data)} sample rows\n"
        
        return summary
    
    def get_schema_summary(self) -> str:
        """Legacy method for backward compatibility"""
        return self.get_ai_optimized_schema_summary()
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results as list of dictionaries"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Get column names for a specific table"""
        try:
            columns = self.inspector.get_columns(table_name)
            return [col['name'] for col in columns]
        except Exception as e:
            print(f"Error getting columns for {table_name}: {e}")
            return []
    
    def get_table_data_types(self, table_name: str) -> Dict[str, str]:
        """Get data types for all columns in a table"""
        try:
            columns = self.inspector.get_columns(table_name)
            return {col['name']: str(col['type']) for col in columns}
        except Exception as e:
            print(f"Error getting data types for {table_name}: {e}")
            return {}
    
    def suggest_related_tables(self, table_name: str) -> List[str]:
        """Suggest related tables based on foreign key relationships"""
        try:
            related_tables = set()
            
            # Tables that reference this table
            for table in self.inspector.get_table_names():
                foreign_keys = self.inspector.get_foreign_keys(table)
                for fk in foreign_keys:
                    if fk['referred_table'] == table_name:
                        related_tables.add(table)
            
            # Tables that this table references
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            for fk in foreign_keys:
                related_tables.add(fk['referred_table'])
            
            return list(related_tables)
        except Exception as e:
            print(f"Error suggesting related tables: {e}")
            return [] 

    def is_table(self, table_name: str) -> bool:
        """Check if a table exists in the database (supports schema.table and table)"""
        try:
            if '.' in table_name:
                schema, table = table_name.split('.', 1)
                return table in self.inspector.get_table_names(schema=schema)
            else:
                for schema in self.inspector.get_schema_names():
                    if schema in ['information_schema', 'pg_catalog', 'pg_toast']:
                        continue
                    if table_name in self.inspector.get_table_names(schema=schema):
                        return True
                return False
        except Exception as e:
            print(f"Error checking table existence: {e}")
            return False

    def get_table_schema_summary(self, table_names: list) -> str:
        """Get schema summary for only the specified tables and their direct relationships"""
        summary = ""
        for table_name in table_names:
            try:
                table_info = self._analyze_table(table_name)
                if 'error' in table_info:
                    continue
                summary += f"\nTABLE: {table_name}"
                summary += f"\n- Row Count: {table_info.get('row_count', 'Unknown')}"
                summary += f"\n- Description: {table_info.get('description', 'No description')}"
                summary += "\n- COLUMNS:"
                for col_name, col_info in table_info['columns'].items():
                    summary += f"\n  * {col_name}: {col_info['type']}"
                    if col_info['primary_key']:
                        summary += " (PRIMARY KEY)"
                    if col_info['unique']:
                        summary += " (UNIQUE)"
                    if not col_info['nullable']:
                        summary += " (NOT NULL)"
                    if col_info['sample_values']:
                        summary += f" - Sample values: {col_info['sample_values'][:3]}"
                    summary += f" - {col_info['description']}"
                if table_info.get('indexes'):
                    summary += "\n- INDEXES:"
                    for idx in table_info['indexes']:
                        summary += f"\n  * {idx['name']}: {idx['column_names']}"
                summary += "\n"
                # Add direct relationships (foreign keys)
                if '.' in table_name:
                    schema, table = table_name.split('.', 1)
                    try:
                        foreign_keys = self.inspector.get_foreign_keys(table, schema=schema)
                    except:
                        foreign_keys = []
                else:
                    try:
                        foreign_keys = self.inspector.get_foreign_keys(table_name)
                    except:
                        foreign_keys = []
                if foreign_keys:
                    summary += "- FOREIGN KEYS:\n"
                    for fk in foreign_keys:
                        summary += f"  * {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}\n"
            except Exception as e:
                summary += f"\nError analyzing table {table_name}: {e}\n"
        return summary 