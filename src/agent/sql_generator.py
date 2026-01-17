"""
SQL Generator - Converts natural language to SQL queries
"""

from typing import Dict, Any, Optional, List
import anthropic
import json
import re

from src.config import settings
from src.utils import validate_sql_safety
from src.observability import get_langfuse, QueryTracer


class SQLGenerator:
    """Generates SQL queries from natural language using Claude"""

    def __init__(self, schema_context: str):
        self.schema_context = schema_context
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def generate(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Generate SQL from natural language query"""
        tracer = QueryTracer()
        tracer.start_trace("sql_generation")

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
                name="sql_generation",
                model=self.model,
                input_messages=[{"role": "user", "content": prompt}],
                output=response.content[0].text,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )

            # Validate SQL safety
            if result.get("success") and result.get("sql"):
                safety = validate_sql_safety(result["sql"], settings.blocked_sql_keywords)
                if not safety["safe"]:
                    result = {
                        "success": False,
                        "error": safety["reason"],
                        "sql": None
                    }

            tracer.end_span(output=result)
            tracer.end()

            return result

        except Exception as e:
            tracer.end_span(output={"error": str(e)})
            tracer.end()
            return {
                "success": False,
                "error": str(e),
                "sql": None
            }

    def _build_prompt(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Build the SQL generation prompt"""
        history_context = ""
        if conversation_history:
            history_context = "\nPrevious conversation:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")[:500]
                history_context += f"{role}: {content}\n"

        return f"""You are an expert SQL query generator for PostgreSQL. Generate safe, read-only SQL queries based on natural language questions.

DATABASE SCHEMA:
{self.schema_context}

RULES:
1. Generate ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Always use proper table and column names from the schema
3. Use appropriate JOINs when querying related tables
4. Add LIMIT clause for potentially large result sets (max {settings.max_query_rows})
5. CRITICAL: When using aggregate functions (SUM, COUNT, AVG, etc.), ALWAYS include GROUP BY clause for ALL non-aggregated columns
6. Include helpful column aliases for clarity
7. Handle NULL values appropriately
8. Double-check your SQL syntax before responding

{history_context}

USER QUESTION: {user_query}

Respond in JSON format:
{{
    "sql": "the SQL query",
    "explanation": "brief explanation of what the query does",
    "tables_used": ["list", "of", "tables"],
    "estimated_complexity": "simple|medium|complex"
}}

If the question cannot be answered with the available schema, respond:
{{
    "sql": null,
    "error": "explanation of why",
    "suggestion": "what information might help"
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

            if result.get("sql"):
                # Clean up SQL
                result["sql"] = result["sql"].strip()
                result["success"] = True
            else:
                result["success"] = False

            return result

        except json.JSONDecodeError as e:
            # Try to extract SQL directly if JSON parsing fails
            sql_match = re.search(r'SELECT.*?(?:;|$)', response, re.IGNORECASE | re.DOTALL)
            if sql_match:
                return {
                    "success": True,
                    "sql": sql_match.group().strip(),
                    "explanation": "Extracted from response",
                    "tables_used": []
                }

            return {
                "success": False,
                "error": f"Failed to parse response: {str(e)}",
                "sql": None
            }

    def explain_query(self, sql: str) -> str:
        """Generate a natural language explanation of a SQL query"""
        prompt = f"""Explain this SQL query in simple terms:

```sql
{sql}
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
        prompt = f"""Based on this database schema, suggest 5 useful example queries a user might want to run:

{schema_context}

Provide queries as natural language questions (not SQL).
Format as a numbered list."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.split("\n")

        except Exception as e:
            return ["Show all records", "Count total entries"]
