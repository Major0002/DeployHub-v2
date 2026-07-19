"""Database initialization script."""
import asyncio

from database.base import async_engine, Base
from models.user import User
from models.project import Project
from models.deployment import Deployment


async def init_db():
    """Create all database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
