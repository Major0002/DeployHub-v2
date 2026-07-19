"""Project database model."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.base import Base


class Project(Base):
    """Project model for deployment management."""

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Repository
    repo_url = Column(Text, nullable=True)
    repo_branch = Column(String(100), default="main")

    # Configuration
    language = Column(String(50), nullable=True)  # node, python, go, rust, etc.
    framework = Column(String(50), nullable=True)  # nextjs, fastapi, etc.
    build_command = Column(String(255), nullable=True)
    output_directory = Column(String(255), default="dist")

    # Environment variables (encrypted in production)
    env_vars = Column(JSON, default=dict)

    # Status
    status = Column(String(50), default="idle")  # idle, building, deployed, failed
    health_status = Column(String(50), default="unknown")  # healthy, unhealthy, unknown

    # Resources
    cpu_limit = Column(String(20), default="1")
    memory_limit = Column(String(20), default="512Mi")

    # Owner
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", backref="projects")

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_deployed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    deployments = relationship("Deployment", back_populates="project", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self):
        return f"<Project {self.name}>"
