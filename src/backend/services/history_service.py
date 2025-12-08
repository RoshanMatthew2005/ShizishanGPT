"""
History Service
Handles query history storage and retrieval
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..db.mongo_client import initialize_mongo, mongo_client

logger = logging.getLogger(__name__)


class HistoryService:
    """
    Service for query history operations
    """
    
    def __init__(self):
        self.initialized = False
    
    def initialize(self):
        """Initialize service with MongoDB"""
        try:
            from ..db.mongo_client import get_mongo_client
            client = get_mongo_client()
            if client and client.enabled:
                self.initialized = True
                logger.info("✓ History service initialized with existing MongoDB client")
            else:
                logger.warning("MongoDB client not available")
                self.initialized = False
        except Exception as e:
            logger.warning(f"MongoDB not available: {e}")
            self.initialized = False
    
    async def log_query(self,
                       endpoint: str,
                       query_data: Dict[str, Any],
                       response_data: Dict[str, Any],
                       execution_time: float,
                       user_id: Optional[str] = None) -> bool:
        """
        Log a query to history
        
        Args:
            endpoint: API endpoint
            query_data: Query parameters
            response_data: Response data
            execution_time: Execution time in seconds
            user_id: Optional user identifier
        
        Returns:
            True if logged successfully, False otherwise
        """
        try:
            if not self.initialized:
                self.initialize()
            
            if not self.initialized or mongo_client is None:
                logger.debug("MongoDB not available, skipping history logging")
                return False
            
            # Prepare log entry
            log_entry = {
                "endpoint": endpoint,
                "query": query_data,
                "response": response_data,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id or "anonymous"
            }
            
            # Log to MongoDB
            result = mongo_client.log_query(
                endpoint=endpoint,
                query=str(query_data),
                response=str(response_data),
                execution_time=execution_time,
                status="success",
                metadata={"user_id": user_id or "anonymous"}
            )
            
            if result:
                logger.debug(f"Query logged to history: {endpoint}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            return False
    
    async def get_history(self,
                         limit: int = 50,
                         user_id: Optional[str] = None,
                         endpoint: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve query history
        
        Args:
            limit: Maximum number of records to retrieve
            user_id: Filter by user ID
            endpoint: Filter by endpoint
        
        Returns:
            List of history records
        """
        try:
            if not self.initialized:
                self.initialize()
            
            if not self.initialized or mongo_client is None:
                logger.debug("MongoDB not available, returning empty history")
                return []
            
            # Build query filter
            query_filter = {}
            if user_id:
                query_filter["user_id"] = user_id
            if endpoint:
                query_filter["endpoint"] = endpoint
            
            # Retrieve from MongoDB
            history = await mongo_client.get_history(limit=limit, query_filter=query_filter)
            
            logger.debug(f"Retrieved {len(history)} history records")
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to retrieve history: {e}")
            return []
    
    async def clear_history(self, user_id: Optional[str] = None) -> int:
        """
        Clear query history
        
        Args:
            user_id: If specified, only clear this user's history
        
        Returns:
            Number of records deleted
        """
        try:
            if not self.initialized:
                self.initialize()
            
            if not self.initialized or mongo_client is None:
                logger.debug("MongoDB not available")
                return 0
            
            # Build delete filter
            delete_filter = {}
            if user_id:
                delete_filter["user_id"] = user_id
            
            # Delete from MongoDB
            if mongo_client.db is not None:
                result = mongo_client.collection.delete_many(delete_filter)
                count = result.deleted_count
                logger.info(f"Cleared {count} history records")
                return count
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            return 0


# Global service instance
history_service = HistoryService()
