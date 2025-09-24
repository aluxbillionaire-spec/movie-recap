"""
Test configuration and utilities.
"""
import pytest
import asyncio
from typing import Dict, Any, AsyncGenerator
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.database import get_db
from app.core.config import get_settings
from app.models.base import Base


# Test database configuration
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_movie_recap"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def test_db_setup(test_engine):
    """Set up test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_engine, test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session):
    """Override database dependency for testing."""
    async def _override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def test_client(override_get_db):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = Mock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.incr = AsyncMock(return_value=1)
    redis_mock.expire = AsyncMock(return_value=True)
    redis_mock.pipeline = Mock()
    redis_mock.pipeline.return_value.__enter__ = Mock(return_value=redis_mock)
    redis_mock.pipeline.return_value.__exit__ = Mock(return_value=None)
    return redis_mock


@pytest.fixture
def mock_celery():
    """Mock Celery client."""
    celery_mock = Mock()
    celery_mock.send_task = Mock(return_value=Mock(id="test-task-id"))
    return celery_mock


@pytest.fixture
def mock_storage():
    """Mock storage service."""
    storage_mock = Mock()
    storage_mock.upload_file = AsyncMock(return_value="test-file-id")
    storage_mock.download_file = AsyncMock(return_value=b"test-file-content")
    storage_mock.delete_file = AsyncMock(return_value=True)
    storage_mock.get_file_info = AsyncMock(return_value={
        "size": 1024,
        "mime_type": "video/mp4",
        "created_at": "2023-01-01T00:00:00Z"
    })
    return storage_mock


@pytest.fixture
def sample_tenant_data():
    """Sample tenant data for testing."""
    return {
        "id": "test-tenant",
        "name": "Test Tenant",
        "email": "admin@testtenant.com",
        "plan": "professional",
        "settings": {
            "max_concurrent_jobs": 5,
            "storage_limit_gb": 100,
            "api_rate_limit": 1000
        }
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "is_active": True
    }


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Movie Recap",
        "description": "Test project for movie recap generation",
        "settings": {
            "target_resolution": "4K",
            "quality": "high",
            "enable_watermark": True
        }
    }


@pytest.fixture
def sample_video_file():
    """Sample video file data for testing."""
    return {
        "filename": "test_movie.mp4",
        "content_type": "video/mp4",
        "size": 1024 * 1024 * 100,  # 100MB
        "content": b"fake-video-content"
    }


@pytest.fixture
def sample_script_file():
    """Sample script file data for testing."""
    return {
        "filename": "test_script.txt",
        "content_type": "text/plain",
        "size": 1024 * 10,  # 10KB
        "content": b"This is a test movie script content."
    }


@pytest.fixture
def auth_headers():
    """Generate authentication headers for testing."""
    def _auth_headers(token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    return _auth_headers


@pytest.fixture
def tenant_headers():
    """Generate tenant headers for testing."""
    def _tenant_headers(tenant_id: str) -> Dict[str, str]:
        return {
            "X-Tenant-ID": tenant_id,
            "Content-Type": "application/json"
        }
    return _tenant_headers


class TestHelpers:
    """Test helper utilities."""
    
    @staticmethod
    def create_jwt_token(user_id: str, tenant_id: str) -> str:
        """Create a JWT token for testing."""
        # In a real implementation, use your JWT library
        return f"test-token-{user_id}-{tenant_id}"
    
    @staticmethod
    def assert_response_structure(response_data: Dict[str, Any], expected_keys: list):
        """Assert that response has expected structure."""
        for key in expected_keys:
            assert key in response_data, f"Missing key: {key}"
    
    @staticmethod
    def assert_error_response(response_data: Dict[str, Any], error_code: str):
        """Assert that response is a proper error response."""
        assert "error" in response_data
        assert "code" in response_data["error"]
        assert response_data["error"]["code"] == error_code
    
    @staticmethod
    async def wait_for_job_completion(client: AsyncClient, job_id: str, timeout: int = 30):
        """Wait for a job to complete during testing."""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = await client.get(f"/api/v1/jobs/{job_id}")
            if response.status_code == 200:
                job_data = response.json()
                if job_data["status"] in ["completed", "failed", "cancelled"]:
                    return job_data
            
            await asyncio.sleep(1)
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")


# Test data factories
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_tenant(**kwargs) -> Dict[str, Any]:
        """Create tenant test data."""
        default_data = {
            "id": "test-tenant",
            "name": "Test Tenant",
            "email": "admin@testtenant.com",
            "plan": "professional",
            "is_active": True,
            "settings": {
                "max_concurrent_jobs": 5,
                "storage_limit_gb": 100,
                "api_rate_limit": 1000
            }
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_user(**kwargs) -> Dict[str, Any]:
        """Create user test data."""
        default_data = {
            "email": "testuser@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User",
            "is_active": True,
            "role": "user"
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_project(**kwargs) -> Dict[str, Any]:
        """Create project test data."""
        default_data = {
            "name": "Test Movie Recap",
            "description": "Test project for movie recap generation",
            "status": "active",
            "settings": {
                "target_resolution": "4K",
                "quality": "high",
                "enable_watermark": True
            }
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_job(**kwargs) -> Dict[str, Any]:
        """Create job test data."""
        default_data = {
            "type": "video_processing",
            "status": "pending",
            "priority": "normal",
            "settings": {
                "target_resolution": "4K",
                "quality": "high"
            },
            "metadata": {}
        }
        default_data.update(kwargs)
        return default_data


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "external: mark test as requiring external services"
    )