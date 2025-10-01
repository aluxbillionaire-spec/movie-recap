"""
Projects API Endpoints

Project management functionality for organizing user uploads and processing jobs.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, validator
import uuid

from app.core.database import get_db_session
from app.core.security import get_current_user_token
from app.models.project import Project
from app.models.user import User
from app.core.exceptions import ValidationException, PermissionException

router = APIRouter()


# Pydantic models
class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    settings: Optional[dict] = {}
    
    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters long')
        if len(v) > 255:
            raise ValueError('Title must be less than 255 characters')
        return v.strip()


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[dict] = None
    status: Optional[str] = None
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if len(v.strip()) < 3:
                raise ValueError('Title must be at least 3 characters long')
            if len(v) > 255:
                raise ValueError('Title must be less than 255 characters')
        return v.strip() if v else None


class ProjectResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    settings: dict
    status: str
    user_id: str
    tenant_id: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    limit: int
    offset: int


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """List user's projects with pagination and filtering."""
    
    # Build query
    query = select(Project).where(
        and_(
            Project.user_id == current_user["user_id"],
            Project.tenant_id == current_user["tenant_id"]
        )
    )
    
    # Add filters
    if status:
        query = query.where(Project.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            Project.title.ilike(search_term) | 
            Project.description.ilike(search_term)
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(Project.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return ProjectListResponse(
        items=[ProjectResponse.from_orm(project) for project in projects],
        total=total,
        limit=limit,
        offset=offset
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new project."""
    
    try:
        # Create project
        project = Project(
            title=project_data.title,
            description=project_data.description,
            settings=project_data.settings or {},
            user_id=current_user["user_id"],
            tenant_id=current_user["tenant_id"]
        )
        
        db.add(project)
        await db.commit()
        await db.refresh(project)
        
        return ProjectResponse.from_orm(project)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """Get project by ID."""
    
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Query project with user/tenant check
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == project_uuid,
                Project.user_id == current_user["user_id"],
                Project.tenant_id == current_user["tenant_id"]
            )
        )
    )
    
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return ProjectResponse.from_orm(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """Update project."""
    
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Get project
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == project_uuid,
                Project.user_id == current_user["user_id"],
                Project.tenant_id == current_user["tenant_id"]
            )
        )
    )
    
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    try:
        # Update fields
        update_data = project_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(project, field, value)
        
        await db.commit()
        await db.refresh(project)
        
        return ProjectResponse.from_orm(project)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete project and all associated data."""
    
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Get project
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == project_uuid,
                Project.user_id == current_user["user_id"],
                Project.tenant_id == current_user["tenant_id"]
            )
        )
    )
    
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    try:
        # Check if project has active jobs
        from app.models.job import Job
        
        jobs_result = await db.execute(
            select(Job).where(
                and_(
                    Job.project_id == project_uuid,
                    Job.status.in_(["pending", "running", "manual_review"])
                )
            )
        )
        
        active_jobs = jobs_result.scalars().all()
        
        if active_jobs:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete project with active jobs. Please wait for jobs to complete or cancel them first."
            )
        
        # Delete project (cascading deletes will handle related data)
        await db.delete(project)
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )


@router.get("/{project_id}/stats")
async def get_project_stats(
    project_id: str,
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """Get project statistics."""
    
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Verify project exists and user has access
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == project_uuid,
                Project.user_id == current_user["user_id"],
                Project.tenant_id == current_user["tenant_id"]
            )
        )
    )
    
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get statistics
    from app.models.asset import Asset
    from app.models.job import Job
    from sqlalchemy import func
    
    # Asset stats
    assets_result = await db.execute(
        select(
            Asset.type,
            func.count(Asset.id).label('count'),
            func.sum(Asset.size_bytes).label('total_size')
        ).where(Asset.project_id == project_uuid).group_by(Asset.type)
    )
    
    assets_stats = {}
    for row in assets_result:
        assets_stats[row.type] = {
            'count': row.count,
            'total_size_bytes': row.total_size or 0
        }
    
    # Job stats
    jobs_result = await db.execute(
        select(
            Job.status,
            func.count(Job.id).label('count')
        ).where(Job.project_id == project_uuid).group_by(Job.status)
    )
    
    jobs_stats = {}
    for row in jobs_result:
        jobs_stats[row.status] = row.count
    
    return {
        "project_id": str(project_uuid),
        "assets": assets_stats,
        "jobs": jobs_stats,
        "created_at": project.created_at.isoformat(),
        "last_updated": project.updated_at.isoformat()
    }