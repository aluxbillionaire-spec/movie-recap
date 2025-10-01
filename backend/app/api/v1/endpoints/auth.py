"""
Authentication Endpoints

User registration, login, token refresh, and logout functionality.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, validator

from app.core.database import get_db_session
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    blacklist_token,
    generate_secure_token,
    hash_refresh_token,
    security
)
from app.models.user import User
from app.models.tenant import Tenant
from app.models.user_session import UserSession
from app.core.exceptions import AuthenticationException, ValidationException

router = APIRouter()


# Pydantic models for request/response
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    tenant_name: str
    first_name: str = None
    last_name: str = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('tenant_name')
    def validate_tenant_name(cls, v):
        if len(v) < 3:
            raise ValueError('Tenant name must be at least 3 characters long')
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    tenant_id: str
    first_name: str = None
    last_name: str = None
    roles: list[str]
    is_active: bool
    email_verified: bool
    created_at: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistration,
    db: AsyncSession = Depends(get_db_session)
):
    """Register a new user and tenant."""
    
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Check if tenant name already exists
    result = await db.execute(
        select(Tenant).where(Tenant.name == user_data.tenant_name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tenant name already exists"
        )
    
    # Create tenant
    tenant = Tenant(
        name=user_data.tenant_name,
        display_name=user_data.tenant_name.title()
    )
    db.add(tenant)
    await db.flush()  # Get tenant ID
    
    # Create user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        tenant_id=tenant.id,
        roles=["admin"]  # First user in tenant is admin
    )
    db.add(user)
    await db.commit()
    
    return UserResponse(**user.to_dict())


@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Authenticate user and return tokens."""
    
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    # Create tokens
    token_data = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "roles": user.roles,
        "email": user.email
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Store refresh token session
    session = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        device_info={},
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(session)
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60  # 15 minutes
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Refresh access token using refresh token."""
    
    # Verify refresh token
    payload = verify_token(refresh_data.refresh_token, "refresh")
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if refresh token session exists and is valid
    token_hash = hash_refresh_token(refresh_data.refresh_token)
    result = await db.execute(
        select(UserSession).where(
            UserSession.refresh_token_hash == token_hash,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user data
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    token_data = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "roles": user.roles,
        "email": user.email
    }
    
    access_token = create_access_token(token_data)
    
    # Update session last used
    session.last_used_at = datetime.utcnow()
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_data.refresh_token,  # Return same refresh token
        expires_in=15 * 60
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Logout user and blacklist token."""
    
    # Blacklist the access token
    blacklist_token(credentials.credentials)
    
    # Get user from token
    payload = verify_token(credentials.credentials, "access")
    user_id = payload.get("sub")
    
    if user_id:
        # Invalidate all refresh token sessions for this user
        result = await db.execute(
            select(UserSession).where(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        )
        sessions = result.scalars().all()
        
        for session in sessions:
            session.is_active = False
        
        await db.commit()


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user information."""
    
    payload = verify_token(credentials.credentials, "access")
    user_id = payload.get("sub")
    
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user.to_dict())