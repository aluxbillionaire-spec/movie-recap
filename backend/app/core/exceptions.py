"""
Custom exceptions for the movie recap service.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for all API errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class ValidationError(BaseAPIException):
    """Validation error."""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        error_code = f"VALIDATION_ERROR_{field.upper()}" if field else "VALIDATION_ERROR"
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code
        )


class AuthenticationError(BaseAPIException):
    """Authentication error."""
    
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_ERROR",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(BaseAPIException):
    """Authorization error."""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR"
        )


class ResourceNotFoundError(BaseAPIException):
    """Resource not found error."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id '{identifier}' not found",
            error_code="RESOURCE_NOT_FOUND"
        )


class TenantNotFoundError(BaseAPIException):
    """Tenant not found error."""
    
    def __init__(self, tenant_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_id}' not found",
            error_code="TENANT_NOT_FOUND"
        )


class RateLimitExceededError(BaseAPIException):
    """Rate limit exceeded error."""
    
    def __init__(self, limit: int, window: str):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {limit} requests per {window}",
            error_code="RATE_LIMIT_EXCEEDED"
        )


class FileUploadError(BaseAPIException):
    """File upload error."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="FILE_UPLOAD_ERROR"
        )


class ProcessingError(BaseAPIException):
    """Processing error."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="PROCESSING_ERROR"
        )


class StorageError(BaseAPIException):
    """Storage error."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="STORAGE_ERROR"
        )


class ExternalServiceError(BaseAPIException):
    """External service error."""
    
    def __init__(self, service: str, detail: str):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{service} service error: {detail}",
            error_code="EXTERNAL_SERVICE_ERROR"
        )


class DatabaseError(BaseAPIException):
    """Database error."""
    
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR"
        )


class ContentModerationError(BaseAPIException):
    """Content moderation error."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="CONTENT_MODERATION_ERROR"
        )


class QuotaExceededError(BaseAPIException):
    """Quota exceeded error."""
    
    def __init__(self, quota_type: str, limit: int):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"{quota_type} quota exceeded. Limit: {limit}",
            error_code="QUOTA_EXCEEDED"
        )


class MaintenanceError(BaseAPIException):
    """Service maintenance error."""
    
    def __init__(self, detail: str = "Service temporarily unavailable for maintenance"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="MAINTENANCE_ERROR"
        )