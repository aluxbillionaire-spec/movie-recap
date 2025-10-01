"""
Movie Recap Pipeline - Main FastAPI Application

A multi-tenant backend for automated long-form video recap generation.
Handles authentication, uploads, job management, and content moderation.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, create_db_and_tables
from app.core.security import init_security
from app.api.v1.router import api_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.tenant import TenantMiddleware
from app.core.exceptions import (
    ValidationException,
    QuotaExceededException,
    AuthenticationException,
    PermissionException
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await create_db_and_tables()
    init_security()
    
    yield
    
    # Shutdown
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title="Movie Recap Pipeline API",
    description="Multi-tenant backend for automated long-form video recap generation",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(TenantMiddleware)


# Exception handlers
@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(QuotaExceededException)
async def quota_exceeded_handler(request: Request, exc: QuotaExceededException):
    return JSONResponse(
        status_code=429,
        content={
            "error": "quota_exceeded",
            "message": exc.message,
            "quota_type": exc.quota_type,
            "current_usage": exc.current_usage,
            "limit": exc.limit
        }
    )


@app.exception_handler(AuthenticationException)
async def auth_exception_handler(request: Request, exc: AuthenticationException):
    return JSONResponse(
        status_code=401,
        content={
            "error": "authentication_error",
            "message": exc.message
        }
    )


@app.exception_handler(PermissionException)
async def permission_exception_handler(request: Request, exc: PermissionException):
    return JSONResponse(
        status_code=403,
        content={
            "error": "permission_denied",
            "message": exc.message,
            "required_permission": exc.required_permission
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred"
        }
    )


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/health/ready")
async def readiness_check():
    """Readiness check with database connectivity."""
    try:
        # Test database connection
        from app.core.database import get_async_session
        async with get_async_session() as session:
            await session.execute("SELECT 1")
        
        return {"status": "ready", "timestamp": time.time()}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service not ready")


# Include API routes
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )