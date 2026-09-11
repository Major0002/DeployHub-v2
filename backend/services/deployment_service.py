"""Deployment business logic service."""
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.deployment import Deployment
from models.project import Project
from schemas.deployment import DeploymentTriggerRequest, DeploymentStatusUpdate


class DeploymentService:
    """Service for deployment operations and lifecycle management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, deployment_id: UUID) -> Optional[Deployment]:
        """Get deployment by ID with project details."""
        result = await self.db.execute(
            select(Deployment)
            .options(selectinload(Deployment.project))
            .where(Deployment.id == deployment_id)
        )
        return result.scalar_one_or_none()

    async def get_project_deployments(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Deployment]:
        """Get all deployments for a specific project."""
        result = await self.db.execute(
            select(Deployment)
            .where(Deployment.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .order_by(Deployment.created_at.desc())
        )
        return result.scalars().all()

    async def get_user_deployments(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Deployment]:
        """Get all deployments across projects owned by a user."""
        result = await self.db.execute(
            select(Deployment)
            .join(Project)
            .where(Project.owner_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Deployment.created_at.desc())
        )
        return result.scalars().all()

    async def create(
        self,
        project: Project,
        user_id: UUID,
        trigger_data: Optional[DeploymentTriggerRequest] = None
    ) -> Deployment:
        """Create and trigger a new deployment for a project."""
        now = datetime.now(timezone.utc)

        branch = (
            trigger_data.branch
            if trigger_data and trigger_data.branch
            else (project.repo_branch or "main")
        )
        commit_sha = trigger_data.commit_sha if trigger_data else None
        commit_message = (
            trigger_data.commit_message
            if trigger_data and trigger_data.commit_message
            else "Manual deployment triggered"
        )
        image_tag = (
            trigger_data.image_tag
            if trigger_data and trigger_data.image_tag
            else f"{project.slug}:{commit_sha[:7] if commit_sha else 'latest'}"
        )

        deployment = Deployment(
            project_id=project.id,
            triggered_by=user_id,
            status="pending",
            branch=branch,
            commit_sha=commit_sha,
            commit_message=commit_message,
            image_tag=image_tag,
            started_at=now,
            deploy_metadata={"env_vars_override": trigger_data.env_vars if trigger_data else {}}
        )

        # Update project status
        project.status = "building"
        project.last_deployed_at = now

        self.db.add(deployment)
        await self.db.commit()
        await self.db.refresh(deployment)
        return deployment

    async def update_status(
        self,
        deployment_id: UUID,
        update_data: DeploymentStatusUpdate
    ) -> Optional[Deployment]:
        """Update deployment status, duration, logs, and URLs."""
        deployment = await self.get_by_id(deployment_id)
        if not deployment:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(deployment, field, value)

        now = datetime.now(timezone.utc)
        if update_data.status in ["success", "failed", "cancelled", "rolled_back"]:
            if not deployment.completed_at:
                deployment.completed_at = now

            # Sync project status
            project = deployment.project
            if project:
                if update_data.status == "success":
                    project.status = "deployed"
                    project.health_status = "healthy"
                elif update_data.status == "failed":
                    project.status = "failed"
                    project.health_status = "unhealthy"
                elif update_data.status in ["cancelled", "rolled_back"]:
                    project.status = "idle"

        await self.db.commit()
        await self.db.refresh(deployment)
        return deployment

    async def cancel(self, deployment_id: UUID) -> Optional[Deployment]:
        """Cancel an in-progress deployment."""
        deployment = await self.get_by_id(deployment_id)
        if not deployment:
            return None

        if deployment.status in ["pending", "building", "running"]:
            deployment.status = "cancelled"
            deployment.completed_at = datetime.now(timezone.utc)
            if deployment.project:
                deployment.project.status = "idle"
            await self.db.commit()
            await self.db.refresh(deployment)

        return deployment

    async def rollback(
        self,
        deployment_id: UUID,
        user_id: UUID
    ) -> Optional[Deployment]:
        """Trigger a rollback deployment to a previous deployment's state."""
        target_deployment = await self.get_by_id(deployment_id)
        if not target_deployment or not target_deployment.project:
            return None

        rollback_trigger = DeploymentTriggerRequest(
            commit_sha=target_deployment.commit_sha,
            commit_message=f"Rollback to deployment {str(target_deployment.id)[:8]}",
            branch=target_deployment.branch,
            image_tag=target_deployment.image_tag
        )

        return await self.create(
            project=target_deployment.project,
            user_id=user_id,
            trigger_data=rollback_trigger
        )

    async def append_logs(
        self,
        deployment_id: UUID,
        log_text: str,
        log_type: str = "build"
    ) -> Optional[Deployment]:
        """Append log output to build or runtime logs."""
        deployment = await self.get_by_id(deployment_id)
        if not deployment:
            return None

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        formatted_entry = f"[{timestamp}] {log_text}\n"

        if log_type == "runtime":
            deployment.runtime_logs = (deployment.runtime_logs or "") + formatted_entry
        else:
            deployment.build_logs = (deployment.build_logs or "") + formatted_entry

        await self.db.commit()
        await self.db.refresh(deployment)
        return deployment
