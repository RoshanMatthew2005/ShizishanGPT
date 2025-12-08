"""
FastAPI Dependencies
Shared dependencies for routes and services
"""

from typing import Optional
from fastapi import Header, HTTPException, status
from .config import settings
import logging

logger = logging.getLogger(__name__)


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Verify API key (optional - can be enabled for production)
    Currently disabled for development
    """
    # For production, uncomment and set API_KEY in settings
    # if settings.API_KEY and x_api_key != settings.API_KEY:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid API key"
    #     )
    return x_api_key or "no-key"


async def get_request_id(x_request_id: Optional[str] = Header(None)) -> str:
    """
    Get or generate request ID for tracking
    """
    import uuid
    return x_request_id or str(uuid.uuid4())


class ModelRegistry:
    """
    Global registry for loaded models
    Stores models loaded at startup for reuse
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance.models = {}
            cls._instance.initialized = False
        return cls._instance
    
    def register(self, name: str, model):
        """Register a model"""
        self.models[name] = model
        logger.info(f"Registered model: {name}")
    
    def get(self, name: str):
        """Get a registered model"""
        if name not in self.models:
            raise ValueError(f"Model '{name}' not found in registry")
        return self.models[name]
    
    def has(self, name: str) -> bool:
        """Check if model exists"""
        return name in self.models
    
    def set_initialized(self):
        """Mark registry as initialized"""
        self.initialized = True
    
    def is_initialized(self) -> bool:
        """Check if registry is initialized"""
        return self.initialized


# Global model registry instance
model_registry = ModelRegistry()


def get_model(name: str):
    """
    Dependency to get a model from registry
    """
    try:
        return model_registry.get(name)
    except ValueError as e:
        logger.error(f"Model not found: {name}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model '{name}' not available"
        )
