"""
User Model and Authentication
Handles user data, authentication, and super admin functionality
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserCreate(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    location: Optional[str] = None
    farm_size: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    farm_size: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user data response"""
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    location: Optional[str] = None
    farm_size: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True


class UserInDB(BaseModel):
    """Internal user model with hashed password"""
    username: str
    email: str
    hashed_password: str
    full_name: str
    role: UserRole = UserRole.USER
    phone: Optional[str] = None
    location: Optional[str] = None
    farm_size: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True
    login_count: int = 0
    query_count: int = 0


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserStats(BaseModel):
    """User statistics for admin dashboard"""
    total_users: int
    active_users: int
    new_users_today: int
    total_queries: int
    average_queries_per_user: float
