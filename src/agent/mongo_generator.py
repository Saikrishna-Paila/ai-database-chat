"""
MongoDB Query Generator - Converts natural language to MongoDB queries
"""

from typing import Dict, Any, Optional, List
import anthropic
import json

from src.config import settings
from src.utils import validate_mongo_safety
from src.observability import get_langfuse, QueryTracer


class MongoQueryGenerator:
    """Generates MongoDB queries from natural language using Claude"""

    def __init__(self, schema_context: str):
        self.schema_context = schema_context
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def generate(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Generate MongoDB query from natural language"""
        tracer = QueryTracer()
        tracer.start_trace("mongo_generation")

        prompt = self._build_prompt(user_query, conversation_history)

        tracer.start_span("llm_call", input_data={"query": user_query})

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            result = self._parse_response(response.content[0].text)

            # Log generation
            tracer.log_generation(
                name="mongo_generation",
                model=self.model,
                input_messages=[{"role": "user", "content": prompt}],
                output=response.content[0].text,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )

            # Validate query safety
            if result.get("success"):
                query_to_check = result.get("filter", result.get("pipeline", {}))
                if isinstance(query_to_check, list):
                    for stage in query_to_check:
                        safety = validate_mongo_safety(stage)
                        if not safety["safe"]:
                            result = {
                                "success": False,
                                "error": safety["reason"]
                            }
                            break
                else:
                    safety = validate_mongo_safety(query_to_check)
                    if not safety["safe"]:
                        result = {
                            "success": False,
                            "error": safety["reason"]
                        }

            tracer.end_span(output=result)
            tracer.end()

            return result

        except Exception as e:
            tracer.end_span(output={"error": str(e)})
            tracer.end()
            return {
                "success": False,
                "error": str(e)
            }

    def _build_prompt(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Build the MongoDB query generation prompt"""
        history_context = ""
        if conversation_history:
            history_context = "\nPrevious conversation:\n"
            for msg in conversation_history[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")[:500]
                history_context += f"{role}: {content}\n"

        return f"""You are an expert MongoDB query generator. Generate safe, read-only MongoDB queries based on natural language questions.

DATABASE SCHEMA:
{self.schema_context}

RULES:
1. Generate ONLY read operations (find, aggregate) - no insert, update, delete
2. Use proper collection and field names from the schema
3. Use aggregation pipeline for complex queries (grouping, counting, sorting)
4. Add $limit stage for potentially large result sets (max {settings.max_query_rows})
5. Never use dangerous operators like $where or $function
6. Handle nested documents appropriately using dot notation

{history_context}

USER QUESTION: {user_query}

Respond in JSON format. For simple queries:
{{
    "query_type": "find",
    "collection": "collection_name",
    "filter": {{}},
    "projection": {{}},
    "sort": [["field", 1]],
    "limit": 100,
    "explanation": "what the query does"
}}

For aggregation queries:
{{
    "query_type": "aggregate",
    "collection": "collection_name",
    "pipeline": [
        {{"$match": {{}}}},
        {{"$group": {{}}}},
        {{"$limit": 100}}
    ],
    "explanation": "what the query does"
}}

If the question cannot be answered:
{{
    "query_type": null,
    "error": "explanation",
    "suggestion": "what might help"
}}

JSON Response:"""

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response"""
        try:
            # Clean up response
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
                if response.startswith("json"):
                    response = response[4:]

            result = json.loads(response)

            if result.get("query_type"):
                result["success"] = True
            else:
                result["success"] = False

            return result

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse response: {str(e)}"
            }

    def explain_query(self, query: Dict[str, Any]) -> str:
        """Generate natural language explanation of a MongoDB query"""
        query_str = json.dumps(query, indent=2)

        prompt = f"""Explain this MongoDB query in simple terms:

```json
{query_str}
```

Provide a brief, clear explanation of what the query does and what results it will return."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        except Exception as e:
            return f"Could not explain query: {str(e)}"

    def suggest_queries(self, schema_context: str) -> List[str]:
        """Suggest example queries based on the schema"""
        prompt = f"""Based on this MongoDB schema, suggest 5 useful example queries a user might want to run:

{schema_context}

Provide queries as natural language questions (not MongoDB syntax).
Format as a numbered list."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.split("\n")

        except Exception as e:
            return ["Show all documents", "Count total documents"]
