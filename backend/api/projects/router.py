from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import get_db
from schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetail, ProjectStats
from schemas.deployment import DeploymentResponse, DeploymentTriggerRequest
from services.project_service import ProjectService
from services.deployment_service import DeploymentService
from utils.dependencies import get_current_user
from models.user import User

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all projects for the current user."""
    project_service = ProjectService(db)
    return await project_service.get_user_projects(current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project."""
    project_service = ProjectService(db)
    project = await project_service.create(current_user.id, project_data)
    return project


@router.get("/stats", response_model=ProjectStats)
async def get_project_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get project statistics for the current user."""
    project_service = ProjectService(db)
    return await project_service.get_stats(current_user.id)


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get project details by ID."""
    project_service = ProjectService(db)
    project = await project_service.get_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")

    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a project."""
    project_service = ProjectService(db)
    project = await project_service.get_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")

    updated = await project_service.update(project_id, project_data)
    return updated


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project."""
    project_service = ProjectService(db)
    project = await project_service.get_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")

    await project_service.delete(project_id)
    return None


@router.post("/{project_id}/deploy", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def deploy_project(
    project_id: UUID,
    trigger_data: Optional[DeploymentTriggerRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger a new deployment for a project."""
    project_service = ProjectService(db)
    project = await project_service.get_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")

    deploy_service = DeploymentService(db)
    return await deploy_service.create(
        project=project,
        user_id=current_user.id,
        trigger_data=trigger_data
    )

