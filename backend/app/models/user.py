"""
User Model

SQLAlchemy model for user management with multi-tenant support.
"""

from sqlalchemy import Column, String, Boolean, TIMESTAMP, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class User(Base):
    """User model with multi-tenant support."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    roles = Column(ARRAY(Text), default=["user"])
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    preferences = Column(JSONB, default={})
    last_login = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, tenant_id={self.tenant_id})>"
    
    @property
    def full_name(self):
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in (self.roles or [])
    
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.has_role("admin")
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "roles": self.roles,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "preferences": self.preferences,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }