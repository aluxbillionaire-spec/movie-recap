"""
Tenant Model

Multi-tenant support with quota management.
"""

from sqlalchemy import Column, String, Boolean, TIMESTAMP, BigInteger, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Tenant(Base):
    """Tenant model for multi-tenancy support."""
    
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    billing_plan = Column(String(50), default="free")
    quota_storage_bytes = Column(BigInteger, default=10737418240)  # 10GB
    quota_processing_hours = Column(Integer, default=10)
    quota_jobs_per_month = Column(Integer, default=50)
    settings = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    projects = relationship("Project", back_populates="tenant")
    assets = relationship("Asset", back_populates="tenant")
    jobs = relationship("Job", back_populates="tenant")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name}, plan={self.billing_plan})>"
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "name": self.name,
            "display_name": self.display_name,
            "billing_plan": self.billing_plan,
            "quota_storage_bytes": self.quota_storage_bytes,
            "quota_processing_hours": self.quota_processing_hours,
            "quota_jobs_per_month": self.quota_jobs_per_month,
            "settings": self.settings,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }