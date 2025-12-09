"""
User Database Operations
Handles all user-related database operations with MongoDB
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)

try:
    from pymongo import MongoClient
    from pymongo.errors import DuplicateKeyError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    logger.warning("pymongo not installed")


class UserDatabase:
    """User database operations"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.users_collection = None
        self.connected = False
        
        if PYMONGO_AVAILABLE:
            self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            
            db_name = os.getenv("MONGODB_DB", "shizishangpt")
            self.db = self.client[db_name]
            self.users_collection = self.db["users"]
            
            # Create indexes
            self.users_collection.create_index("email", unique=True)
            self.users_collection.create_index("username", unique=True)
            
            self.connected = True
            logger.info("✓ Connected to User Database")
            
            # Create super admin if not exists
            self._create_super_admin()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.connected = False
    
    def _create_super_admin(self):
        """Create default super admin account"""
        try:
            from ..services.auth_service import auth_service
            
            super_admin = self.users_collection.find_one({"role": "super_admin"})
            if not super_admin:
                admin_data = {
                    "username": "superadmin",
                    "email": "admin@shizishangpt.com",
                    "hashed_password": auth_service.hash_password("admin123"),
                    "full_name": "Super Administrator",
                    "role": "super_admin",
                    "created_at": datetime.now(),
                    "is_active": True,
                    "login_count": 0,
                    "query_count": 0
                }
                self.users_collection.insert_one(admin_data)
                logger.info("✓ Super admin account created (admin@shizishangpt.com / admin123)")
        except Exception as e:
            logger.error(f"Error creating super admin: {e}")
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Create a new user"""
        if not self.connected:
            return None
        
        try:
            user_data["created_at"] = datetime.now()
            user_data["is_active"] = True
            user_data["login_count"] = 0
            user_data["query_count"] = 0
            
            result = self.users_collection.insert_one(user_data)
            logger.info(f"User created: {user_data['email']}")
            return str(result.inserted_id)
        except DuplicateKeyError:
            logger.error(f"User already exists: {user_data.get('email')}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        if not self.connected:
            return None
        
        try:
            user = self.users_collection.find_one({"email": email})
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
            return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        if not self.connected:
            return None
        
        try:
            user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
            return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        if not self.connected:
            return False
        
        try:
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        if not self.connected:
            return False
        
        try:
            result = self.users_collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all users (for admin)"""
        if not self.connected:
            return []
        
        try:
            users = list(self.users_collection.find().skip(skip).limit(limit))
            for user in users:
                user["id"] = str(user["_id"])
                del user["_id"]
                del user["hashed_password"]  # Don't send password hash
            return users
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
    
    def update_last_login(self, user_id: str):
        """Update user's last login time"""
        if not self.connected:
            return
        
        try:
            self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {"last_login": datetime.now()},
                    "$inc": {"login_count": 1}
                }
            )
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
    
    def increment_query_count(self, user_id: str):
        """Increment user's query count"""
        if not self.connected:
            return
        
        try:
            self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$inc": {"query_count": 1}}
            )
        except Exception as e:
            logger.error(f"Error incrementing query count: {e}")
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics for admin dashboard"""
        if not self.connected:
            return {}
        
        try:
            total_users = self.users_collection.count_documents({})
            active_users = self.users_collection.count_documents({"is_active": True})
            
            # Users created today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            new_users_today = self.users_collection.count_documents({
                "created_at": {"$gte": today_start}
            })
            
            # Total queries
            pipeline = [
                {"$group": {"_id": None, "total_queries": {"$sum": "$query_count"}}}
            ]
            result = list(self.users_collection.aggregate(pipeline))
            total_queries = result[0]["total_queries"] if result else 0
            
            avg_queries = total_queries / total_users if total_users > 0 else 0
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "new_users_today": new_users_today,
                "total_queries": total_queries,
                "average_queries_per_user": round(avg_queries, 2)
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}


# Global instance
user_db = UserDatabase()
