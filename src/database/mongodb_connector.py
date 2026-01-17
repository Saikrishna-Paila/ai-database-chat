"""
MongoDB Database Connector
"""

from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import pandas as pd

from src.config import settings


class MongoDBConnector:
    """Handles MongoDB database connections and operations"""

    def __init__(self, connection_url: Optional[str] = None):
        self.connection_url = connection_url or settings.mongodb_url
        self.db_name = settings.mongodb_db
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None

    @property
    def client(self) -> MongoClient:
        """Lazy load MongoDB client"""
        if self._client is None:
            self._client = MongoClient(
                self.connection_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
        return self._client

    @property
    def db(self) -> Database:
        """Get database instance"""
        if self._db is None:
            self._db = self.client[self.db_name]
        return self._db

    def test_connection(self) -> bool:
        """Test if database connection is working"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            return False

    def get_collections(self) -> List[str]:
        """Get list of all collections in the database"""
        return self.db.list_collection_names()

    def get_collection_schema(self, collection_name: str) -> Dict[str, Any]:
        """Get schema information for a collection by sampling documents"""
        collection = self.db[collection_name]

        # Get sample documents to infer schema
        sample_docs = list(collection.find().limit(10))

        # Infer fields from sample documents
        fields = {}
        for doc in sample_docs:
            self._extract_fields(doc, fields)

        # Get document count
        doc_count = collection.count_documents({})

        # Get sample data (without _id for cleaner output)
        sample_data = []
        for doc in sample_docs[:3]:
            doc_copy = dict(doc)
            if '_id' in doc_copy:
                doc_copy['_id'] = str(doc_copy['_id'])
            sample_data.append(doc_copy)

        # Get indexes
        indexes = list(collection.list_indexes())
        index_info = [
            {"name": idx["name"], "keys": list(idx["key"].keys())}
            for idx in indexes
        ]

        return {
            "collection_name": collection_name,
            "fields": fields,
            "document_count": doc_count,
            "sample_data": sample_data,
            "indexes": index_info
        }

    def _extract_fields(self, doc: Dict, fields: Dict, prefix: str = ""):
        """Recursively extract fields and their types from a document"""
        for key, value in doc.items():
            field_name = f"{prefix}.{key}" if prefix else key
            field_type = type(value).__name__

            if field_name not in fields:
                fields[field_name] = {"types": set(), "sample_values": []}

            fields[field_name]["types"].add(field_type)

            # Store sample values (limit to 3)
            if len(fields[field_name]["sample_values"]) < 3:
                if field_type not in ['dict', 'list']:
                    sample = str(value)[:50]  # Truncate long values
                    if sample not in fields[field_name]["sample_values"]:
                        fields[field_name]["sample_values"].append(sample)

            # Recurse into nested documents
            if isinstance(value, dict):
                self._extract_fields(value, fields, field_name)

    def get_full_schema(self) -> Dict[str, Any]:
        """Get complete database schema"""
        collections = self.get_collections()
        schema = {
            "database": self.db_name,
            "collections": {}
        }

        for collection in collections:
            schema["collections"][collection] = self.get_collection_schema(collection)

        return schema

    def execute_find(
        self,
        collection_name: str,
        filter_query: Dict = None,
        projection: Dict = None,
        sort: List = None,
        limit: int = None
    ) -> Dict[str, Any]:
        """Execute a find query"""
        try:
            collection = self.db[collection_name]
            filter_query = filter_query or {}
            limit = limit or settings.max_query_rows

            cursor = collection.find(filter_query, projection)

            if sort:
                cursor = cursor.sort(sort)

            cursor = cursor.limit(limit)

            # Convert to list and handle ObjectId
            data = []
            for doc in cursor:
                doc_copy = dict(doc)
                if '_id' in doc_copy:
                    doc_copy['_id'] = str(doc_copy['_id'])
                data.append(doc_copy)

            df = pd.DataFrame(data) if data else pd.DataFrame()

            return {
                "success": True,
                "data": data,
                "dataframe": df,
                "row_count": len(data)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "row_count": 0
            }

    def execute_aggregate(
        self,
        collection_name: str,
        pipeline: List[Dict],
        limit: int = None
    ) -> Dict[str, Any]:
        """Execute an aggregation pipeline"""
        try:
            collection = self.db[collection_name]
            limit = limit or settings.max_query_rows

            # Add limit stage if not present
            has_limit = any('$limit' in stage for stage in pipeline)
            if not has_limit:
                pipeline.append({'$limit': limit})

            cursor = collection.aggregate(pipeline)

            # Convert to list
            data = []
            for doc in cursor:
                doc_copy = dict(doc)
                if '_id' in doc_copy:
                    doc_copy['_id'] = str(doc_copy['_id'])
                data.append(doc_copy)

            df = pd.DataFrame(data) if data else pd.DataFrame()

            return {
                "success": True,
                "data": data,
                "dataframe": df,
                "row_count": len(data)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "row_count": 0
            }

    def execute_query(
        self,
        query_type: str,
        collection_name: str,
        query: Dict
    ) -> Dict[str, Any]:
        """Generic query executor"""
        if query_type == "find":
            return self.execute_find(
                collection_name,
                filter_query=query.get("filter"),
                projection=query.get("projection"),
                sort=query.get("sort"),
                limit=query.get("limit")
            )
        elif query_type == "aggregate":
            return self.execute_aggregate(
                collection_name,
                pipeline=query.get("pipeline", []),
                limit=query.get("limit")
            )
        else:
            return {
                "success": False,
                "error": f"Unknown query type: {query_type}",
                "data": [],
                "row_count": 0
            }

    def get_schema_description(self) -> str:
        """Get a formatted string description of the schema for LLM context"""
        schema = self.get_full_schema()
        description = f"MongoDB Database: {schema['database']}\n\n"

        for coll_name, coll_info in schema["collections"].items():
            description += f"Collection: {coll_name}\n"
            description += f"  Document Count: {coll_info['document_count']}\n"
            description += "  Fields:\n"

            # Convert fields dict to readable format
            for field_name, field_info in coll_info.get("fields", {}).items():
                types = list(field_info.get("types", set()))
                types_str = "/".join(types) if types else "unknown"
                description += f"    - {field_name}: {types_str}\n"

            if coll_info.get("indexes"):
                description += "  Indexes:\n"
                for idx in coll_info["indexes"]:
                    description += f"    - {idx['name']}: {idx['keys']}\n"

            description += "\n"

        return description

    def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
