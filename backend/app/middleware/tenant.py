"""
Tenant Middleware

Middleware for handling multi-tenant requests and ensuring tenant isolation.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.core.database import get_async_session
from app.models.tenant import Tenant
from app.core.exceptions import TenantNotFoundError, TenantNotActiveError

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and validate tenant information from requests.
    
    Supports multiple tenant identification methods:
    1. Subdomain (e.g., customer1.yourdomain.com)
    2. Header (X-Tenant-ID)
    3. Path prefix (e.g., /tenant/{tenant_id}/api/...)
    4. JWT token tenant claim
    """
    
    def __init__(self, app, default_tenant: str = "default"):
        super().__init__(app)
        self.default_tenant = default_tenant
        
    async def dispatch(self, request: Request, call_next):
        # Skip tenant middleware for health checks and public endpoints
        if self._should_skip_tenant_check(request.url.path):
            return await call_next(request)
            
        try:
            # Extract tenant identifier
            tenant_id = await self._extract_tenant_id(request)
            
            # Validate and set tenant context
            if tenant_id:
                tenant = await self._validate_tenant(tenant_id)
                request.state.tenant = tenant
                request.state.tenant_id = tenant.id
            else:
                # Use default tenant for requests without explicit tenant
                tenant = await self._get_default_tenant()
                request.state.tenant = tenant
                request.state.tenant_id = tenant.id if tenant else None
                
        except (TenantNotFoundError, TenantNotActiveError) as e:
            logger.warning(f"Tenant validation failed: {e}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Tenant not found or inactive"}
            )
        except Exception as e:
            logger.error(f"Tenant middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )
            
        response = await call_next(request)
        
        # Add tenant info to response headers (optional)
        if hasattr(request.state, 'tenant') and request.state.tenant:
            response.headers["X-Tenant-ID"] = str(request.state.tenant.id)
            response.headers["X-Tenant-Name"] = request.state.tenant.name
            
        return response
    
    def _should_skip_tenant_check(self, path: str) -> bool:
        """Check if tenant validation should be skipped for this path."""
        skip_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/auth/register",  # Allow tenant creation
            "/auth/login",     # Tenant is determined after login
            "/static",
            "/favicon.ico"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    async def _extract_tenant_id(self, request: Request) -> str | None:
        """Extract tenant ID from various sources."""
        
        # 1. Check subdomain (highest priority)
        host = request.headers.get("host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            if subdomain not in ["www", "api", "app"]:  # Reserved subdomains
                return subdomain
        
        # 2. Check X-Tenant-ID header
        tenant_header = request.headers.get("X-Tenant-ID")
        if tenant_header:
            return tenant_header
            
        # 3. Check path prefix (/tenant/{tenant_id}/...)
        path_parts = request.url.path.strip("/").split("/")
        if len(path_parts) >= 2 and path_parts[0] == "tenant":
            return path_parts[1]
            
        # 4. Check JWT token (if user is authenticated)
        if hasattr(request.state, 'user') and request.state.user:
            return getattr(request.state.user, 'tenant_id', None)
            
        # 5. Check query parameter (fallback)
        return request.query_params.get("tenant_id")
    
    async def _validate_tenant(self, tenant_identifier: str) -> Tenant:
        """Validate tenant exists and is active."""
        async for db in get_async_session():
            try:
                # Try to find by ID first, then by name
                query = select(Tenant).where(
                    (Tenant.id == tenant_identifier) | 
                    (Tenant.name == tenant_identifier)
                )
                result = await db.execute(query)
                tenant = result.scalar_one_or_none()
                
                if not tenant:
                    raise TenantNotFoundError(f"Tenant '{tenant_identifier}' not found")
                
                if not tenant.is_active:
                    raise TenantNotActiveError(f"Tenant '{tenant_identifier}' is not active")
                
                return tenant
                
            finally:
                await db.close()
    
    async def _get_default_tenant(self) -> Tenant | None:
        """Get the default tenant."""
        try:
            return await self._validate_tenant(self.default_tenant)
        except (TenantNotFoundError, TenantNotActiveError):
            logger.warning(f"Default tenant '{self.default_tenant}' not found or inactive")
            return None


def get_current_tenant(request: Request) -> Tenant:
    """Dependency to get current tenant from request state."""
    if not hasattr(request.state, 'tenant') or not request.state.tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context not found"
        )
    return request.state.tenant


def get_current_tenant_id(request: Request) -> str:
    """Dependency to get current tenant ID from request state."""
    tenant = get_current_tenant(request)
    return str(tenant.id)


# Tenant-aware database dependency
async def get_tenant_db(request: Request) -> AsyncSession:
    """Get database session with tenant context."""
    tenant = get_current_tenant(request)
    
    async for db in get_async_session():
        try:
            # Set tenant context for this session
            db.info["tenant_id"] = str(tenant.id)
            db.info["tenant"] = tenant
            yield db
        finally:
            await db.close()