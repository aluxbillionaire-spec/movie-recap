"""
Asset Model

File metadata storage for videos, scripts, and outputs.
"""

from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, BigInteger, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Asset(Base):
    """Asset model for file metadata storage."""
    
    __tablename__ = "assets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # video, script, thumbnail, output
    filename = Column(String(255), nullable=False)
    storage_path = Column(Text, nullable=False)
    content_type = Column(String(100))
    size_bytes = Column(BigInteger, nullable=False)
    duration_seconds = Column(Numeric(10, 3))  # For video/audio files
    metadata = Column(JSONB, default={})
    checksum = Column(String(64))
    status = Column(String(50), default="uploaded")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="assets")
    tenant = relationship("Tenant", back_populates="assets")
    transcripts = relationship("Transcript", back_populates="asset", cascade="all, delete-orphan")
    moderation_records = relationship("ContentModeration", back_populates="asset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Asset(id={self.id}, type={self.type}, filename={self.filename})>"
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "tenant_id": str(self.tenant_id),
            "type": self.type,
            "filename": self.filename,
            "storage_path": self.storage_path,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "duration_seconds": float(self.duration_seconds) if self.duration_seconds else None,
            "metadata": self.metadata,
            "checksum": self.checksum,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }