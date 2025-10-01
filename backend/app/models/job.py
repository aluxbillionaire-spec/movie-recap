"""
Job Model

Processing job management and tracking.
"""

from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Job(Base):
    """Job model for processing task management."""
    
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # preprocess, align, assemble, upscale, finalize
    status = Column(String(50), default="pending")  # pending, running, manual_review, completed, failed, cancelled
    priority = Column(Integer, default=0)
    progress = Column(JSONB, default={"percent": 0, "stage": "initializing", "details": {}})
    config = Column(JSONB, default={})
    input_assets = Column(ARRAY(UUID), default=[])
    output_assets = Column(ARRAY(UUID), default=[])
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    estimated_duration = Column(Integer)  # seconds
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="jobs")
    tenant = relationship("Tenant", back_populates="jobs")
    scenes = relationship("Scene", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Job(id={self.id}, type={self.type}, status={self.status})>"
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "tenant_id": str(self.tenant_id),
            "type": self.type,
            "status": self.status,
            "priority": self.priority,
            "progress": self.progress,
            "config": self.config,
            "input_assets": [str(asset_id) for asset_id in (self.input_assets or [])],
            "output_assets": [str(asset_id) for asset_id in (self.output_assets or [])],
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "estimated_duration": self.estimated_duration,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }