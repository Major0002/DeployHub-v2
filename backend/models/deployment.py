"""Deployment database model."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON, Uuid
from sqlalchemy.orm import relationship

from database.base import Base


class Deployment(Base):
    """Deployment model tracking individual deployments."""

    __tablename__ = "deployments"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Status
    status = Column(String(50), default="pending")  # pending, building, running, success, failed, cancelled, rolled_back

    # Build info
    commit_sha = Column(String(100), nullable=True)
    commit_message = Column(Text, nullable=True)
    branch = Column(String(100), default="main")

    # Docker
    image_tag = Column(String(255), nullable=True)
    container_id = Column(String(255), nullable=True)

    # Logs
    build_logs = Column(Text, nullable=True)
    runtime_logs = Column(Text, nullable=True)

    # Metrics
    build_duration_ms = Column(Integer, nullable=True)
    deploy_duration_ms = Column(Integer, nullable=True)

    # URLs
    preview_url = Column(Text, nullable=True)
    production_url = Column(Text, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)
    error_stack = Column(Text, nullable=True)

    # Metadata stored in column 'metadata'
    deploy_metadata = Column("metadata", JSON, default=dict)

    # Foreign keys
    project_id = Column(Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    project = relationship("Project", back_populates="deployments")

    triggered_by = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    triggerer = relationship("User", foreign_keys=[triggered_by])

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Deployment {self.id} - {self.status}>"

