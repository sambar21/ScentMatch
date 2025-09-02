# backend/app/core/error_handlers.py
import logging
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import BaseAPIException
from app.core.structured_logger import get_logger
from app.middleware.simple_logging import get_correlation_id

logger = get_logger("error_handler")

async def api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handle custom API exceptions"""
    
    correlation_id = exc.correlation_id or get_correlation_id()
    
    # Log the error with context
    logger.error(
        f"API Error: {exc.error_code}",
        extra={
            "correlation_id": correlation_id,
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url.path),
            "method": request.method,
            "event_type": "api_error",
            **exc.extra_data
        }
    )
    
    # Return consistent error response
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "correlation_id": correlation_id,
                "status_code": exc.status_code
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI validation errors (422)"""
    
    correlation_id = get_correlation_id()
    
    # Extract field errors
    field_errors = []
    for error in exc.errors():
        field_errors.append({
            "field": ".".join(str(x) for x in error["loc"][1:]),  # Skip 'body'
            "message": error["msg"],
            "type": error["type"]
        })
    
    # Log validation error
    logger.warning(
        "Validation Error",
        extra={
            "correlation_id": correlation_id,
            "error_code": "VALIDATION_ERROR", 
            "path": str(request.url.path),
            "method": request.method,
            "field_errors": field_errors,
            "event_type": "validation_error"
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "correlation_id": correlation_id,
                "status_code": 422,
                "details": field_errors
            }
        }
    )

async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors"""
    
    correlation_id = get_correlation_id()
    
    # Log the database error (with full details for debugging)
    logger.error(
        "Database Error",
        extra={
            "correlation_id": correlation_id,
            "error_code": "DATABASE_ERROR",
            "path": str(request.url.path),
            "method": request.method,
            "exception_type": type(exc).__name__,
            "event_type": "database_error"
        },
        exc_info=True  # Include stack trace in logs
    )
    
    # Return generic error to user (don't expose DB details)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Database temporarily unavailable",
                "correlation_id": correlation_id,
                "status_code": 503
            }
        }
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors"""
    
    correlation_id = get_correlation_id()
    
    # Log the unexpected error
    logger.critical(
        "Unexpected Error",
        extra={
            "correlation_id": correlation_id,
            "error_code": "INTERNAL_ERROR",
            "path": str(request.url.path),
            "method": request.method,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "event_type": "internal_error"
        },
        exc_info=True
    )
    
    # Return generic 500 error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "correlation_id": correlation_id,
                "status_code": 500
            }
        }
    )