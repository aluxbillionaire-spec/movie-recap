"""
Test the authentication system.
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.core.auth import AuthService, JWTService
from app.core.exceptions import AuthenticationError, AuthorizationError
from tests.conftest import TestDataFactory


class TestJWTService:
    """Test JWT service functionality."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        jwt_service = JWTService()
        user_data = {"user_id": "test-user", "tenant_id": "test-tenant"}
        
        token = jwt_service.create_access_token(user_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT format
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        jwt_service = JWTService()
        user_data = {"user_id": "test-user", "tenant_id": "test-tenant"}
        
        token = jwt_service.create_refresh_token(user_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        jwt_service = JWTService()
        user_data = {"user_id": "test-user", "tenant_id": "test-tenant"}
        
        token = jwt_service.create_access_token(user_data)
        decoded_data = jwt_service.verify_token(token)
        
        assert decoded_data["user_id"] == "test-user"
        assert decoded_data["tenant_id"] == "test-tenant"
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        jwt_service = JWTService()
        
        with pytest.raises(AuthenticationError):
            jwt_service.verify_token("invalid-token")
    
    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        jwt_service = JWTService()
        
        # Create token with very short expiry
        with patch('app.core.auth.datetime') as mock_datetime:
            # Mock current time
            mock_datetime.utcnow.return_value.timestamp.return_value = 1000000000
            token = jwt_service.create_access_token({"user_id": "test"}, expires_delta=-1)
            
            # Advance time
            mock_datetime.utcnow.return_value.timestamp.return_value = 1000000060
            
            with pytest.raises(AuthenticationError):
                jwt_service.verify_token(token)


class TestAuthService:
    """Test authentication service functionality."""
    
    @pytest.fixture
    def auth_service(self, mock_redis):
        """Create auth service with mocked dependencies."""
        return AuthService(redis_client=mock_redis)
    
    @pytest.fixture
    def user_data(self):
        """Sample user data."""
        return TestDataFactory.create_user()
    
    async def test_create_user_success(self, auth_service, user_data):
        """Test successful user creation."""
        with patch('app.core.auth.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            result = await auth_service.create_user(
                email=user_data["email"],
                password=user_data["password"],
                full_name=user_data["full_name"],
                tenant_id="test-tenant"
            )
            
            assert result["email"] == user_data["email"]
            assert result["full_name"] == user_data["full_name"]
            assert "id" in result
    
    async def test_create_user_duplicate_email(self, auth_service, user_data):
        """Test user creation with duplicate email."""
        with patch('app.core.auth.get_user_by_email') as mock_get_user:
            mock_get_user.return_value = {"id": "existing-user"}
            
            with pytest.raises(AuthenticationError):
                await auth_service.create_user(
                    email=user_data["email"],
                    password=user_data["password"],
                    full_name=user_data["full_name"],
                    tenant_id="test-tenant"
                )
    
    async def test_authenticate_user_success(self, auth_service, user_data):
        """Test successful user authentication."""
        with patch('app.core.auth.get_user_by_email') as mock_get_user, \
             patch('app.core.auth.verify_password') as mock_verify:
            
            mock_get_user.return_value = {
                "id": "test-user",
                "email": user_data["email"],
                "password_hash": "hashed_password",
                "is_active": True,
                "tenant_id": "test-tenant"
            }
            mock_verify.return_value = True
            
            result = await auth_service.authenticate_user(
                email=user_data["email"],
                password=user_data["password"]
            )
            
            assert result["id"] == "test-user"
            assert result["email"] == user_data["email"]
    
    async def test_authenticate_user_invalid_credentials(self, auth_service, user_data):
        """Test authentication with invalid credentials."""
        with patch('app.core.auth.get_user_by_email') as mock_get_user:
            mock_get_user.return_value = None
            
            with pytest.raises(AuthenticationError):
                await auth_service.authenticate_user(
                    email=user_data["email"],
                    password="wrong_password"
                )
    
    async def test_authenticate_user_inactive(self, auth_service, user_data):
        """Test authentication with inactive user."""
        with patch('app.core.auth.get_user_by_email') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user",
                "email": user_data["email"],
                "is_active": False
            }
            
            with pytest.raises(AuthenticationError):
                await auth_service.authenticate_user(
                    email=user_data["email"],
                    password=user_data["password"]
                )
    
    async def test_refresh_token_success(self, auth_service):
        """Test successful token refresh."""
        with patch('app.core.auth.JWTService.verify_token') as mock_verify, \
             patch('app.core.auth.get_user_by_id') as mock_get_user:
            
            mock_verify.return_value = {"user_id": "test-user", "tenant_id": "test-tenant"}
            mock_get_user.return_value = {
                "id": "test-user",
                "email": "test@example.com",
                "is_active": True,
                "tenant_id": "test-tenant"
            }
            
            result = await auth_service.refresh_token("valid-refresh-token")
            
            assert "access_token" in result
            assert "refresh_token" in result
            assert "token_type" in result
    
    async def test_refresh_token_invalid(self, auth_service):
        """Test token refresh with invalid token."""
        with patch('app.core.auth.JWTService.verify_token') as mock_verify:
            mock_verify.side_effect = AuthenticationError("Invalid token")
            
            with pytest.raises(AuthenticationError):
                await auth_service.refresh_token("invalid-token")
    
    async def test_logout_user(self, auth_service):
        """Test user logout."""
        token = "test-token"
        
        await auth_service.logout_user(token)
        
        # Verify token was blacklisted
        auth_service.redis_client.set.assert_called_once()
    
    async def test_change_password_success(self, auth_service):
        """Test successful password change."""
        with patch('app.core.auth.get_user_by_id') as mock_get_user, \
             patch('app.core.auth.verify_password') as mock_verify, \
             patch('app.core.auth.hash_password') as mock_hash, \
             patch('app.core.auth.update_user_password') as mock_update:
            
            mock_get_user.return_value = {
                "id": "test-user",
                "password_hash": "old_hash"
            }
            mock_verify.return_value = True
            mock_hash.return_value = "new_hash"
            
            await auth_service.change_password(
                user_id="test-user",
                current_password="old_password",
                new_password="new_password"
            )
            
            mock_update.assert_called_once_with("test-user", "new_hash")
    
    async def test_change_password_wrong_current(self, auth_service):
        """Test password change with wrong current password."""
        with patch('app.core.auth.get_user_by_id') as mock_get_user, \
             patch('app.core.auth.verify_password') as mock_verify:
            
            mock_get_user.return_value = {
                "id": "test-user",
                "password_hash": "old_hash"
            }
            mock_verify.return_value = False
            
            with pytest.raises(AuthenticationError):
                await auth_service.change_password(
                    user_id="test-user",
                    current_password="wrong_password",
                    new_password="new_password"
                )


@pytest.mark.integration
class TestAuthIntegration:
    """Integration tests for authentication system."""
    
    async def test_login_flow(self, async_client, db_session):
        """Test complete login flow."""
        # Create a test user first
        user_data = TestDataFactory.create_user()
        
        # Register user
        response = await async_client.post(
            "/api/v1/auth/register",
            json=user_data,
            headers={"X-Tenant-ID": "test-tenant"}
        )
        assert response.status_code == 201
        
        # Login
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "email": user_data["email"],
                "password": user_data["password"]
            },
            headers={"X-Tenant-ID": "test-tenant"}
        )
        assert login_response.status_code == 200
        
        login_data = login_response.json()
        assert "access_token" in login_data
        assert "refresh_token" in login_data
        assert login_data["token_type"] == "bearer"
    
    async def test_protected_endpoint_access(self, async_client, auth_headers):
        """Test accessing protected endpoints."""
        # Try without token
        response = await async_client.get("/api/v1/user/profile")
        assert response.status_code == 401
        
        # Try with invalid token
        response = await async_client.get(
            "/api/v1/user/profile",
            headers=auth_headers("invalid-token")
        )
        assert response.status_code == 401
        
        # Try with valid token (mocked)
        with patch('app.core.auth.JWTService.verify_token') as mock_verify:
            mock_verify.return_value = {"user_id": "test-user", "tenant_id": "test-tenant"}
            
            response = await async_client.get(
                "/api/v1/user/profile",
                headers=auth_headers("valid-token")
            )
            # This might be 404 if user doesn't exist, but not 401
            assert response.status_code != 401
    
    async def test_token_refresh_flow(self, async_client):
        """Test token refresh flow."""
        with patch('app.core.auth.AuthService.refresh_token') as mock_refresh:
            mock_refresh.return_value = {
                "access_token": "new-access-token",
                "refresh_token": "new-refresh-token",
                "token_type": "bearer"
            }
            
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "old-refresh-token"}
            )
            assert response.status_code == 200
            
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data