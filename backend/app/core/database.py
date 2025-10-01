"""
Database Configuration and Session Management

Async SQLAlchemy setup with connection pooling and session management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio

from app.core.config import settings

# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before use
    poolclass=NullPool if settings.TESTING else None,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()


async def create_db_and_tables():
    """Create database tables if they don't exist."""
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models import (
            tenant, user, project, asset, job, 
            scene, transcript, content_moderation, 
            usage_tracking, audit_log, user_session
        )
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with automatic cleanup."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to inject database session."""
    async with get_async_session() as session:
        yield session