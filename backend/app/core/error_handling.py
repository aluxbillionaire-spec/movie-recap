"""
Error handling middleware and utilities.
"""
import json
import logging
import traceback
from typing import Any, Dict, Optional
from datetime import datetime

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.exceptions import BaseAPIException

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle errors and format responses consistently."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except BaseAPIException as exc:
            return await self.handle_api_exception(request, exc)
        except Exception as exc:
            return await self.handle_unexpected_exception(request, exc)
    
    async def handle_api_exception(self, request: Request, exc: BaseAPIException) -> JSONResponse:
        """Handle known API exceptions."""
        logger.warning(
            f"API Exception: {exc.error_code} - {exc.detail}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
                "error_code": exc.error_code,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "tenant_id": request.headers.get("x-tenant-id")
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.detail,
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": request.url.path
                }
            },
            headers=exc.headers
        )
    
    async def handle_unexpected_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error(
            f"Unexpected exception: {type(exc).__name__}: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "tenant_id": request.headers.get("x-tenant-id"),
                "traceback": traceback.format_exc()
            }
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": request.url.path
                }
            }
        )


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized error response."""
    content: Dict[str, Any] = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if details:
        content["error"]["details"] = details
    
    return JSONResponse(status_code=status_code, content=content)


class ValidationErrorHandler:
    """Utility class for handling validation errors."""
    
    @staticmethod
    def format_pydantic_errors(errors: list) -> Dict[str, Any]:
        """Format Pydantic validation errors."""
        formatted_errors = {}
        
        for error in errors:
            field_path = ".".join(str(loc) for loc in error["loc"])
            formatted_errors[field_path] = {
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            }
        
        return formatted_errors
    
    @staticmethod
    def create_validation_error_response(errors: list) -> JSONResponse:
        """Create a validation error response."""
        formatted_errors = ValidationErrorHandler.format_pydantic_errors(errors)
        
        return create_error_response(
            status_code=422,
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"field_errors": formatted_errors}
        )


class RetryHandler:
    """Utility for handling retries with exponential backoff."""
    
    @staticmethod
    def should_retry(exception: Exception, attempt: int, max_attempts: int) -> bool:
        """Determine if an operation should be retried."""
        if attempt >= max_attempts:
            return False
        
        # Retry on temporary failures
        retry_exceptions = (
            ConnectionError,
            TimeoutError,
        )
        
        return isinstance(exception, retry_exceptions)
    
    @staticmethod
    def calculate_backoff_delay(attempt: int, base_delay: float = 1.0) -> float:
        """Calculate exponential backoff delay."""
        return base_delay * (2 ** attempt)


class CircuitBreaker:
    """Simple circuit breaker implementation."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        return (datetime.utcnow() - self.last_failure_time).seconds >= self.timeout
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class HealthChecker:
    """Health check utilities."""
    
    @staticmethod
    async def check_database_health(db) -> Dict[str, Any]:
        """Check database health."""
        try:
            # Simple query to check database connectivity
            result = await db.execute("SELECT 1")
            return {"status": "healthy", "response_time_ms": 0}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def check_redis_health(redis) -> Dict[str, Any]:
        """Check Redis health."""
        try:
            await redis.ping()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def check_storage_health() -> Dict[str, Any]:
        """Check storage health."""
        try:
            # Implement storage-specific health check
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}