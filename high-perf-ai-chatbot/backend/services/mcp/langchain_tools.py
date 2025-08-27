"""
LangChain tool wrappers for MCP server functionality
"""
from typing import List
from langchain_core.tools import Tool
from .tools import query_db, execute_db
from .db_adapter import run_query
import json

def create_mcp_tools() -> List[Tool]:
    """Create LangChain tools from MCP server functions"""
    
    def safe_query_db(sql: str) -> str:
        """Safely execute SELECT queries"""
        try:
            if not sql.strip().upper().startswith('SELECT'):
                return "Error: Only SELECT queries allowed"
            
            results = query_db(sql)
            if not results:
                return "No results found"
            
            # Format for better readability
            formatted = [dict(row) for row in results]
            return json.dumps(formatted, indent=2, default=str)
            
        except Exception as e:
            return f"Database query error: {str(e)}"
    
    def safe_execute_db(sql: str) -> str:
        """Safely execute INSERT/UPDATE/DELETE queries"""
        try:
            sql_upper = sql.strip().upper()
            allowed_ops = ['INSERT', 'UPDATE', 'DELETE']
            
            if not any(sql_upper.startswith(op) for op in allowed_ops):
                return "Error: Only INSERT, UPDATE, DELETE allowed"
            
            result = execute_db(sql)
            return f"Operation completed: {result}"
            
        except Exception as e:
            return f"Database execution error: {str(e)}"
    
    def get_database_schema(table_name: str = "") -> str:
        """Get database schema information"""
        try:
            if table_name:
                schema_sql = f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
                """
            else:
                schema_sql = """
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
                """
            
            results = query_db(schema_sql)
            return json.dumps([dict(r) for r in results], indent=2, default=str)
            
        except Exception as e:
            return f"Schema query error: {str(e)}"
    
    return [
        Tool(
            name="query_database",
            description="Execute SELECT queries on PostgreSQL. Use for retrieving data.",
            func=safe_query_db
        ),
        Tool(
            name="execute_database", 
            description="Execute INSERT/UPDATE/DELETE on PostgreSQL. Use for data modifications.",
            func=safe_execute_db
        ),
        Tool(
            name="get_database_schema",
            description="Get database schema. Provide table_name or leave empty for all tables.",
            func=get_database_schema
        )
    ]
