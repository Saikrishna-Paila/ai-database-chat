"""
Query Router - Determines which database to query based on user intent
"""

from typing import Dict, Any, Optional, List
import anthropic
import json

from src.config import settings
from src.observability import get_langfuse


class QueryRouter:
    """Routes natural language queries to the appropriate database"""

    def __init__(self, available_databases: List[str]):
        self.available_databases = available_databases
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
        self.langfuse = get_langfuse()

    def route_query(
        self,
        user_query: str,
        schema_context: str
    ) -> Dict[str, Any]:
        """Determine which database should handle the query"""

        # If only one database available, route to it
        if len(self.available_databases) == 1:
            return {
                "database": self.available_databases[0],
                "confidence": 1.0,
                "reasoning": "Only one database available"
            }

        # Use LLM to determine routing
        routing_prompt = self._build_routing_prompt(user_query, schema_context)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": routing_prompt}
                ]
            )

            result = self._parse_routing_response(response.content[0].text)
            return result

        except Exception as e:
            # Default to first available database on error
            return {
                "database": self.available_databases[0],
                "confidence": 0.5,
                "reasoning": f"Routing error, defaulting: {str(e)}"
            }

    def _build_routing_prompt(self, user_query: str, schema_context: str) -> str:
        """Build the routing prompt for the LLM"""
        db_descriptions = {
            "postgresql": "SQL relational database with structured tables, relationships, and ACID compliance. Best for: transactional data, joins, aggregations, complex queries.",
            "mongodb": "NoSQL document database with flexible schema. Best for: document storage, nested data, unstructured data, flexible queries."
        }

        available_desc = "\n".join([
            f"- {db}: {db_descriptions.get(db, 'Database')}"
            for db in self.available_databases
        ])

        return f"""You are a database routing expert. Analyze the user's query and determine which database is most appropriate.

Available Databases:
{available_desc}

Database Schema:
{schema_context}

User Query: "{user_query}"

Respond in JSON format only:
{{
    "database": "postgresql" or "mongodb",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Consider:
1. Which database has the relevant data/tables/collections
2. Query complexity and type (analytical, transactional, document-based)
3. Data structure (relational vs document)

JSON Response:"""

    def _parse_routing_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM routing response"""
        try:
            # Try to extract JSON from response
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]

            result = json.loads(response)

            # Validate response
            if result.get("database") not in self.available_databases:
                result["database"] = self.available_databases[0]
                result["confidence"] = 0.5

            return result

        except json.JSONDecodeError:
            # Default response on parse error
            return {
                "database": self.available_databases[0],
                "confidence": 0.5,
                "reasoning": "Failed to parse routing response"
            }


class IntentClassifier:
    """Classifies user intent for better query handling"""

    INTENT_TYPES = [
        "data_retrieval",    # Simple SELECT/find queries
        "aggregation",       # GROUP BY, COUNT, SUM, aggregation pipelines
        "comparison",        # Comparing data across tables/collections
        "time_series",       # Time-based queries
        "search",            # Text search queries
        "schema_info",       # Questions about database structure
        "explanation"        # Questions about data meaning
    ]

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def classify(self, user_query: str) -> Dict[str, Any]:
        """Classify the intent of a user query"""
        prompt = f"""Classify the following database query intent.

Query: "{user_query}"

Intent types:
- data_retrieval: Simple data fetch (SELECT, find)
- aggregation: Grouping, counting, summing
- comparison: Comparing data points
- time_series: Time-based analysis
- search: Text/keyword search
- schema_info: Questions about database structure
- explanation: Questions about what data means

Respond in JSON format:
{{
    "primary_intent": "intent_type",
    "requires_visualization": true/false,
    "complexity": "simple" | "medium" | "complex"
}}

JSON Response:"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )

            return self._parse_intent_response(response.content[0].text)

        except Exception as e:
            return {
                "primary_intent": "data_retrieval",
                "requires_visualization": False,
                "complexity": "simple"
            }

    def _parse_intent_response(self, response: str) -> Dict[str, Any]:
        """Parse intent classification response"""
        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]

            return json.loads(response)

        except json.JSONDecodeError:
            return {
                "primary_intent": "data_retrieval",
                "requires_visualization": False,
                "complexity": "simple"
            }
