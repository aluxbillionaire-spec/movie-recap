"""
Project Model

Project management for organizing user uploads and processing jobs.
"""

from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Project(Base):
    """Project model for organizing user content."""
    
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    settings = Column(JSONB, default={})
    status = Column(String(50), default="active")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="projects")
    tenant = relationship("Tenant", back_populates="projects")
    assets = relationship("Asset", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, title={self.title}, user_id={self.user_id})>"
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "tenant_id": str(self.tenant_id),
            "title": self.title,
            "description": self.description,
            "settings": self.settings,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }