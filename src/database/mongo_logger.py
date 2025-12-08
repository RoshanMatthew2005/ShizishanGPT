"""
MongoDB Logger
Logs queries and responses to MongoDB database.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json


class MongoLogger:
    """Logs conversations and interactions to MongoDB."""
    
    def __init__(self, 
                 connection_string: str = "mongodb://localhost:27017/",
                 database_name: str = "shizishanGPT",
                 collection_name: str = "conversations"):
        """
        Initialize the MongoDB logger.
        
        Args:
            connection_string: MongoDB connection string
            database_name: Database name
            collection_name: Collection name for conversations
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.collection_name = collection_name
        
        self.client = None
        self.db = None
        self.collection = None
        self.is_connected = False
        
        # Try to import pymongo
        try:
            import pymongo
            self.pymongo = pymongo
            self._available = True
        except ImportError:
            print("⚠ pymongo not installed. Install with: pip install pymongo")
            print("⚠ Logging will be disabled")
            self._available = False
    
    def connect(self) -> bool:
        """
        Connect to MongoDB.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._available:
            return False
        
        try:
            self.client = self.pymongo.MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            self.client.server_info()
            
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            self.is_connected = True
            print(f"✓ Connected to MongoDB: {self.database_name}.{self.collection_name}")
            return True
            
        except Exception as e:
            print(f"⚠ Failed to connect to MongoDB: {e}")
            print(f"⚠ Logging will be disabled")
            return False
    
    def log_query(self, 
                  query: str, 
                  response: str,
                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log a query and response to MongoDB.
        
        Args:
            query: User query
            response: System response
            metadata: Optional metadata (tools used, execution time, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            if not self.connect():
                # Fallback to console logging
                self._log_to_console(query, response, metadata)
                return False
        
        try:
            document = {
                "query": query,
                "response": response,
                "metadata": metadata or {},
                "timestamp": datetime.now()
            }
            
            self.collection.insert_one(document)
            return True
            
        except Exception as e:
            print(f"⚠ Failed to log to MongoDB: {e}")
            self._log_to_console(query, response, metadata)
            return False
    
    def _log_to_console(self, 
                       query: str, 
                       response: str, 
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Fallback console logging when MongoDB is unavailable.
        
        Args:
            query: User query
            response: System response
            metadata: Optional metadata
        """
        print("\n" + "="*70)
        print("CONVERSATION LOG (Console Fallback)")
        print("="*70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Query: {query}")
        print(f"Response: {response[:200]}...")
        if metadata:
            print(f"Metadata: {json.dumps(metadata, indent=2)}")
        print("="*70 + "\n")
    
    def get_recent_queries(self, limit: int = 10) -> list:
        """
        Get recent queries from database.
        
        Args:
            limit: Number of queries to retrieve
            
        Returns:
            List of query documents
        """
        if not self.is_connected:
            return []
        
        try:
            cursor = self.collection.find().sort("timestamp", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"⚠ Failed to retrieve queries: {e}")
            return []
    
    def search_queries(self, keyword: str, limit: int = 20) -> list:
        """
        Search queries by keyword.
        
        Args:
            keyword: Keyword to search for
            limit: Maximum results
            
        Returns:
            List of matching documents
        """
        if not self.is_connected:
            return []
        
        try:
            query = {"query": {"$regex": keyword, "$options": "i"}}
            cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"⚠ Failed to search queries: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get logging statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self.is_connected:
            return {
                "connected": False,
                "total_logs": 0
            }
        
        try:
            total = self.collection.count_documents({})
            
            return {
                "connected": True,
                "total_logs": total,
                "database": self.database_name,
                "collection": self.collection_name
            }
        except Exception as e:
            print(f"⚠ Failed to get stats: {e}")
            return {"connected": False, "error": str(e)}
    
    def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.is_connected = False
            print("✓ MongoDB connection closed")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()


# Example usage
if __name__ == "__main__":
    logger = MongoLogger()
    
    # Test connection
    if logger.connect():
        # Log a test query
        success = logger.log_query(
            query="What fertilizers for rice?",
            response="Use NPK fertilizers with 4:2:1 ratio",
            metadata={
                "tool": "rag_retrieval",
                "execution_time": 1.23,
                "confidence": 0.85
            }
        )
        
        print(f"\nLog successful: {success}")
        
        # Get stats
        stats = logger.get_stats()
        print(f"\nStats: {stats}")
        
        # Get recent queries
        recent = logger.get_recent_queries(5)
        print(f"\nRecent queries: {len(recent)}")
        
        logger.close()
    else:
        print("\nMongoDB not available - using console fallback")
        logger._log_to_console(
            "Test query",
            "Test response",
            {"tool": "test"}
        )
