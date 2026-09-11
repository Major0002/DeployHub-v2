"""Database initialization and seeding script."""
import asyncio
import os
from datetime import datetime, timezone

from sqlalchemy import select
from database.base import async_engine, AsyncSessionLocal, Base
from models.user import User
from models.project import Project
from models.deployment import Deployment
from core.security import hash_password


async def seed_data():
    """Seed initial administrator user and sample project if database is empty."""
    async with AsyncSessionLocal() as session:
        # Check if users already exist
        result = await session.execute(select(User).limit(1))
        existing_user = result.scalar_one_or_none()

        if existing_user is None:
            print("🌱 Seeding initial data...")
            admin_email = os.getenv("ADMIN_EMAIL", "admin@deployhub.dev")
            admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!")

            admin = User(
                email=admin_email,
                username="admin",
                full_name="DeployHub Administrator",
                hashed_password=hash_password(admin_password),
                role="admin",
                is_active=True,
                is_verified=True,
                is_superuser=True
            )
            session.add(admin)
            await session.flush()

            # Create sample project
            demo_project = Project(
                name="Demo API Gateway",
                slug="demo-api-gateway",
                description="High-performance API Gateway service with automated routing",
                repo_url="https://github.com/deployhub/api-gateway",
                repo_branch="main",
                language="python",
                framework="fastapi",
                build_command="pip install -r requirements.txt",
                output_directory="dist",
                status="deployed",
                health_status="healthy",
                owner_id=admin.id,
                last_deployed_at=datetime.now(timezone.utc)
            )
            session.add(demo_project)
            await session.flush()

            # Create sample successful deployment
            demo_deployment = Deployment(
                project_id=demo_project.id,
                triggered_by=admin.id,
                status="success",
                branch="main",
                commit_sha="865dca1",
                commit_message="Initial platform deployment",
                image_tag="demo-api-gateway:v2.0.0",
                build_duration_ms=42000,
                deploy_duration_ms=8500,
                production_url="http://localhost:8000/api/v1/health",
                build_logs="[INFO] Container built successfully\n[INFO] Tests passed 12/12\n",
                runtime_logs="[INFO] Service running on port 8000\n",
                deploy_metadata={"environment": "production"}
            )
            session.add(demo_deployment)

            await session.commit()
            print(f"✅ Initial admin seeded: {admin_email} / (password configured)")
            print("✅ Initial sample project and deployment created.")
        else:
            print("ℹ️ Database already contains data, skipping seed.")


async def init_db():
    """Create all database tables and seed initial data."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")
    await seed_data()


if __name__ == "__main__":
    asyncio.run(init_db())
