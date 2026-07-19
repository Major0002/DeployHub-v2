"""Project business logic service."""
import re
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from models.project import Project
from models.deployment import Deployment
from schemas.project import ProjectCreate, ProjectUpdate, ProjectStats


class ProjectService:
    """Service for project CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug from project name."""
        slug = re.sub(r"[^\w\s-]", "", name.lower())
        slug = re.sub(r"[\s_-]+", "-", slug)
        return slug.strip("-")

    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID with deployments."""
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.deployments))
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Project]:
        """Get project by slug."""
        result = await self.db.execute(
            select(Project).where(Project.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_user_projects(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects owned by a user."""
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.deployments))
            .where(Project.owner_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Project.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, user_id: UUID, project_data: ProjectCreate) -> Project:
        """Create a new project."""
        slug = self._generate_slug(project_data.name)

        # Ensure unique slug
        base_slug = slug
        counter = 1
        while await self.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        project = Project(
            name=project_data.name,
            slug=slug,
            description=project_data.description,
            repo_url=project_data.repo_url,
            repo_branch=project_data.repo_branch,
            language=project_data.language,
            framework=project_data.framework,
            build_command=project_data.build_command,
            output_directory=project_data.output_directory,
            env_vars=project_data.env_vars,
            cpu_limit=project_data.cpu_limit,
            memory_limit=project_data.memory_limit,
            owner_id=user_id
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update(self, project_id: UUID, project_data: ProjectUpdate) -> Optional[Project]:
        """Update a project."""
        project = await self.get_by_id(project_id)
        if not project:
            return None

        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete(self, project_id: UUID) -> bool:
        """Delete a project."""
        project = await self.get_by_id(project_id)
        if not project:
            return False

        await self.db.delete(project)
        await self.db.commit()
        return True

    async def get_stats(self, user_id: UUID) -> ProjectStats:
        """Get project statistics for a user."""
        # Total projects
        total_result = await self.db.execute(
            select(func.count()).select_from(Project).where(Project.owner_id == user_id)
        )
        total_projects = total_result.scalar()

        # Active projects (status != idle)
        active_result = await self.db.execute(
            select(func.count()).select_from(Project)
            .where(Project.owner_id == user_id)
            .where(Project.status != "idle")
        )
        active_projects = active_result.scalar()

        # Failed projects
        failed_result = await self.db.execute(
            select(func.count()).select_from(Project)
            .where(Project.owner_id == user_id)
            .where(Project.status == "failed")
        )
        failed_projects = failed_result.scalar()

        # Total deployments
        from models.deployment import Deployment
        deploy_result = await self.db.execute(
            select(func.count()).select_from(Deployment)
            .join(Project)
            .where(Project.owner_id == user_id)
        )
        total_deployments = deploy_result.scalar()

        # Successful deployments
        success_result = await self.db.execute(
            select(func.count()).select_from(Deployment)
            .join(Project)
            .where(Project.owner_id == user_id)
            .where(Deployment.status == "success")
        )
        successful_deployments = success_result.scalar()

        # Failed deployments
        failed_deploy_result = await self.db.execute(
            select(func.count()).select_from(Deployment)
            .join(Project)
            .where(Project.owner_id == user_id)
            .where(Deployment.status == "failed")
        )
        failed_deployments = failed_deploy_result.scalar()

        return ProjectStats(
            total_projects=total_projects,
            active_projects=active_projects,
            failed_projects=failed_projects,
            total_deployments=total_deployments,
            successful_deployments=successful_deployments,
            failed_deployments=failed_deployments
        )
