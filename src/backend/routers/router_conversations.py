"""
Conversation History Router
Handles conversation storage and retrieval endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from ..utils.response_formatter import format_success, format_error
from ..services.conversation_service import conversation_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/conversations", tags=["Conversations"])


class SaveConversationRequest(BaseModel):
    """Request to save a conversation"""
    session_id: str = Field(..., description="Unique conversation ID")
    title: str = Field(..., description="Conversation title")
    messages: List[Dict[str, Any]] = Field(..., description="List of messages")
    user_id: str = Field(default="anonymous", description="User identifier")


class GetConversationsRequest(BaseModel):
    """Request to get conversation list"""
    user_id: str = Field(default="anonymous", description="User identifier")
    limit: int = Field(default=20, ge=1, le=100, description="Max conversations to return")


class GetConversationRequest(BaseModel):
    """Request to get a specific conversation"""
    session_id: str = Field(..., description="Conversation ID")
    user_id: str = Field(default="anonymous", description="User identifier")


class DeleteConversationRequest(BaseModel):
    """Request to delete a conversation"""
    session_id: str = Field(..., description="Conversation ID")
    user_id: str = Field(default="anonymous", description="User identifier")


@router.post("/save")
async def save_conversation(request: SaveConversationRequest):
    """
    Save or update a conversation
    """
    try:
        success = await conversation_service.save_conversation(
            session_id=request.session_id,
            title=request.title,
            messages=request.messages,
            user_id=request.user_id
        )
        
        if success:
            return format_success(
                data={"session_id": request.session_id},
                message="Conversation saved successfully"
            )
        else:
            return format_error(
                error="Failed to save conversation",
                status_code=500
            )
            
    except Exception as e:
        logger.error(f"Save conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/list")
async def get_conversations(request: GetConversationsRequest):
    """
    Get list of user's conversations
    """
    try:
        conversations = await conversation_service.get_conversations(
            user_id=request.user_id,
            limit=request.limit
        )
        
        return format_success(
            data={
                "conversations": conversations,
                "count": len(conversations)
            },
            message=f"Retrieved {len(conversations)} conversations"
        )
            
    except Exception as e:
        logger.error(f"Get conversations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get")
async def get_conversation(request: GetConversationRequest):
    """
    Get a specific conversation with all messages
    """
    try:
        conversation = await conversation_service.get_conversation(
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        if conversation:
            return format_success(
                data={"conversation": conversation},
                message="Conversation retrieved successfully"
            )
        else:
            return format_error(
                error="Conversation not found",
                status_code=404
            )
            
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete")
async def delete_conversation(request: DeleteConversationRequest):
    """
    Delete a conversation
    """
    try:
        success = await conversation_service.delete_conversation(
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        if success:
            return format_success(
                data={"session_id": request.session_id},
                message="Conversation deleted successfully"
            )
        else:
            return format_error(
                error="Conversation not found or already deleted",
                status_code=404
            )
            
    except Exception as e:
        logger.error(f"Delete conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
