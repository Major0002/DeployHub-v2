"""Deployment management API routes."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import get_db
from models.user import User
from schemas.deployment import (
    DeploymentResponse,
    DeploymentTriggerRequest,
    DeploymentStatusUpdate
)
from services.deployment_service import DeploymentService
from services.project_service import ProjectService
from utils.dependencies import get_current_user

router = APIRouter(prefix="/deployments", tags=["Deployments"])


@router.get("/", response_model=List[DeploymentResponse])
async def list_user_deployments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all deployments across projects owned by the current user."""
    deploy_service = DeploymentService(db)
    return await deploy_service.get_user_deployments(current_user.id, skip=skip, limit=limit)


@router.post("/project/{project_id}", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def trigger_project_deployment(
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
    deployment = await deploy_service.create(
        project=project,
        user_id=current_user.id,
        trigger_data=trigger_data
    )
    return deployment


@router.get("/project/{project_id}", response_model=List[DeploymentResponse])
async def list_project_deployments(
    project_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all deployments for a specific project."""
    project_service = ProjectService(db)
    project = await project_service.get_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")

    deploy_service = DeploymentService(db)
    return await deploy_service.get_project_deployments(project_id, skip=skip, limit=limit)


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get deployment details by ID."""
    deploy_service = DeploymentService(db)
    deployment = await deploy_service.get_by_id(deployment_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    if (
        deployment.project
        and deployment.project.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    return deployment


@router.patch("/{deployment_id}/status", response_model=DeploymentResponse)
async def update_deployment_status(
    deployment_id: UUID,
    update_data: DeploymentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update deployment status, duration, or logs."""
    deploy_service = DeploymentService(db)
    deployment = await deploy_service.get_by_id(deployment_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    if (
        deployment.project
        and deployment.project.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    updated = await deploy_service.update_status(deployment_id, update_data)
    return updated


@router.post("/{deployment_id}/cancel", response_model=DeploymentResponse)
async def cancel_deployment(
    deployment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel an active deployment."""
    deploy_service = DeploymentService(db)
    deployment = await deploy_service.get_by_id(deployment_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    if (
        deployment.project
        and deployment.project.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    cancelled = await deploy_service.cancel(deployment_id)
    return cancelled


@router.post("/{deployment_id}/rollback", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def rollback_deployment(
    deployment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Roll back to a previous deployment version."""
    deploy_service = DeploymentService(db)
    deployment = await deploy_service.get_by_id(deployment_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Target deployment not found")

    if (
        deployment.project
        and deployment.project.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    new_deployment = await deploy_service.rollback(deployment_id, current_user.id)
    if not new_deployment:
        raise HTTPException(status_code=400, detail="Could not rollback deployment")

    return new_deployment


@router.get("/{deployment_id}/logs")
async def get_deployment_logs(
    deployment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get deployment build and runtime logs."""
    deploy_service = DeploymentService(db)
    deployment = await deploy_service.get_by_id(deployment_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    if (
        deployment.project
        and deployment.project.owner_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "deployment_id": deployment.id,
        "status": deployment.status,
        "build_logs": deployment.build_logs or "",
        "runtime_logs": deployment.runtime_logs or ""
    }
