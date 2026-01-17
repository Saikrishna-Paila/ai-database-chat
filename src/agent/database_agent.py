"""
Database Agent - Main orchestrator for natural language database queries
"""

from typing import Dict, Any, Optional, List
import pandas as pd

from src.mcp import MCPManager
from src.config import settings
from src.observability import get_langfuse, QueryTracer
from src.visualization import AutoChartGenerator
from src.utils import format_results, format_sql, format_mongo_query

from .query_router import QueryRouter, IntentClassifier
from .sql_generator import SQLGenerator
from .mongo_generator import MongoQueryGenerator


class DatabaseAgent:
    """Main agent that orchestrates database queries from natural language"""

    def __init__(
        self,
        postgres_url: Optional[str] = None,
        mongodb_url: Optional[str] = None
    ):
        # Initialize MCP Manager
        self.mcp = MCPManager(
            postgres_url=postgres_url or settings.postgres_url,
            mongodb_url=mongodb_url or settings.mongodb_url
        )

        # Get available databases
        self.available_databases = self.mcp.get_available_databases()

        # Initialize router
        self.router = QueryRouter(self.available_databases)

        # Initialize intent classifier
        self.intent_classifier = IntentClassifier()

        # Initialize query generators (lazy loaded)
        self._sql_generator: Optional[SQLGenerator] = None
        self._mongo_generator: Optional[MongoQueryGenerator] = None

        # Initialize chart generator
        self.chart_generator = AutoChartGenerator()

        # Conversation history
        self.conversation_history: List[Dict] = []

        # Langfuse client
        self.langfuse = get_langfuse()

    @property
    def sql_generator(self) -> Optional[SQLGenerator]:
        """Lazy load SQL generator"""
        if self._sql_generator is None and self.mcp.postgres:
            schema = self.mcp.postgres.get_context()
            self._sql_generator = SQLGenerator(schema)
        return self._sql_generator

    @property
    def mongo_generator(self) -> Optional[MongoQueryGenerator]:
        """Lazy load MongoDB generator"""
        if self._mongo_generator is None and self.mcp.mongodb:
            schema = self.mcp.mongodb.get_context()
            self._mongo_generator = MongoQueryGenerator(schema)
        return self._mongo_generator

    def process_query(
        self,
        user_query: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a natural language query and return results"""
        tracer = QueryTracer(user_id=user_id)
        tracer.start_trace("database_query", metadata={"query": user_query})

        result = {
            "success": False,
            "query": user_query,
            "database": None,
            "generated_query": None,
            "data": [],
            "dataframe": None,
            "visualization": None,
            "explanation": None,
            "error": None
        }

        try:
            # Step 1: Fast routing (keyword-based, no LLM call)
            tracer.start_span("query_routing")
            routing = self._fast_route(user_query)
            result["database"] = routing["database"]
            tracer.end_span(output=routing)

            # Step 3: Generate query
            tracer.start_span("query_generation")
            if routing["database"] == "postgresql":
                gen_result = self._generate_postgres_query(user_query)
            else:
                gen_result = self._generate_mongodb_query(user_query)
            tracer.end_span(output=gen_result)

            if not gen_result.get("success"):
                result["error"] = gen_result.get("error", "Failed to generate query")
                tracer.log_score("query_success", 0.0, "Generation failed")
                tracer.end()
                return result

            result["generated_query"] = gen_result
            result["explanation"] = gen_result.get("explanation", "")

            # Step 4: Execute query
            tracer.start_span("query_execution")
            exec_result = self._execute_query(routing["database"], gen_result)
            tracer.end_span(output={"row_count": exec_result.get("row_count", 0)})

            if not exec_result.get("success"):
                result["error"] = exec_result.get("error", "Query execution failed")
                tracer.log_score("query_success", 0.0, "Execution failed")
                tracer.end()
                return result

            result["success"] = True
            result["data"] = exec_result.get("data", [])
            result["row_count"] = exec_result.get("row_count", 0)

            # Create DataFrame
            if result["data"]:
                result["dataframe"] = pd.DataFrame(result["data"])

            # Skip visualization for faster response

            # Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_query
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": f"Returned {result['row_count']} rows"
            })

            tracer.log_score("query_success", 1.0, "Success")

        except Exception as e:
            result["error"] = str(e)
            tracer.log_score("query_success", 0.0, str(e))

        finally:
            tracer.end()

        return result

    def _fast_route(self, user_query: str) -> Dict[str, Any]:
        """Fast keyword-based routing without LLM call"""
        query_lower = user_query.lower()

        # MongoDB keywords (events, logs, sessions, analytics, tracking)
        mongo_keywords = [
            "event", "events", "log", "logs", "session", "sessions",
            "click", "clicks", "page view", "pageview", "tracking",
            "analytics", "user activity", "behavior", "metric", "metrics"
        ]

        # PostgreSQL keywords (customers, orders, products, sales)
        postgres_keywords = [
            "customer", "customers", "order", "orders", "product", "products",
            "sale", "sales", "revenue", "purchase", "purchases", "buyer",
            "inventory", "price", "quantity", "item", "items", "spent",
            "top-selling", "best selling", "order_items"
        ]

        # Count keyword matches
        mongo_score = sum(1 for kw in mongo_keywords if kw in query_lower)
        postgres_score = sum(1 for kw in postgres_keywords if kw in query_lower)

        # Check database availability
        has_postgres = "postgresql" in self.available_databases
        has_mongo = "mongodb" in self.available_databases

        # Route based on scores and availability
        if mongo_score > postgres_score and has_mongo:
            return {"database": "mongodb", "confidence": 0.8}
        elif postgres_score > 0 and has_postgres:
            return {"database": "postgresql", "confidence": 0.8}
        elif has_postgres:
            return {"database": "postgresql", "confidence": 0.6}
        elif has_mongo:
            return {"database": "mongodb", "confidence": 0.6}
        else:
            return {"database": "postgresql", "confidence": 0.5}

    def _generate_postgres_query(self, user_query: str) -> Dict[str, Any]:
        """Generate PostgreSQL query"""
        if not self.sql_generator:
            return {"success": False, "error": "PostgreSQL not available"}

        return self.sql_generator.generate(user_query, self.conversation_history)

    def _generate_mongodb_query(self, user_query: str) -> Dict[str, Any]:
        """Generate MongoDB query"""
        if not self.mongo_generator:
            return {"success": False, "error": "MongoDB not available"}

        return self.mongo_generator.generate(user_query, self.conversation_history)

    def _execute_query(self, database: str, gen_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the generated query"""
        if database == "postgresql":
            sql = gen_result.get("sql")
            if not sql:
                return {"success": False, "error": "No SQL query generated"}
            return self.mcp.execute_tool("postgres_query", {"sql": sql})

        elif database == "mongodb":
            query_type = gen_result.get("query_type")
            collection = gen_result.get("collection")

            if not collection:
                return {"success": False, "error": "No collection specified"}

            if query_type == "find":
                return self.mcp.execute_tool("mongodb_find", {
                    "collection": collection,
                    "filter": gen_result.get("filter", {}),
                    "projection": gen_result.get("projection"),
                    "sort": gen_result.get("sort"),
                    "limit": gen_result.get("limit", settings.max_query_rows)
                })
            elif query_type == "aggregate":
                return self.mcp.execute_tool("mongodb_aggregate", {
                    "collection": collection,
                    "pipeline": gen_result.get("pipeline", []),
                    "limit": gen_result.get("limit", settings.max_query_rows)
                })
            else:
                return {"success": False, "error": f"Unknown query type: {query_type}"}

        return {"success": False, "error": f"Unknown database: {database}"}

    def get_schema_info(self) -> Dict[str, Any]:
        """Get schema information for all databases"""
        return self.mcp.get_database_info()

    def get_suggested_queries(self) -> List[str]:
        """Get suggested queries based on available schemas"""
        suggestions = []

        if self.sql_generator:
            suggestions.extend(self.sql_generator.suggest_queries(
                self.mcp.postgres.get_context()
            ))

        if self.mongo_generator:
            suggestions.extend(self.mongo_generator.suggest_queries(
                self.mcp.mongodb.get_context()
            ))

        return suggestions[:10]  # Limit to 10 suggestions

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def close(self):
        """Close all connections"""
        self.mcp.close()
