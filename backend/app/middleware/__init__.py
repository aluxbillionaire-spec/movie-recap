"""
Rate Limiting Middleware

Implement rate limiting per user and tenant with Redis backend.
"""

import time
import json
from typing import Optional, Dict, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.security import verify_token


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with Redis backend."""
    
    def __init__(self, app, redis_url: str = None):
        super().__init__(app)
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis_client = None
        
        # Rate limit configurations
        self.rate_limits = {
            "per_minute": settings.RATE_LIMIT_PER_MINUTE,
            "per_hour": settings.RATE_LIMIT_PER_HOUR, 
            "per_day": settings.RATE_LIMIT_PER_DAY
        }
        
        # Exempt paths from rate limiting
        self.exempt_paths = ["/health", "/docs", "/openapi.json"]
        
    async def get_redis_client(self):
        """Get Redis client with connection pooling."""
        if self.redis_client is None:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
        return self.redis_client
        
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        
        # Skip rate limiting for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        try:
            # Get user identifier
            user_id, tenant_id = await self.get_user_identifier(request)
            
            # Check rate limits
            await self.check_rate_limits(user_id, tenant_id, request)
            
            # Process request
            response = await call_next(request)
            
            # Update rate limit counters
            await self.update_rate_limits(user_id, tenant_id, request)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            # Log error and allow request to proceed
            print(f"Rate limiting error: {e}")
            return await call_next(request)
    
    async def get_user_identifier(self, request: Request) -> tuple[Optional[str], Optional[str]]:
        """Extract user and tenant ID from request."""
        
        # Try to get from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                payload = verify_token(token, "access")
                return payload.get("sub"), payload.get("tenant_id")
            except:
                pass
        
        # Fallback to IP address for anonymous users
        client_ip = request.client.host
        return f"anonymous:{client_ip}", "anonymous"
    
    async def check_rate_limits(self, user_id: str, tenant_id: str, request: Request):
        """Check if request exceeds rate limits."""
        
        redis_client = await self.get_redis_client()
        current_time = int(time.time())
        
        # Check different time windows
        for window, limit in self.rate_limits.items():
            key = f"rate_limit:{user_id}:{window}"
            
            # Get window duration
            if window == "per_minute":
                window_duration = 60
            elif window == "per_hour":
                window_duration = 3600
            else:  # per_day
                window_duration = 86400
            
            # Get current count
            current_count = await redis_client.get(key)
            current_count = int(current_count) if current_count else 0
            
            if current_count >= limit:
                # Rate limit exceeded
                remaining_time = await redis_client.ttl(key)
                
                response_data = {
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded for {window}",
                    "limit": limit,
                    "window": window,
                    "retry_after": remaining_time
                }
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=response_data
                )
    
    async def update_rate_limits(self, user_id: str, tenant_id: str, request: Request):
        """Update rate limit counters."""
        
        redis_client = await self.get_redis_client()
        current_time = int(time.time())
        
        # Update counters for each window
        for window, limit in self.rate_limits.items():
            key = f"rate_limit:{user_id}:{window}"
            
            # Get window duration
            if window == "per_minute":
                window_duration = 60
            elif window == "per_hour":
                window_duration = 3600
            else:  # per_day
                window_duration = 86400
            
            # Increment counter
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_duration)
            await pipe.execute()


"""
Logging Middleware

Structured logging for requests and responses.
"""

import logging
import time
import json
import uuid
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("movie_recap_api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Structured logging middleware."""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Sensitive headers to exclude from logs
        self.sensitive_headers = {
            "authorization", "cookie", "x-api-key", "x-auth-token"
        }
        
        # Paths to exclude from detailed logging
        self.exclude_paths = ["/health", "/metrics"]
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response details."""
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Log request
        if request.url.path not in self.exclude_paths:
            await self.log_request(request, request_id)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            if request.url.path not in self.exclude_paths:
                await self.log_response(request, response, request_id, process_time)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            await self.log_error(request, e, request_id, process_time)
            raise
    
    async def log_request(self, request: Request, request_id: str):
        """Log incoming request details."""
        
        # Get user info if available
        user_info = await self.get_user_info(request)
        
        # Filter headers
        headers = self.filter_sensitive_headers(dict(request.headers))
        
        log_data = {
            "event": "request_started",
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": headers,
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "user_info": user_info
        }
        
        logger.info(json.dumps(log_data))
    
    async def log_response(self, request: Request, response: Response, request_id: str, process_time: float):
        """Log response details."""
        
        log_data = {
            "event": "request_completed",
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "response_size": response.headers.get("content-length")
        }
        
        # Log level based on status code
        if response.status_code >= 500:
            logger.error(json.dumps(log_data))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))
    
    async def log_error(self, request: Request, error: Exception, request_id: str, process_time: float):
        """Log error details."""
        
        log_data = {
            "event": "request_error",
            "request_id": request_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "process_time": round(process_time, 4),
            "path": request.url.path,
            "method": request.method
        }
        
        logger.error(json.dumps(log_data))
    
    def filter_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive headers from logs."""
        
        filtered = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                filtered[key] = "[REDACTED]"
            else:
                filtered[key] = value
        
        return filtered
    
    async def get_user_info(self, request: Request) -> Dict[str, Any]:
        """Extract user information from request."""
        
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = verify_token(token, "access")
                
                return {
                    "user_id": payload.get("sub"),
                    "tenant_id": payload.get("tenant_id"),
                    "roles": payload.get("roles", [])
                }
        except:
            pass
        
        return {"authenticated": False}


"""
Tenant Middleware

Multi-tenant context and isolation.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    """Multi-tenant context middleware."""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Public paths that don't require tenant context
        self.public_paths = [
            "/health", "/docs", "/openapi.json", "/auth/register", "/auth/login"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Add tenant context to request."""
        
        # Skip tenant validation for public paths
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)
        
        try:
            # Extract tenant information
            tenant_info = await self.get_tenant_info(request)
            
            # Add tenant context to request state
            request.state.tenant_id = tenant_info.get("tenant_id")
            request.state.user_id = tenant_info.get("user_id")
            request.state.user_roles = tenant_info.get("roles", [])
            
            # Validate tenant is active
            if not tenant_info.get("tenant_active", True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tenant account is suspended"
                )
            
            response = await call_next(request)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication"
            )
    
    async def get_tenant_info(self, request: Request) -> Dict[str, Any]:
        """Extract tenant information from request."""
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        try:
            token = auth_header.split(" ")[1]
            payload = verify_token(token, "access")
            
            return {
                "user_id": payload.get("sub"),
                "tenant_id": payload.get("tenant_id"),
                "roles": payload.get("roles", []),
                "tenant_active": True  # In production, validate from database
            }
            
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )