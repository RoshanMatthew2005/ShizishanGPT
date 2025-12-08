"""
Error Handler
Global exception handling for FastAPI
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
import traceback
from .response_formatter import format_error

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors
    """
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        field = " -> ".join(str(x) for x in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    logger.warning(f"Validation error on {request.url.path}: {error_messages}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=format_error(
            error="Validation failed",
            status_code=422,
            details={
                "errors": error_messages,
                "path": str(request.url.path)
            }
        )
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all other exceptions
    """
    # Log the full traceback
    logger.error(f"Unhandled exception on {request.url.path}:")
    logger.error(traceback.format_exc())
    
    # Determine status code
    status_code = getattr(exc, "status_code", 500)
    
    # Get error message
    error_message = str(exc) or "Internal server error"
    
    return JSONResponse(
        status_code=status_code,
        content=format_error(
            error=error_message,
            status_code=status_code,
            details={
                "type": exc.__class__.__name__,
                "path": str(request.url.path)
            }
        )
    )


async def http_exception_handler(request: Request, exc):
    """
    Handle HTTP exceptions from FastAPI
    """
    logger.warning(f"HTTP exception on {request.url.path}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error(
            error=exc.detail,
            status_code=exc.status_code,
            details={"path": str(request.url.path)}
        )
    )


class ModelLoadError(Exception):
    """Exception raised when model loading fails"""
    pass


class ServiceError(Exception):
    """Exception raised by services"""
    pass


class DatabaseError(Exception):
    """Exception raised by database operations"""
    pass
