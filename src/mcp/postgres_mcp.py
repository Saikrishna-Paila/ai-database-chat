"""
PostgreSQL MCP (Model Context Protocol) Client
Wraps the PostgreSQL connector with MCP-compatible interface
"""

from typing import Dict, Any, List, Optional
import json

from src.database.postgres_connector import PostgresConnector
from src.config import settings


class PostgresMCPClient:
    """MCP-compatible client for PostgreSQL operations"""

    def __init__(self, connector: Optional[PostgresConnector] = None):
        self.connector = connector or PostgresConnector()
        self.db_type = "postgresql"

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available MCP tools for PostgreSQL"""
        return [
            {
                "name": "postgres_query",
                "description": "Execute a read-only SQL query on PostgreSQL database",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "The SQL query to execute"
                        }
                    },
                    "required": ["sql"]
                }
            },
            {
                "name": "postgres_schema",
                "description": "Get the schema information for the PostgreSQL database",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "postgres_tables",
                "description": "List all tables in the PostgreSQL database",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "postgres_table_info",
                "description": "Get detailed information about a specific table",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table to inspect"
                        }
                    },
                    "required": ["table_name"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool"""
        tool_handlers = {
            "postgres_query": self._handle_query,
            "postgres_schema": self._handle_schema,
            "postgres_tables": self._handle_tables,
            "postgres_table_info": self._handle_table_info
        }

        handler = tool_handlers.get(tool_name)
        if not handler:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }

        return handler(arguments)

    def _handle_query(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SQL query execution"""
        sql = arguments.get("sql", "")

        if not sql:
            return {"success": False, "error": "No SQL query provided"}

        # Safety check
        if not self._is_safe_query(sql):
            return {
                "success": False,
                "error": "Query contains blocked keywords or operations"
            }

        result = self.connector.execute_query(sql)

        # Convert DataFrame to serializable format
        if result.get("success") and "dataframe" in result:
            del result["dataframe"]

        return result

    def _handle_schema(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle schema retrieval"""
        try:
            schema = self.connector.get_full_schema()
            return {
                "success": True,
                "data": schema
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _handle_tables(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle table listing"""
        try:
            tables = self.connector.get_tables()
            return {
                "success": True,
                "data": {"tables": tables}
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _handle_table_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle table info retrieval"""
        table_name = arguments.get("table_name", "")

        if not table_name:
            return {"success": False, "error": "No table name provided"}

        try:
            schema = self.connector.get_table_schema(table_name)
            return {
                "success": True,
                "data": schema
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _is_safe_query(self, sql: str) -> bool:
        """Check if query is safe to execute"""
        sql_upper = sql.upper()

        for keyword in settings.blocked_sql_keywords:
            if keyword.upper() in sql_upper:
                return False

        # No multiple statements
        if sql.count(';') > 1:
            return False

        return True

    def get_context(self) -> str:
        """Get database context for LLM"""
        return self.connector.get_schema_description()

    def test_connection(self) -> bool:
        """Test database connection"""
        return self.connector.test_connection()

    def close(self):
        """Close the connection"""
        self.connector.close()
