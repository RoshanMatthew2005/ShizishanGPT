"""
User Authentication Models
Pydantic schemas for user management
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles enum"""
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    phone: Optional[str] = None
    location: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (no password)"""
    id: str
    email: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    location: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class UserUpdate(BaseModel):
    """Schema for user update"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    password: Optional[str] = None


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserInDB(BaseModel):
    """Schema for user in database"""
    email: str
    hashed_password: str
    full_name: str
    role: UserRole = UserRole.USER
    phone: Optional[str] = None
    location: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    chat_count: int = 0


class AdminUserManagement(BaseModel):
    """Schema for admin user management"""
    user_id: str
    action: str  # "activate", "deactivate", "delete", "grant_admin", "revoke_admin"
