"""
Conversation Service
Handles user conversation history storage and retrieval
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..db.mongo_client import get_mongo_client

try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Service for managing user conversation history
    """
    
    def __init__(self):
        self.initialized = False
        self.conversations_collection = None
        self.mongo_client = None
        self.db = None
    
    def initialize(self):
        """Initialize service with MongoDB conversations collection"""
        try:
            if not PYMONGO_AVAILABLE:
                logger.warning("pymongo not available, conversation history disabled")
                self.initialized = False
                return
                
            from ..config import settings
            
            # Create direct MongoDB connection for conversations
            self.mongo_client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
            # Test connection
            self.mongo_client.admin.command('ping')
            
            self.db = self.mongo_client[settings.MONGODB_DB_NAME]
            self.conversations_collection = self.db["conversations"]
            self.initialized = True
            logger.info("✓ Conversation service initialized with direct MongoDB connection")
            
        except Exception as e:
            logger.warning(f"Conversation service initialization failed: {e}")
            self.initialized = False
            self.conversations_collection = None
    
    async def save_conversation(self,
                               session_id: str,
                               title: str,
                               messages: List[Dict[str, Any]],
                               user_id: str = "anonymous") -> bool:
        """
        Save or update a conversation
        
        Args:
            session_id: Unique conversation identifier
            title: Conversation title
            messages: List of message objects
            user_id: User identifier
        
        Returns:
            True if saved successfully
        """
        try:
            if not self.initialized or self.conversations_collection is None:
                logger.debug("Conversation service not available")
                return False
            
            conversation_update = {
                "session_id": session_id,
                "user_id": user_id,
                "title": title,
                "messages": messages,
                "message_count": len(messages),
                "last_updated": datetime.utcnow()
            }
            
            # Update existing conversation or insert new
            result = self.conversations_collection.update_one(
                {"session_id": session_id, "user_id": user_id},
                {
                    "$set": conversation_update, 
                    "$setOnInsert": {"created_at": datetime.utcnow()}
                },
                upsert=True
            )
            
            logger.debug(f"Conversation saved: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return False
    
    async def get_conversations(self,
                               user_id: str = "anonymous",
                               limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve user's conversation history
        
        Args:
            user_id: User identifier
            limit: Maximum number of conversations to retrieve
        
        Returns:
            List of conversation summaries
        """
        try:
            if not self.initialized or self.conversations_collection is None:
                logger.debug("Conversation service not available")
                return []
            
            cursor = self.conversations_collection.find(
                {"user_id": user_id}
            ).sort("last_updated", -1).limit(limit)
            
            conversations = []
            for doc in cursor:
                # Remove MongoDB _id and return summary
                conversations.append({
                    "session_id": doc.get("session_id"),
                    "title": doc.get("title"),
                    "message_count": doc.get("message_count", 0),
                    "last_updated": doc.get("last_updated").isoformat() if doc.get("last_updated") else None,
                    "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None
                })
            
            logger.debug(f"Retrieved {len(conversations)} conversations for user: {user_id}")
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversations: {e}")
            return []
    
    async def get_conversation(self,
                              session_id: str,
                              user_id: str = "anonymous") -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific conversation with all messages
        
        Args:
            session_id: Conversation identifier
            user_id: User identifier
        
        Returns:
            Full conversation object or None
        """
        try:
            if not self.initialized or self.conversations_collection is None:
                logger.debug("Conversation service not available")
                return None
            
            doc = self.conversations_collection.find_one({
                "session_id": session_id,
                "user_id": user_id
            })
            
            if doc:
                doc.pop("_id", None)  # Remove MongoDB ID
                # Convert datetime to ISO format
                if doc.get("last_updated"):
                    doc["last_updated"] = doc["last_updated"].isoformat()
                if doc.get("created_at"):
                    doc["created_at"] = doc["created_at"].isoformat()
                
                logger.debug(f"Retrieved conversation: {session_id}")
                return doc
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation: {e}")
            return None
    
    async def delete_conversation(self,
                                 session_id: str,
                                 user_id: str = "anonymous") -> bool:
        """
        Delete a conversation
        
        Args:
            session_id: Conversation identifier
            user_id: User identifier
        
        Returns:
            True if deleted successfully
        """
        try:
            if not self.initialized or self.conversations_collection is None:
                logger.debug("Conversation service not available")
                return False
            
            result = self.conversations_collection.delete_one({
                "session_id": session_id,
                "user_id": user_id
            })
            
            logger.debug(f"Deleted conversation: {session_id}")
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            return False
    
    def close(self):
        """Close MongoDB connection"""
        try:
            if self.mongo_client:
                self.mongo_client.close()
                logger.info("Conversation service MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing conversation service connection: {e}")


# Global service instance
conversation_service = ConversationService()
