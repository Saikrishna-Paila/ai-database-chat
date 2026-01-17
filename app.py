"""
AI Database Chat - Chainlit Frontend
Natural language interface for querying PostgreSQL and MongoDB
"""

import chainlit as cl
from typing import Optional
import pandas as pd
import json

from src.agent import DatabaseAgent
from src.config import settings
from src.utils import format_sql, format_mongo_query


# Global agent instance
agent: Optional[DatabaseAgent] = None


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session"""
    global agent

    # Send welcome message
    await cl.Message(
        content="# Welcome to AI Database Chat\n\nI can help you query your databases using natural language. Just ask me questions about your data!"
    ).send()

    # Initialize agent
    try:
        agent = DatabaseAgent()

        # Check database connections
        connections = agent.mcp.test_connections()
        status_parts = []

        if connections.get("postgresql"):
            status_parts.append("PostgreSQL: Connected")
        else:
            status_parts.append("PostgreSQL: Not connected")

        if connections.get("mongodb"):
            status_parts.append("MongoDB: Connected")
        else:
            status_parts.append("MongoDB: Not connected")

        status_msg = "**Database Status:**\n- " + "\n- ".join(status_parts)
        await cl.Message(content=status_msg).send()

        # Show available tables/collections
        db_info = agent.get_schema_info()
        if db_info.get("databases"):
            info_parts = []
            for db in db_info["databases"]:
                if db["type"] == "postgresql" and db.get("tables"):
                    info_parts.append(f"**PostgreSQL Tables:** {', '.join(db['tables'])}")
                if db["type"] == "mongodb" and db.get("collections"):
                    info_parts.append(f"**MongoDB Collections:** {', '.join(db['collections'])}")

            if info_parts:
                await cl.Message(content="\n".join(info_parts)).send()

        # Show suggested queries
        suggestions = agent.get_suggested_queries()
        if suggestions:
            suggestions_text = "**Example questions you can ask:**\n"
            for i, s in enumerate(suggestions[:5], 1):
                if s.strip():
                    suggestions_text += f"{i}. {s.strip()}\n"
            await cl.Message(content=suggestions_text).send()

    except Exception as e:
        await cl.Message(
            content=f"Error initializing database connections: {str(e)}\n\nPlease check your configuration."
        ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages"""
    global agent

    if agent is None:
        await cl.Message(content="Agent not initialized. Please refresh the page.").send()
        return

    user_query = message.content.strip()

    # Handle special commands
    if user_query.lower() in ["/help", "help"]:
        await show_help()
        return

    if user_query.lower() in ["/schema", "schema"]:
        await show_schema()
        return

    if user_query.lower() in ["/clear", "clear"]:
        agent.clear_history()
        await cl.Message(content="Conversation history cleared.").send()
        return

    # Process the query
    thinking_msg = cl.Message(content="Analyzing your question...")
    await thinking_msg.send()

    try:
        result = agent.process_query(user_query)

        # Remove thinking message
        await thinking_msg.remove()

        # Build response
        response_parts = []

        if result.get("success"):
            # Show which database was used
            db_used = result.get("database", "unknown")
            response_parts.append(f"**Database:** {db_used.upper()}")

            # Show generated query
            if result.get("generated_query"):
                gen_query = result["generated_query"]
                if db_used == "postgresql" and gen_query.get("sql"):
                    sql_formatted = format_sql(gen_query["sql"])
                    response_parts.append(f"\n**Generated SQL:**\n```sql\n{sql_formatted}\n```")
                elif db_used == "mongodb":
                    if gen_query.get("query_type") == "find":
                        query_display = {
                            "collection": gen_query.get("collection"),
                            "filter": gen_query.get("filter", {}),
                            "projection": gen_query.get("projection"),
                            "sort": gen_query.get("sort"),
                            "limit": gen_query.get("limit")
                        }
                    else:
                        query_display = {
                            "collection": gen_query.get("collection"),
                            "pipeline": gen_query.get("pipeline", [])
                        }
                    response_parts.append(f"\n**Generated MongoDB Query:**\n```json\n{format_mongo_query(query_display)}\n```")

            # Show explanation
            if result.get("explanation"):
                response_parts.append(f"\n**Explanation:** {result['explanation']}")

            # Show row count
            row_count = result.get("row_count", 0)
            response_parts.append(f"\n**Results:** {row_count} rows returned")

            # Send main response
            await cl.Message(content="\n".join(response_parts)).send()

            # Show data as table
            if result.get("dataframe") is not None and len(result["dataframe"]) > 0:
                df = result["dataframe"]

                # Limit display to first 20 rows
                display_df = df.head(20)

                # Create markdown table
                table_md = display_df.to_markdown(index=False)
                await cl.Message(content=f"**Data Preview:**\n\n{table_md}").send()

                if len(df) > 20:
                    await cl.Message(content=f"*Showing first 20 of {len(df)} rows*").send()

            # Show visualization if available (disabled for performance)
            # if result.get("visualization"):
            #     fig = result["visualization"]
            #     elements = [cl.Plotly(name="chart", figure=fig)]
            #     await cl.Message(content="**Visualization:**", elements=elements).send()

        else:
            # Show error
            error_msg = result.get("error", "Unknown error occurred")
            await cl.Message(content=f"**Error:** {error_msg}").send()

            # Show suggestion if available
            if result.get("generated_query", {}).get("suggestion"):
                await cl.Message(
                    content=f"**Suggestion:** {result['generated_query']['suggestion']}"
                ).send()

    except Exception as e:
        await thinking_msg.remove()
        await cl.Message(content=f"**Error processing query:** {str(e)}").send()


async def show_help():
    """Show help message"""
    help_text = """# AI Database Chat Help

## How to Use
Simply type your questions in natural language. The AI will:
1. Understand your intent
2. Route to the appropriate database (PostgreSQL or MongoDB)
3. Generate and execute the query
4. Display results with optional visualizations

## Example Questions
- "Show me all users who signed up this month"
- "What are the top 10 products by sales?"
- "Count orders by status"
- "Find customers from New York"
- "What's the average order value?"

## Commands
- `/help` - Show this help message
- `/schema` - Show database schema
- `/clear` - Clear conversation history

## Tips
- Be specific about what data you want
- Mention table/collection names if you know them
- Ask for aggregations using words like "count", "sum", "average"
- Request visualizations by asking "show me a chart of..."
"""
    await cl.Message(content=help_text).send()


async def show_schema():
    """Show database schema"""
    global agent

    if agent is None:
        await cl.Message(content="Agent not initialized.").send()
        return

    schema_context = agent.mcp.get_combined_context()
    await cl.Message(content=f"# Database Schema\n\n```\n{schema_context}\n```").send()


@cl.on_chat_end
async def on_chat_end():
    """Clean up on chat end"""
    global agent
    if agent:
        agent.close()
        agent = None


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
