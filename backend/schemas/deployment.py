"""Deployment Pydantic schemas."""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class DeploymentBase(BaseModel):
    """Base deployment schema."""
    commit_sha: Optional[str] = None
    commit_message: Optional[str] = None
    branch: str = "main"


class DeploymentCreate(DeploymentBase):
    """Schema for creating a deployment."""
    pass


class DeploymentResponse(DeploymentBase):
    """Schema for deployment response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    image_tag: Optional[str] = None
    container_id: Optional[str] = None
    build_logs: Optional[str] = None
    runtime_logs: Optional[str] = None
    build_duration_ms: Optional[int] = None
    deploy_duration_ms: Optional[int] = None
    preview_url: Optional[str] = None
    production_url: Optional[str] = None
    error_message: Optional[str] = None
    project_id: UUID
    triggered_by: Optional[UUID] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class DeploymentLog(BaseModel):
    """Deployment log entry."""
    timestamp: datetime
    level: str = Field(..., pattern="^(info|warn|error|debug)$")
    message: str
    source: str = "build"  # build, runtime, system
