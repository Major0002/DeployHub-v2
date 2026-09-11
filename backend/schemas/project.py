"""Project Pydantic schemas."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    repo_url: Optional[str] = None
    repo_branch: str = "main"
    language: Optional[str] = None
    framework: Optional[str] = None
    build_command: Optional[str] = None
    output_directory: str = "dist"
    env_vars: Dict[str, str] = Field(default_factory=dict)
    cpu_limit: str = "1"
    memory_limit: str = "512Mi"


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    repo_url: Optional[str] = None
    repo_branch: Optional[str] = None
    build_command: Optional[str] = None
    output_directory: Optional[str] = None
    env_vars: Optional[Dict[str, str]] = None
    cpu_limit: Optional[str] = None
    memory_limit: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    status: str
    health_status: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    last_deployed_at: Optional[datetime] = None


from schemas.deployment import DeploymentResponse


class ProjectDetail(ProjectResponse):
    """Detailed project with deployments."""
    deployments: List[DeploymentResponse] = []


class ProjectStats(BaseModel):
    """Project statistics."""
    total_projects: int
    active_projects: int
    failed_projects: int
    total_deployments: int
    successful_deployments: int
    failed_deployments: int


# Resolve forward references
ProjectDetail.model_rebuild()

