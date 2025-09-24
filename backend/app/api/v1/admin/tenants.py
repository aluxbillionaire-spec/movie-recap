"""
Tenant Management API

Administrative endpoints for managing tenants in multi-tenant deployment.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.core.database import get_async_session
from app.models.tenant import Tenant
from app.models.user import User
from app.models.usage_tracking import UsageTracking
from app.core.exceptions import TenantNotFoundError
from app.middleware.tenant import get_current_tenant_id
from pydantic import BaseModel, Field


# Pydantic models for tenant management
class TenantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, regex="^[a-z0-9-]+$")
    display_name: str = Field(..., min_length=2, max_length=255)
    billing_plan: str = Field(default="free", regex="^(free|starter|professional|enterprise)$")
    quota_storage_bytes: int = Field(default=10737418240)  # 10GB
    quota_processing_hours: int = Field(default=10)
    quota_jobs_per_month: int = Field(default=50)
    settings: dict = Field(default_factory=dict)


class TenantUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=255)
    billing_plan: Optional[str] = Field(None, regex="^(free|starter|professional|enterprise)$")
    quota_storage_bytes: Optional[int] = Field(None, gt=0)
    quota_processing_hours: Optional[int] = Field(None, gt=0)
    quota_jobs_per_month: Optional[int] = Field(None, gt=0)
    settings: Optional[dict] = None
    is_active: Optional[bool] = None


class TenantResponse(BaseModel):
    id: str
    name: str
    display_name: str
    billing_plan: str
    quota_storage_bytes: int
    quota_processing_hours: int
    quota_jobs_per_month: int
    settings: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Usage statistics
    user_count: Optional[int] = None
    storage_used: Optional[int] = None
    processing_hours_used: Optional[float] = None
    jobs_this_month: Optional[int] = None


class TenantUsageStats(BaseModel):
    tenant_id: str
    period_start: datetime
    period_end: datetime
    storage_used_bytes: int
    processing_hours_used: float
    jobs_completed: int
    api_calls: int
    bandwidth_used_bytes: int


class TenantSecurityConfig(BaseModel):
    allowed_countries: List[str] = Field(default_factory=list)
    blocked_countries: List[str] = Field(default_factory=list)
    allowed_ips: List[str] = Field(default_factory=list)
    blocked_ips: List[str] = Field(default_factory=list)
    require_2fa: bool = False
    max_login_attempts: int = 5
    lockout_duration: int = 3600


router = APIRouter(prefix="/admin/tenants", tags=["tenant-management"])


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new tenant."""
    
    # Check if tenant name already exists
    query = select(Tenant).where(Tenant.name == tenant_data.name)
    result = await db.execute(query)
    existing_tenant = result.scalar_one_or_none()
    
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tenant with name '{tenant_data.name}' already exists"
        )
    
    # Create new tenant
    tenant = Tenant(
        id=uuid.uuid4(),
        **tenant_data.dict()
    )
    
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    
    return TenantResponse(**tenant.to_dict())


@router.get("/", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    billing_plan: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_session)
):
    """List all tenants with pagination and filtering."""
    
    query = select(Tenant)
    
    # Apply filters
    if active_only:
        query = query.where(Tenant.is_active == True)
    
    if billing_plan:
        query = query.where(Tenant.billing_plan == billing_plan)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Tenant.name.ilike(search_term)) |
            (Tenant.display_name.ilike(search_term))
        )
    
    # Add pagination
    query = query.offset(skip).limit(limit).order_by(Tenant.created_at.desc())
    
    result = await db.execute(query)
    tenants = result.scalars().all()
    
    # Get usage statistics for each tenant
    tenant_responses = []
    for tenant in tenants:
        tenant_dict = tenant.to_dict()
        
        # Get user count
        user_count_query = select(func.count(User.id)).where(User.tenant_id == tenant.id)
        user_count_result = await db.execute(user_count_query)
        tenant_dict["user_count"] = user_count_result.scalar()
        
        tenant_responses.append(TenantResponse(**tenant_dict))
    
    return tenant_responses


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """Get tenant details by ID."""
    
    query = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(query)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    tenant_dict = tenant.to_dict()
    
    # Get usage statistics
    user_count_query = select(func.count(User.id)).where(User.tenant_id == tenant.id)
    user_count_result = await db.execute(user_count_query)
    tenant_dict["user_count"] = user_count_result.scalar()
    
    return TenantResponse(**tenant_dict)


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    tenant_update: TenantUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """Update tenant configuration."""
    
    query = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(query)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Update tenant with provided fields
    update_data = tenant_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(tenant, field, value)
    
    await db.commit()
    await db.refresh(tenant)
    
    return TenantResponse(**tenant.to_dict())


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: str,
    force: bool = Query(False, description="Force delete even if tenant has users"),
    db: AsyncSession = Depends(get_async_session)
):
    """Delete a tenant (soft delete by default)."""
    
    query = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(query)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Check if tenant has users
    user_count_query = select(func.count(User.id)).where(User.tenant_id == tenant.id)
    user_count_result = await db.execute(user_count_query)
    user_count = user_count_result.scalar()
    
    if user_count > 0 and not force:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tenant has {user_count} users. Use force=true to delete anyway."
        )
    
    if force:
        # Hard delete
        await db.delete(tenant)
    else:
        # Soft delete
        tenant.is_active = False
    
    await db.commit()


@router.get("/{tenant_id}/usage", response_model=TenantUsageStats)
async def get_tenant_usage(
    tenant_id: str,
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_async_session)
):
    """Get tenant usage statistics for a specific period."""
    
    # Default to current month if no period specified
    if not period_start:
        period_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    if not period_end:
        period_end = datetime.now()
    
    # Verify tenant exists
    tenant_query = select(Tenant).where(Tenant.id == tenant_id)
    tenant_result = await db.execute(tenant_query)
    tenant = tenant_result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Aggregate usage statistics
    usage_query = select(
        func.sum(UsageTracking.amount).filter(UsageTracking.resource_type == "storage").label("storage_used"),
        func.sum(UsageTracking.amount).filter(UsageTracking.resource_type == "processing_time").label("processing_hours"),
        func.count(UsageTracking.id).filter(UsageTracking.resource_type == "job").label("jobs_completed"),
        func.sum(UsageTracking.amount).filter(UsageTracking.resource_type == "api_calls").label("api_calls"),
        func.sum(UsageTracking.amount).filter(UsageTracking.resource_type == "bandwidth").label("bandwidth_used")
    ).where(
        (UsageTracking.tenant_id == tenant_id) &
        (UsageTracking.created_at >= period_start) &
        (UsageTracking.created_at <= period_end)
    )
    
    usage_result = await db.execute(usage_query)
    usage_row = usage_result.first()
    
    return TenantUsageStats(
        tenant_id=tenant_id,
        period_start=period_start,
        period_end=period_end,
        storage_used_bytes=int(usage_row.storage_used or 0),
        processing_hours_used=float(usage_row.processing_hours or 0),
        jobs_completed=int(usage_row.jobs_completed or 0),
        api_calls=int(usage_row.api_calls or 0),
        bandwidth_used_bytes=int(usage_row.bandwidth_used or 0)
    )


@router.put("/{tenant_id}/security", response_model=dict)
async def update_tenant_security(
    tenant_id: str,
    security_config: TenantSecurityConfig,
    db: AsyncSession = Depends(get_async_session)
):
    """Update tenant security configuration."""
    
    query = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(query)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Update security settings
    if not tenant.settings:
        tenant.settings = {}
    
    tenant.settings["security"] = security_config.dict()
    
    await db.commit()
    
    return {"message": "Security configuration updated successfully"}


@router.get("/{tenant_id}/security", response_model=TenantSecurityConfig)
async def get_tenant_security(
    tenant_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """Get tenant security configuration."""
    
    query = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(query)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    security_settings = tenant.settings.get("security", {}) if tenant.settings else {}
    
    return TenantSecurityConfig(**security_settings)


@router.post("/{tenant_id}/suspend", status_code=status.HTTP_200_OK)
async def suspend_tenant(
    tenant_id: str,
    reason: str = Query(..., description="Reason for suspension"),
    db: AsyncSession = Depends(get_async_session)
):
    """Suspend a tenant (emergency action)."""
    
    query = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(query)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    tenant.is_active = False
    
    # Log suspension reason
    if not tenant.settings:
        tenant.settings = {}
    
    tenant.settings["suspension"] = {
        "suspended_at": datetime.now().isoformat(),
        "reason": reason,
        "suspended_by": "admin"  # In real app, get from JWT
    }
    
    await db.commit()
    
    return {"message": f"Tenant {tenant.name} has been suspended", "reason": reason}


@router.post("/{tenant_id}/activate", status_code=status.HTTP_200_OK)
async def activate_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """Reactivate a suspended tenant."""
    
    query = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(query)
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    tenant.is_active = True
    
    # Remove suspension info
    if tenant.settings and "suspension" in tenant.settings:
        del tenant.settings["suspension"]
        tenant.settings["reactivated_at"] = datetime.now().isoformat()
    
    await db.commit()
    
    return {"message": f"Tenant {tenant.name} has been reactivated"}