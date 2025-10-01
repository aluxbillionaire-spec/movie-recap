"""
Jobs API Endpoints

Job management and monitoring for processing tasks.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from pydantic import BaseModel, validator
import uuid
from datetime import datetime

from app.core.database import get_db_session
from app.core.security import get_current_user_token
from app.models.job import Job
from app.models.project import Project
from app.workers.celery_app import celery_app
from app.core.exceptions import ValidationException, PermissionException

router = APIRouter()


# Pydantic models
class JobAction(BaseModel):
    action: str
    payload: Optional[Dict[str, Any]] = {}
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = [
            'approve_scenes', 'reject_scenes', 'retry', 'cancel', 
            'continue_processing', 'adjust_settings'
        ]
        if v not in allowed_actions:
            raise ValueError(f'action must be one of: {", ".join(allowed_actions)}')
        return v


class JobResponse(BaseModel):
    id: str
    project_id: str
    type: str
    status: str
    priority: int
    progress: Dict[str, Any]
    config: Dict[str, Any]
    input_assets: List[str]
    output_assets: List[str]
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    estimated_duration: Optional[int]
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    limit: int
    offset: int


class JobProgressUpdate(BaseModel):
    percent: float
    stage: str
    details: Dict[str, Any] = {}
    estimated_completion: Optional[datetime] = None


@router.get("", response_model=JobListResponse)
async def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None, alias="type"),
    project_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """List user's jobs with filtering and pagination."""
    
    # Base query - only jobs for user's projects
    query = select(Job).join(Project).where(
        and_(
            Project.user_id == current_user["user_id"],
            Project.tenant_id == current_user["tenant_id"]
        )
    )
    
    # Apply filters
    if status:
        query = query.where(Job.status == status)
    
    if job_type:
        query = query.where(Job.type == job_type)
    
    if project_id:
        try:
            project_uuid = uuid.UUID(project_id)
            query = query.where(Job.project_id == project_uuid)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid project ID format"
            )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(Job.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return JobListResponse(
        items=[JobResponse.from_orm(job) for job in jobs],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """Get job details by ID."""
    
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )
    
    # Query job with project access check
    result = await db.execute(
        select(Job).join(Project).where(
            and_(
                Job.id == job_uuid,
                Project.user_id == current_user["user_id"],
                Project.tenant_id == current_user["tenant_id"]
            )
        )
    )
    
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return JobResponse.from_orm(job)


@router.post("/{job_id}/actions", response_model=JobResponse)
async def perform_job_action(
    job_id: str,
    action: JobAction,
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """Perform manual actions on jobs."""
    
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )
    
    # Get job with access check
    result = await db.execute(
        select(Job).join(Project).where(
            and_(
                Job.id == job_uuid,
                Project.user_id == current_user["user_id"],
                Project.tenant_id == current_user["tenant_id"]
            )
        )
    )
    
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    try:
        # Handle different actions
        if action.action == "approve_scenes":
            await handle_approve_scenes(job, action.payload, db)
            
        elif action.action == "reject_scenes":
            await handle_reject_scenes(job, action.payload, db)
            
        elif action.action == "retry":
            await handle_retry_job(job, db)
            
        elif action.action == "cancel":
            await handle_cancel_job(job, db)
            
        elif action.action == "continue_processing":
            await handle_continue_processing(job, action.payload, db)
            
        elif action.action == "adjust_settings":
            await handle_adjust_settings(job, action.payload, db)
        
        await db.commit()
        await db.refresh(job)
        
        return JobResponse.from_orm(job)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform action: {str(e)}"
        )


@router.get("/{job_id}/progress")
async def get_job_progress(
    job_id: str,
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """Get detailed job progress information."""
    
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )
    
    # Get job
    result = await db.execute(
        select(Job).join(Project).where(
            and_(
                Job.id == job_uuid,
                Project.user_id == current_user["user_id"],
                Project.tenant_id == current_user["tenant_id"]
            )
        )
    )
    
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get real-time progress from Celery if job is running
    celery_progress = None
    if job.status in ["pending", "running"]:
        try:
            # Get Celery task info
            task_result = celery_app.AsyncResult(str(job.id))
            if task_result.state in ["PENDING", "PROGRESS"]:
                celery_progress = {
                    "state": task_result.state,
                    "info": task_result.info
                }
        except Exception:
            # Celery task not found or error - use DB progress
            pass
    
    progress_data = {
        "job_id": str(job.id),
        "status": job.status,
        "progress": job.progress,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "estimated_completion": None,
        "runtime_seconds": None
    }
    
    # Calculate runtime and estimated completion
    if job.started_at:
        runtime = datetime.utcnow() - job.started_at
        progress_data["runtime_seconds"] = runtime.total_seconds()
        
        # Estimate completion based on current progress
        percent = job.progress.get("percent", 0)
        if percent > 0 and job.estimated_duration:
            estimated_total = (runtime.total_seconds() / percent) * 100
            estimated_remaining = estimated_total - runtime.total_seconds()
            estimated_completion = datetime.utcnow() + timedelta(seconds=estimated_remaining)
            progress_data["estimated_completion"] = estimated_completion.isoformat()
    
    # Include Celery real-time data if available
    if celery_progress:
        progress_data["celery_state"] = celery_progress
    
    return progress_data


@router.get("/{job_id}/logs")
async def get_job_logs(
    job_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    level: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """Get job execution logs."""
    
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format"
        )
    
    # Verify job access
    result = await db.execute(
        select(Job).join(Project).where(
            and_(
                Job.id == job_uuid,
                Project.user_id == current_user["user_id"],
                Project.tenant_id == current_user["tenant_id"]
            )
        )
    )
    
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get logs from audit_logs table
    from app.models.audit_log import AuditLog
    
    query = select(AuditLog).where(
        AuditLog.resource_id == job_uuid
    )
    
    if level:
        query = query.where(AuditLog.level == level)
    
    query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
    
    logs_result = await db.execute(query)
    logs = logs_result.scalars().all()
    
    return {
        "job_id": str(job_uuid),
        "logs": [
            {
                "id": str(log.id),
                "level": log.level,
                "message": log.message,
                "timestamp": log.created_at.isoformat(),
                "details": log.details
            }
            for log in logs
        ],
        "limit": limit,
        "offset": offset
    }


# Action handlers
async def handle_approve_scenes(job: Job, payload: Dict[str, Any], db: AsyncSession):
    """Handle scene approval action."""
    
    if job.status != "manual_review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not in manual review status"
        )
    
    scene_ids = payload.get("scene_ids", [])
    
    if not scene_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No scene IDs provided"
        )
    
    # Update scenes as approved
    from app.models.scene import Scene
    
    await db.execute(
        update(Scene).where(
            and_(
                Scene.job_id == job.id,
                Scene.id.in_(scene_ids)
            )
        ).values(user_approved=True, manual_review_required=False)
    )
    
    # Check if all scenes are approved
    remaining_result = await db.execute(
        select(func.count()).where(
            and_(
                Scene.job_id == job.id,
                Scene.manual_review_required == True
            )
        )
    )
    
    remaining_count = remaining_result.scalar()
    
    if remaining_count == 0:
        # All scenes approved, continue processing
        job.status = "pending"
        
        # Queue next processing step
        from app.workers.assembly import assemble_video
        assemble_video.delay(str(job.id))


async def handle_reject_scenes(job: Job, payload: Dict[str, Any], db: AsyncSession):
    """Handle scene rejection action."""
    
    if job.status != "manual_review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not in manual review status"
        )
    
    scene_ids = payload.get("scene_ids", [])
    rejection_reason = payload.get("reason", "User rejected")
    
    if not scene_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No scene IDs provided"
        )
    
    # Mark scenes as rejected
    from app.models.scene import Scene
    
    await db.execute(
        update(Scene).where(
            and_(
                Scene.job_id == job.id,
                Scene.id.in_(scene_ids)
            )
        ).values(
            user_approved=False,
            manual_review_required=False,
            flagged_reason=rejection_reason
        )
    )


async def handle_retry_job(job: Job, db: AsyncSession):
    """Handle job retry action."""
    
    if job.status not in ["failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job cannot be retried in current status"
        )
    
    if job.retry_count >= job.max_retries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum retry attempts reached"
        )
    
    # Reset job status and increment retry count
    job.status = "pending"
    job.retry_count += 1
    job.error_message = None
    job.started_at = None
    job.completed_at = None
    
    # Queue job for processing
    queue_job_for_processing(job)


async def handle_cancel_job(job: Job, db: AsyncSession):
    """Handle job cancellation."""
    
    if job.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job cannot be cancelled in current status"
        )
    
    # Cancel Celery task if running
    if job.status in ["pending", "running"]:
        try:
            celery_app.control.revoke(str(job.id), terminate=True)
        except Exception:
            pass
    
    job.status = "cancelled"
    job.completed_at = datetime.utcnow()


async def handle_continue_processing(job: Job, payload: Dict[str, Any], db: AsyncSession):
    """Handle continue processing action (after upscaling, etc.)."""
    
    upscaled_video_path = payload.get("upscaled_video_path")
    
    if upscaled_video_path:
        # Update job config with upscaled video path
        job.config = job.config or {}
        job.config["upscaled_video_path"] = upscaled_video_path
    
    # Continue with next step
    job.status = "pending"
    
    # Queue appropriate next step
    queue_job_for_processing(job)


async def handle_adjust_settings(job: Job, payload: Dict[str, Any], db: AsyncSession):
    """Handle job settings adjustment."""
    
    settings = payload.get("settings", {})
    
    # Update job configuration
    job.config = job.config or {}
    job.config.update(settings)


def queue_job_for_processing(job: Job):
    """Queue job for appropriate processing step."""
    
    if job.type == "preprocess":
        from app.workers.preprocessing import preprocess_video
        preprocess_video.delay(str(job.id), "", "")
        
    elif job.type == "transcription":
        from app.workers.transcription import transcribe_audio
        transcribe_audio.delay(str(job.id), "", "")
        
    elif job.type == "alignment":
        from app.workers.alignment import align_script_to_video
        align_script_to_video.delay(str(job.id))
        
    elif job.type == "assembly":
        from app.workers.assembly import assemble_video
        assemble_video.delay(str(job.id))