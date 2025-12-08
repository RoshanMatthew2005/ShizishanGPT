"""
Authentication Service
Handles user authentication, JWT tokens, password hashing
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pymongo import MongoClient
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for user authentication and authorization"""
    
    def __init__(self, mongo_client: MongoClient, db_name: str = "shizishangpt"):
        """
        Initialize auth service
        
        Args:
            mongo_client: MongoDB client instance
            db_name: Database name
        """
        self.db = mongo_client[db_name]
        self.users_collection = self.db["users"]
        
        # JWT configuration
        self.SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
        
        # Create indexes
        self.users_collection.create_index("email", unique=True)
        
        # Create superadmin if doesn't exist
        self._create_superadmin_if_not_exists()
        
        logger.info("✓ Auth service initialized")
    
    def _create_superadmin_if_not_exists(self):
        """Create default superadmin account if it doesn't exist"""
        superadmin_email = os.getenv("SUPERADMIN_EMAIL", "admin@shizishangpt.com")
        superadmin_password = os.getenv("SUPERADMIN_PASSWORD", "Admin@123456")
        
        existing = self.users_collection.find_one({"email": superadmin_email})
        if not existing:
            hashed_password = self._hash_password(superadmin_password)
            superadmin = {
                "email": superadmin_email,
                "hashed_password": hashed_password,
                "full_name": "Super Administrator",
                "role": "superadmin",
                "phone": None,
                "location": None,
                "is_active": True,
                "created_at": datetime.now(),
                "last_login": None,
                "chat_count": 0
            }
            self.users_collection.insert_one(superadmin)
            logger.info(f"✓ Superadmin created: {superadmin_email}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token
        
        Args:
            data: Data to encode in token
            expires_delta: Token expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return payload
        
        Args:
            token: JWT token
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token expired")
            return None
        except jwt.JWTError as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def register_user(self, email: str, password: str, full_name: str, 
                     phone: Optional[str] = None, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            email: User email
            password: User password
            full_name: User full name
            phone: Phone number
            location: User location
            
        Returns:
            Created user data
        """
        # Check if user exists
        existing_user = self.users_collection.find_one({"email": email})
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash password
        hashed_password = self._hash_password(password)
        
        # Create user document
        user_doc = {
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "role": "user",
            "phone": phone,
            "location": location,
            "is_active": True,
            "created_at": datetime.now(),
            "last_login": None,
            "chat_count": 0
        }
        
        result = self.users_collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        logger.info(f"✓ User registered: {email}")
        return self._format_user_response(user_doc)
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User data if authenticated, None otherwise
        """
        user = self.users_collection.find_one({"email": email})
        
        if not user:
            return None
        
        if not user.get("is_active", False):
            raise ValueError("User account is deactivated")
        
        if not self._verify_password(password, user["hashed_password"]):
            return None
        
        # Update last login
        self.users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.now()}}
        )
        
        logger.info(f"✓ User authenticated: {email}")
        return self._format_user_response(user)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                return self._format_user_response(user)
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> list:
        """Get all users (admin only)"""
        users = self.users_collection.find().skip(skip).limit(limit)
        return [self._format_user_response(user) for user in users]
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user data"""
        try:
            if "password" in update_data:
                update_data["hashed_password"] = self._hash_password(update_data.pop("password"))
            
            self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            return self.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user (admin only)"""
        try:
            result = self.users_collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    def toggle_user_status(self, user_id: str, is_active: bool) -> bool:
        """Activate/deactivate user"""
        try:
            self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_active": is_active}}
            )
            return True
        except Exception as e:
            logger.error(f"Error toggling user status: {e}")
            return False
    
    def grant_admin_role(self, user_id: str) -> bool:
        """Grant admin role to user"""
        try:
            self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"role": "admin"}}
            )
            return True
        except Exception as e:
            logger.error(f"Error granting admin role: {e}")
            return False
    
    def _format_user_response(self, user_doc: dict) -> Dict[str, Any]:
        """Format user document for response (remove password)"""
        return {
            "id": str(user_doc["_id"]),
            "email": user_doc["email"],
            "full_name": user_doc["full_name"],
            "role": user_doc["role"],
            "phone": user_doc.get("phone"),
            "location": user_doc.get("location"),
            "is_active": user_doc.get("is_active", True),
            "created_at": user_doc["created_at"],
            "last_login": user_doc.get("last_login"),
            "chat_count": user_doc.get("chat_count", 0)
        }
