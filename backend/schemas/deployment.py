"""Deployment Pydantic schemas."""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, AliasChoices


class DeploymentBase(BaseModel):
    """Base deployment schema."""
    commit_sha: Optional[str] = None
    commit_message: Optional[str] = None
    branch: str = "main"


class DeploymentCreate(DeploymentBase):
    """Schema for creating a deployment."""
    project_id: Optional[UUID] = None
    env_vars: Optional[Dict[str, str]] = None


class DeploymentTriggerRequest(DeploymentBase):
    """Schema for triggering a deployment."""
    image_tag: Optional[str] = None
    env_vars: Optional[Dict[str, str]] = None


class DeploymentStatusUpdate(BaseModel):
    """Schema for updating deployment status."""
    status: str = Field(..., pattern="^(pending|building|running|success|failed|cancelled|rolled_back)$")
    container_id: Optional[str] = None
    image_tag: Optional[str] = None
    preview_url: Optional[str] = None
    production_url: Optional[str] = None
    error_message: Optional[str] = None
    error_stack: Optional[str] = None
    build_duration_ms: Optional[int] = None
    deploy_duration_ms: Optional[int] = None


class DeploymentResponse(DeploymentBase):
    """Schema for deployment response."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

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
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("deploy_metadata", "metadata")
    )
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

