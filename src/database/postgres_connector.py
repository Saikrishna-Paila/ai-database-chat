"""
PostgreSQL Database Connector
"""

from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text, inspect, MetaData
from sqlalchemy.engine import Engine
import pandas as pd

from src.config import settings


class PostgresConnector:
    """Handles PostgreSQL database connections and operations"""

    def __init__(self, connection_url: Optional[str] = None):
        self.connection_url = connection_url or settings.postgres_url
        self._engine: Optional[Engine] = None
        self._inspector = None
        self._metadata = None

    @property
    def engine(self) -> Engine:
        """Lazy load database engine"""
        if self._engine is None:
            self._engine = create_engine(
                self.connection_url,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800
            )
        return self._engine

    @property
    def inspector(self):
        """Get SQLAlchemy inspector for schema introspection"""
        if self._inspector is None:
            self._inspector = inspect(self.engine)
        return self._inspector

    def test_connection(self) -> bool:
        """Test if database connection is working"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            return False

    def get_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        return self.inspector.get_table_names()

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get detailed schema information for a table"""
        columns = []
        for col in self.inspector.get_columns(table_name):
            columns.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "default": str(col.get("default", "")) if col.get("default") else None,
                "primary_key": col.get("primary_key", False)
            })

        # Get primary keys
        pk_constraint = self.inspector.get_pk_constraint(table_name)
        primary_keys = pk_constraint.get("constrained_columns", []) if pk_constraint else []

        # Get foreign keys
        foreign_keys = []
        for fk in self.inspector.get_foreign_keys(table_name):
            foreign_keys.append({
                "columns": fk["constrained_columns"],
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"]
            })

        # Get sample data
        sample_data = self.get_sample_data(table_name, limit=3)

        # Get row count
        row_count = self.get_row_count(table_name)

        return {
            "table_name": table_name,
            "columns": columns,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys,
            "sample_data": sample_data,
            "row_count": row_count
        }

    def get_full_schema(self) -> Dict[str, Any]:
        """Get complete database schema"""
        tables = self.get_tables()
        schema = {
            "database": settings.postgres_db,
            "tables": {}
        }

        for table in tables:
            schema["tables"][table] = self.get_table_schema(table)

        return schema

    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict]:
        """Get sample rows from a table"""
        try:
            query = f'SELECT * FROM "{table_name}" LIMIT {limit}'
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                columns = result.keys()
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Error getting sample data: {e}")
            return []

    def get_row_count(self, table_name: str) -> int:
        """Get total row count for a table"""
        try:
            query = f'SELECT COUNT(*) FROM "{table_name}"'
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return result.scalar()
        except Exception as e:
            print(f"Error getting row count: {e}")
            return 0

    def execute_query(
        self,
        sql: str,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute a SQL query and return results"""
        timeout = timeout or settings.query_timeout_seconds

        try:
            with self.engine.connect() as conn:
                # Set statement timeout
                conn.execute(text(f"SET statement_timeout = {timeout * 1000}"))

                # Execute query
                result = conn.execute(text(sql))
                columns = list(result.keys())
                rows = result.fetchall()

                # Convert to list of dicts
                data = [dict(zip(columns, row)) for row in rows]

                # Also create DataFrame for easy manipulation
                df = pd.DataFrame(data) if data else pd.DataFrame()

                return {
                    "success": True,
                    "data": data,
                    "dataframe": df,
                    "columns": columns,
                    "row_count": len(data)
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "columns": [],
                "row_count": 0
            }

    def get_schema_description(self) -> str:
        """Get a formatted string description of the schema for LLM context"""
        schema = self.get_full_schema()
        description = f"PostgreSQL Database: {schema['database']}\n\n"

        for table_name, table_info in schema["tables"].items():
            description += f"Table: {table_name}\n"
            description += f"  Row Count: {table_info['row_count']}\n"
            description += "  Columns:\n"

            for col in table_info["columns"]:
                pk_marker = " (PK)" if col["name"] in table_info["primary_keys"] else ""
                description += f"    - {col['name']}: {col['type']}{pk_marker}\n"

            if table_info["foreign_keys"]:
                description += "  Foreign Keys:\n"
                for fk in table_info["foreign_keys"]:
                    description += f"    - {fk['columns']} -> {fk['referred_table']}.{fk['referred_columns']}\n"

            description += "\n"

        return description

    def close(self):
        """Close database connection"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
