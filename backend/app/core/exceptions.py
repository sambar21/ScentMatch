# backend/app/core/exceptions.py
from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for all API errors"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        correlation_id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.correlation_id = correlation_id
        self.extra_data = kwargs


class ValidationError(BaseAPIException):
    """400 - Bad Request"""

    def __init__(self, detail: str, field: str = None, correlation_id: str = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="VALIDATION_ERROR",
            correlation_id=correlation_id,
            field=field,
        )


class NotFoundError(BaseAPIException):
    """404 - Resource Not Found"""

    def __init__(
        self, resource: str, resource_id: str = None, correlation_id: str = None
    ):
        detail = f"{resource} not found"
        if resource_id:
            detail += f" (ID: {resource_id})"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="RESOURCE_NOT_FOUND",
            correlation_id=correlation_id,
            resource=resource,
            resource_id=resource_id,
        )


class DatabaseError(BaseAPIException):
    """503 - Service Unavailable"""

    def __init__(self, operation: str, correlation_id: str = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database temporarily unavailable",
            error_code="DATABASE_ERROR",
            correlation_id=correlation_id,
            operation=operation,
        )


class AuthenticationError(BaseAPIException):
    """401 - Unauthorized"""

    def __init__(
        self, detail: str = "Authentication required", correlation_id: str = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_ERROR",
            correlation_id=correlation_id,
        )
