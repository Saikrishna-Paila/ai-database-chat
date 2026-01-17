"""
MongoDB MCP (Model Context Protocol) Client
Wraps the MongoDB connector with MCP-compatible interface
"""

from typing import Dict, Any, List, Optional
import json

from src.database.mongodb_connector import MongoDBConnector
from src.config import settings


class MongoDBMCPClient:
    """MCP-compatible client for MongoDB operations"""

    def __init__(self, connector: Optional[MongoDBConnector] = None):
        self.connector = connector or MongoDBConnector()
        self.db_type = "mongodb"

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available MCP tools for MongoDB"""
        return [
            {
                "name": "mongodb_find",
                "description": "Execute a find query on a MongoDB collection",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the collection to query"
                        },
                        "filter": {
                            "type": "object",
                            "description": "MongoDB filter query (optional)",
                            "default": {}
                        },
                        "projection": {
                            "type": "object",
                            "description": "Fields to include/exclude (optional)"
                        },
                        "sort": {
                            "type": "array",
                            "description": "Sort specification as list of [field, direction] pairs"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of documents to return"
                        }
                    },
                    "required": ["collection"]
                }
            },
            {
                "name": "mongodb_aggregate",
                "description": "Execute an aggregation pipeline on a MongoDB collection",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "collection": {
                            "type": "string",
                            "description": "Name of the collection to aggregate"
                        },
                        "pipeline": {
                            "type": "array",
                            "description": "Aggregation pipeline stages",
                            "items": {"type": "object"}
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of documents to return"
                        }
                    },
                    "required": ["collection", "pipeline"]
                }
            },
            {
                "name": "mongodb_schema",
                "description": "Get the schema information for the MongoDB database",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "mongodb_collections",
                "description": "List all collections in the MongoDB database",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "mongodb_collection_info",
                "description": "Get detailed information about a specific collection",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection to inspect"
                        }
                    },
                    "required": ["collection_name"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool"""
        tool_handlers = {
            "mongodb_find": self._handle_find,
            "mongodb_aggregate": self._handle_aggregate,
            "mongodb_schema": self._handle_schema,
            "mongodb_collections": self._handle_collections,
            "mongodb_collection_info": self._handle_collection_info
        }

        handler = tool_handlers.get(tool_name)
        if not handler:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }

        return handler(arguments)

    def _handle_find(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle find query execution"""
        collection = arguments.get("collection", "")

        if not collection:
            return {"success": False, "error": "No collection specified"}

        filter_query = arguments.get("filter", {})

        # Safety check
        if not self._is_safe_query(filter_query):
            return {
                "success": False,
                "error": "Query contains unsafe operators"
            }

        result = self.connector.execute_find(
            collection_name=collection,
            filter_query=filter_query,
            projection=arguments.get("projection"),
            sort=arguments.get("sort"),
            limit=arguments.get("limit")
        )

        # Remove DataFrame from result
        if "dataframe" in result:
            del result["dataframe"]

        return result

    def _handle_aggregate(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle aggregation pipeline execution"""
        collection = arguments.get("collection", "")
        pipeline = arguments.get("pipeline", [])

        if not collection:
            return {"success": False, "error": "No collection specified"}

        if not pipeline:
            return {"success": False, "error": "No pipeline specified"}

        # Safety check pipeline stages
        for stage in pipeline:
            if not self._is_safe_query(stage):
                return {
                    "success": False,
                    "error": "Pipeline contains unsafe operators"
                }

        result = self.connector.execute_aggregate(
            collection_name=collection,
            pipeline=pipeline,
            limit=arguments.get("limit")
        )

        # Remove DataFrame from result
        if "dataframe" in result:
            del result["dataframe"]

        return result

    def _handle_schema(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle schema retrieval"""
        try:
            schema = self.connector.get_full_schema()

            # Convert sets to lists for JSON serialization
            for coll_name, coll_info in schema.get("collections", {}).items():
                for field_name, field_info in coll_info.get("fields", {}).items():
                    if "types" in field_info and isinstance(field_info["types"], set):
                        field_info["types"] = list(field_info["types"])

            return {
                "success": True,
                "data": schema
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _handle_collections(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collection listing"""
        try:
            collections = self.connector.get_collections()
            return {
                "success": True,
                "data": {"collections": collections}
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _handle_collection_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collection info retrieval"""
        collection_name = arguments.get("collection_name", "")

        if not collection_name:
            return {"success": False, "error": "No collection name provided"}

        try:
            schema = self.connector.get_collection_schema(collection_name)

            # Convert sets to lists for JSON serialization
            for field_name, field_info in schema.get("fields", {}).items():
                if "types" in field_info and isinstance(field_info["types"], set):
                    field_info["types"] = list(field_info["types"])

            return {
                "success": True,
                "data": schema
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _is_safe_query(self, query: Dict) -> bool:
        """Check if query is safe to execute"""
        dangerous_operators = ['$where', '$function', '$accumulator']

        def check_dict(d: Dict) -> bool:
            for key, value in d.items():
                if key in dangerous_operators:
                    return False
                if isinstance(value, dict):
                    if not check_dict(value):
                        return False
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            if not check_dict(item):
                                return False
            return True

        return check_dict(query)

    def get_context(self) -> str:
        """Get database context for LLM"""
        return self.connector.get_schema_description()

    def test_connection(self) -> bool:
        """Test database connection"""
        return self.connector.test_connection()

    def close(self):
        """Close the connection"""
        self.connector.close()
