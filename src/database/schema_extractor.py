"""
Unified Schema Extractor for PostgreSQL and MongoDB
"""

from typing import Dict, Any, Optional
from .postgres_connector import PostgresConnector
from .mongodb_connector import MongoDBConnector


class SchemaExtractor:
    """Extracts and formats schema information from both databases"""

    def __init__(
        self,
        postgres_connector: Optional[PostgresConnector] = None,
        mongodb_connector: Optional[MongoDBConnector] = None
    ):
        self.postgres = postgres_connector
        self.mongodb = mongodb_connector

    def get_postgres_schema(self) -> Optional[Dict[str, Any]]:
        """Get PostgreSQL schema if connector is available"""
        if self.postgres:
            return self.postgres.get_full_schema()
        return None

    def get_mongodb_schema(self) -> Optional[Dict[str, Any]]:
        """Get MongoDB schema if connector is available"""
        if self.mongodb:
            return self.mongodb.get_full_schema()
        return None

    def get_combined_schema(self) -> Dict[str, Any]:
        """Get combined schema from all available databases"""
        schema = {
            "databases": []
        }

        if self.postgres:
            pg_schema = self.get_postgres_schema()
            if pg_schema:
                schema["databases"].append({
                    "type": "postgresql",
                    "name": pg_schema.get("database", "postgres"),
                    "schema": pg_schema
                })

        if self.mongodb:
            mongo_schema = self.get_mongodb_schema()
            if mongo_schema:
                schema["databases"].append({
                    "type": "mongodb",
                    "name": mongo_schema.get("database", "mongodb"),
                    "schema": mongo_schema
                })

        return schema

    def get_schema_for_llm(self) -> str:
        """Get formatted schema description for LLM context"""
        descriptions = []

        if self.postgres:
            descriptions.append("=== PostgreSQL Database ===")
            descriptions.append(self.postgres.get_schema_description())

        if self.mongodb:
            descriptions.append("=== MongoDB Database ===")
            descriptions.append(self.mongodb.get_schema_description())

        return "\n".join(descriptions)

    def get_table_names(self) -> Dict[str, list]:
        """Get all table/collection names from both databases"""
        names = {
            "postgresql_tables": [],
            "mongodb_collections": []
        }

        if self.postgres:
            names["postgresql_tables"] = self.postgres.get_tables()

        if self.mongodb:
            names["mongodb_collections"] = self.mongodb.get_collections()

        return names

    def get_available_databases(self) -> list:
        """Get list of available database types"""
        available = []
        if self.postgres:
            available.append("postgresql")
        if self.mongodb:
            available.append("mongodb")
        return available
