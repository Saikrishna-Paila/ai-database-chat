"""
MCP Manager - Coordinates multiple MCP clients
"""

from typing import Dict, Any, List, Optional

from .postgres_mcp import PostgresMCPClient
from .mongodb_mcp import MongoDBMCPClient
from src.database import PostgresConnector, MongoDBConnector


class MCPManager:
    """Manages and coordinates multiple MCP clients"""

    def __init__(
        self,
        postgres_url: Optional[str] = None,
        mongodb_url: Optional[str] = None
    ):
        self._postgres_client: Optional[PostgresMCPClient] = None
        self._mongodb_client: Optional[MongoDBMCPClient] = None

        self.postgres_url = postgres_url
        self.mongodb_url = mongodb_url

    @property
    def postgres(self) -> Optional[PostgresMCPClient]:
        """Lazy load PostgreSQL MCP client"""
        if self._postgres_client is None and self.postgres_url:
            connector = PostgresConnector(self.postgres_url)
            self._postgres_client = PostgresMCPClient(connector)
        return self._postgres_client

    @property
    def mongodb(self) -> Optional[MongoDBMCPClient]:
        """Lazy load MongoDB MCP client"""
        if self._mongodb_client is None and self.mongodb_url:
            connector = MongoDBConnector(self.mongodb_url)
            self._mongodb_client = MongoDBMCPClient(connector)
        return self._mongodb_client

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools from all MCP clients"""
        tools = []

        if self.postgres:
            tools.extend(self.postgres.get_tools())

        if self.mongodb:
            tools.extend(self.mongodb.get_tools())

        return tools

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name, routing to the appropriate MCP client"""
        # PostgreSQL tools
        if tool_name.startswith("postgres_"):
            if not self.postgres:
                return {"success": False, "error": "PostgreSQL not configured"}
            return self.postgres.execute_tool(tool_name, arguments)

        # MongoDB tools
        if tool_name.startswith("mongodb_"):
            if not self.mongodb:
                return {"success": False, "error": "MongoDB not configured"}
            return self.mongodb.execute_tool(tool_name, arguments)

        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    def get_combined_context(self) -> str:
        """Get combined schema context from all databases"""
        contexts = []

        if self.postgres:
            contexts.append("=== PostgreSQL Database ===")
            contexts.append(self.postgres.get_context())

        if self.mongodb:
            contexts.append("=== MongoDB Database ===")
            contexts.append(self.mongodb.get_context())

        return "\n\n".join(contexts)

    def get_available_databases(self) -> List[str]:
        """Get list of available database types"""
        available = []

        if self.postgres and self.postgres.test_connection():
            available.append("postgresql")

        if self.mongodb and self.mongodb.test_connection():
            available.append("mongodb")

        return available

    def test_connections(self) -> Dict[str, bool]:
        """Test all database connections"""
        results = {}

        if self.postgres:
            results["postgresql"] = self.postgres.test_connection()

        if self.mongodb:
            results["mongodb"] = self.mongodb.test_connection()

        return results

    def get_database_info(self) -> Dict[str, Any]:
        """Get information about all connected databases"""
        info = {
            "databases": []
        }

        if self.postgres:
            pg_info = {
                "type": "postgresql",
                "connected": self.postgres.test_connection(),
                "tables": []
            }
            if pg_info["connected"]:
                try:
                    result = self.postgres.execute_tool("postgres_tables", {})
                    if result.get("success"):
                        pg_info["tables"] = result["data"]["tables"]
                except:
                    pass
            info["databases"].append(pg_info)

        if self.mongodb:
            mongo_info = {
                "type": "mongodb",
                "connected": self.mongodb.test_connection(),
                "collections": []
            }
            if mongo_info["connected"]:
                try:
                    result = self.mongodb.execute_tool("mongodb_collections", {})
                    if result.get("success"):
                        mongo_info["collections"] = result["data"]["collections"]
                except:
                    pass
            info["databases"].append(mongo_info)

        return info

    def close(self):
        """Close all connections"""
        if self._postgres_client:
            self._postgres_client.close()
            self._postgres_client = None

        if self._mongodb_client:
            self._mongodb_client.close()
            self._mongodb_client = None
