"""
Authentication Router
Handles user registration, login, and management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import logging
from pymongo import MongoClient

from ..models.auth_schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    UserUpdate, AdminUserManagement
)
from ..services.auth_service import AuthService
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()


# Dependency to get auth service
def get_auth_service() -> AuthService:
    """Get auth service instance with direct MongoDB connection"""
    # Create direct MongoDB connection for auth service
    mongo_client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
    return AuthService(mongo_client, settings.MONGODB_DB_NAME)


# Dependency to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


# Dependency to check if user is admin
async def require_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Require admin or superadmin role"""
    if current_user["role"] not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user
    
    - Creates new user account
    - Returns JWT access token
    """
    try:
        user = auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            location=user_data.location
        )
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": user["id"], "email": user["email"], "role": user["role"]}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login user
    
    - Authenticates user with email and password
    - Returns JWT access token
    """
    try:
        user = auth_service.authenticate_user(
            email=credentials.email,
            password=credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": user["id"], "email": user["email"], "role": user["role"]}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update current user information"""
    update_dict = update_data.dict(exclude_unset=True)
    updated_user = auth_service.update_user(current_user["id"], update_dict)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update failed"
        )
    
    return updated_user


# Admin endpoints
@router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    admin_user: dict = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get all users (Admin only)"""
    users = auth_service.get_all_users(skip=skip, limit=limit)
    return users


@router.post("/admin/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    admin_user: dict = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Create new user (Admin only)"""
    try:
        new_user = auth_service.register_user(user_data.model_dump())
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    admin_user: dict = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get user by ID (Admin only)"""
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    admin_user: dict = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update user (Admin only)"""
    update_dict = {k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    updated_user = auth_service.update_user(user_id, update_dict)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user


@router.put("/admin/users/{user_id}/toggle-active", response_model=UserResponse)
async def toggle_user_active(
    user_id: str,
    admin_user: dict = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Toggle user active status (Admin only)"""
    if user_id == admin_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot toggle your own active status"
        )
    
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    new_status = not user.get("is_active", True)
    auth_service.toggle_user_status(user_id, new_status)
    updated_user = auth_service.get_user_by_id(user_id)
    
    return updated_user


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: dict = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Delete user (Admin only)"""
    if user_id == admin_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    if auth_service.delete_user(user_id):
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
