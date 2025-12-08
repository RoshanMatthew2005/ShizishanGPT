"""
MongoDB Client for Logging
Handles database connections and query logging
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    logger.warning("pymongo not installed. MongoDB logging disabled.")


class MongoDBClient:
    """
    MongoDB client for logging queries and responses
    """
    
    def __init__(self, connection_string: str, db_name: str, collection_name: str, enabled: bool = True):
        self.connection_string = connection_string
        self.db_name = db_name
        self.collection_name = collection_name
        self.enabled = enabled and PYMONGO_AVAILABLE
        self.client = None
        self.db = None
        self.collection = None
        
        if self.enabled:
            self._connect()
    
    def _connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info(f"Connected to MongoDB: {self.db_name}.{self.collection_name}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"MongoDB connection failed: {e}. Logging disabled.")
            self.enabled = False
        except Exception as e:
            logger.error(f"MongoDB initialization error: {e}")
            self.enabled = False
    
    def log_query(self, 
                  endpoint: str,
                  query: str,
                  response: Any,
                  execution_time: float = 0.0,
                  status: str = "success",
                  metadata: Optional[Dict] = None) -> bool:
        """
        Log a query and its response to MongoDB
        """
        if not self.enabled:
            return False
        
        try:
            document = {
                "timestamp": datetime.utcnow(),
                "endpoint": endpoint,
                "query": query,
                "response": str(response)[:1000],  # Truncate long responses
                "execution_time": execution_time,
                "status": status,
                "metadata": metadata or {}
            }
            
            self.collection.insert_one(document)
            return True
            
        except Exception as e:
            logger.error(f"Failed to log to MongoDB: {e}")
            return False
    
    def get_history(self, 
                    limit: int = 10,
                    session_id: Optional[str] = None,
                    endpoint: Optional[str] = None) -> List[Dict]:
        """
        Retrieve query history from MongoDB
        """
        if not self.enabled:
            return []
        
        try:
            query_filter = {}
            
            if session_id:
                query_filter["metadata.session_id"] = session_id
            
            if endpoint:
                query_filter["endpoint"] = endpoint
            
            cursor = self.collection.find(query_filter).sort("timestamp", -1).limit(limit)
            
            results = []
            for doc in cursor:
                doc.pop("_id", None)  # Remove MongoDB ObjectId
                results.append(doc)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve history: {e}")
            return []
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global MongoDB client instance (initialized in main.py)
mongo_client: Optional[MongoDBClient] = None


def get_mongo_client() -> Optional[MongoDBClient]:
    """Get the global MongoDB client"""
    return mongo_client


def initialize_mongo(connection_string: str, db_name: str, collection_name: str, enabled: bool = True):
    """Initialize the global MongoDB client"""
    global mongo_client
    mongo_client = MongoDBClient(connection_string, db_name, collection_name, enabled)
    return mongo_client
