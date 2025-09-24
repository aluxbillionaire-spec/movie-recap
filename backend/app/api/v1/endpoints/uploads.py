"""
Uploads API Endpoints

Handle file uploads with chunked/resumable upload support and Google Drive integration.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, validator
import uuid
import os
import tempfile
import hashlib
import mimetypes
from datetime import datetime, timedelta

from app.core.database import get_db_session
from app.core.security import get_current_user_token
from app.models.project import Project
from app.models.asset import Asset
from app.core.config import settings
from app.services.google_drive import GoogleDriveService
from app.workers.preprocessing import validate_upload
from app.core.exceptions import ValidationException, QuotaExceededException

router = APIRouter()


# Pydantic models
class UploadInitRequest(BaseModel):
    project_id: str
    file_type: str  # video, script
    filename: str
    file_size: int
    content_type: Optional[str] = None
    
    @validator('file_type')
    def validate_file_type(cls, v):
        if v not in ['video', 'script']:
            raise ValueError('file_type must be "video" or "script"')
        return v
    
    @validator('file_size')
    def validate_file_size(cls, v):
        if v <= 0:
            raise ValueError('file_size must be positive')
        if v > settings.MAX_UPLOAD_SIZE:
            raise ValueError(f'file_size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes')
        return v
    
    @validator('filename')
    def validate_filename(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('filename cannot be empty')
        
        # Check for dangerous characters
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        if any(char in v for char in dangerous_chars):
            raise ValueError('filename contains invalid characters')
        
        return v.strip()


class UploadSession(BaseModel):
    upload_id: str
    drive_folder_id: str
    upload_url: str
    expires_at: str
    chunk_size: int = 8 * 1024 * 1024  # 8MB chunks


class UploadCompleteRequest(BaseModel):
    checksum: Optional[str] = None


class AssetResponse(BaseModel):
    id: str
    project_id: str
    type: str
    filename: str
    size_bytes: int
    duration_seconds: Optional[float]
    content_type: Optional[str]
    status: str
    metadata: dict
    created_at: str
    updated_at: str


@router.post("/init", response_model=UploadSession)
async def initialize_upload(
    upload_request: UploadInitRequest,
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """Initialize a resumable upload session."""
    
    try:
        project_uuid = uuid.UUID(upload_request.project_id)
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
    
    # Check quota
    await check_upload_quota(
        current_user["tenant_id"], 
        upload_request.file_size, 
        db
    )
    
    # Validate file extension
    file_ext = os.path.splitext(upload_request.filename)[1].lower()
    
    if upload_request.file_type == 'video':
        if file_ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported video format. Allowed: {', '.join(settings.ALLOWED_VIDEO_EXTENSIONS)}"
            )
    elif upload_request.file_type == 'script':
        if file_ext not in settings.ALLOWED_SCRIPT_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported script format. Allowed: {', '.join(settings.ALLOWED_SCRIPT_EXTENSIONS)}"
            )
    
    try:
        # Initialize Google Drive upload
        drive_service = GoogleDriveService()
        upload_session = await drive_service.create_resumable_upload(
            filename=upload_request.filename,
            file_size=upload_request.file_size,
            content_type=upload_request.content_type,
            folder_path=f"inputs/{current_user['user_id']}/{project_uuid}"
        )
        
        return UploadSession(
            upload_id=upload_session['upload_id'],
            drive_folder_id=upload_session['folder_id'],
            upload_url=upload_session['upload_url'],
            expires_at=(datetime.utcnow() + timedelta(hours=24)).isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize upload: {str(e)}"
        )


@router.post("/{upload_id}/complete")
async def complete_upload(
    upload_id: str,
    complete_request: UploadCompleteRequest,
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """Complete upload and trigger processing."""
    
    try:
        # Get upload session info from Google Drive
        drive_service = GoogleDriveService()
        upload_info = await drive_service.complete_upload(upload_id)
        
        if not upload_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload session not found"
            )
        
        # Verify project access
        project_uuid = uuid.UUID(upload_info['project_id'])
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
        
        # Verify checksum if provided
        if complete_request.checksum:
            if upload_info.get('checksum') != complete_request.checksum:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Checksum mismatch"
                )
        
        # Create asset record
        asset = Asset(
            project_id=project_uuid,
            tenant_id=current_user["tenant_id"],
            type=upload_info['file_type'],
            filename=upload_info['filename'],
            storage_path=upload_info['file_path'],
            content_type=upload_info.get('content_type'),
            size_bytes=upload_info['file_size'],
            checksum=upload_info.get('checksum'),
            status='uploaded',
            metadata=upload_info.get('metadata', {})
        )
        
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        
        # Trigger validation and preprocessing
        from app.workers.celery_app import celery_app
        
        # Queue validation task
        validation_task = validate_upload.delay(
            file_path=upload_info['file_path'],
            file_type=upload_info['file_type']
        )
        
        # Queue preprocessing if validation succeeds
        if upload_info['file_type'] == 'video':
            from app.workers.preprocessing import preprocess_video
            
            preprocess_task = preprocess_video.delay(
                job_id=str(uuid.uuid4()),
                asset_id=str(asset.id),
                file_path=upload_info['file_path']
            )
        
        return {
            "status": "success",
            "asset_id": str(asset.id),
            "validation_task_id": validation_task.id,
            "message": "Upload completed successfully. Processing started."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete upload: {str(e)}"
        )


@router.get("/{upload_id}/status")
async def get_upload_status(
    upload_id: str,
    current_user: dict = Depends(get_current_user_token)
):
    """Get upload session status."""
    
    try:
        drive_service = GoogleDriveService()
        status_info = await drive_service.get_upload_status(upload_id)
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload session not found"
            )
        
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upload status: {str(e)}"
        )


@router.post("/direct", response_model=AssetResponse)
async def direct_upload(
    project_id: str = Form(...),
    file_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """Direct file upload for smaller files (< 100MB)."""
    
    # Size limit for direct upload
    MAX_DIRECT_UPLOAD = 100 * 1024 * 1024  # 100MB
    
    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )
    
    # Verify project
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
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_DIRECT_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large for direct upload. Use resumable upload for files > {MAX_DIRECT_UPLOAD} bytes"
        )
    
    # Check quota
    await check_upload_quota(current_user["tenant_id"], file_size, db)
    
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Calculate checksum
        checksum = hashlib.sha256(content).hexdigest()
        
        # Upload to Google Drive
        drive_service = GoogleDriveService()
        drive_info = await drive_service.upload_file(
            file_path=temp_path,
            filename=file.filename,
            folder_path=f"inputs/{current_user['user_id']}/{project_uuid}"
        )
        
        # Create asset record
        asset = Asset(
            project_id=project_uuid,
            tenant_id=current_user["tenant_id"],
            type=file_type,
            filename=file.filename,
            storage_path=drive_info['file_path'],
            content_type=file.content_type,
            size_bytes=file_size,
            checksum=checksum,
            status='uploaded',
            metadata={'upload_method': 'direct'}
        )
        
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        
        # Cleanup temp file
        os.unlink(temp_path)
        
        return AssetResponse(**asset.to_dict())
        
    except Exception as e:
        await db.rollback()
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


async def check_upload_quota(tenant_id: str, file_size: int, db: AsyncSession):
    """Check if upload would exceed tenant quota."""
    
    from app.models.tenant import Tenant
    from sqlalchemy import func
    
    # Get tenant quota
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Calculate current usage
    usage_result = await db.execute(
        select(func.coalesce(func.sum(Asset.size_bytes), 0)).where(
            Asset.tenant_id == tenant_id
        )
    )
    current_usage = usage_result.scalar()
    
    # Check if new upload would exceed quota
    if current_usage + file_size > tenant.quota_storage_bytes:
        raise QuotaExceededException(
            message="Upload would exceed storage quota",
            quota_type="storage",
            current_usage=current_usage,
            limit=tenant.quota_storage_bytes
        )