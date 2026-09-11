"""Test fixtures and database configuration for pytest."""
import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from database.base import Base, get_db
from main import app
from models.user import User
from models.project import Project
from core.security import hash_password, create_access_token

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create in-memory SQLite async engine for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    """Yield a database session for each test, rolling back on completion."""
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    async with session_factory() as session:
        yield session
        # Clean up database tables after each test
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """HTTP async client with overridden database dependency."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session) -> User:
    """Create and return a standard test user."""
    user = User(
        email="developer@deployhub.dev",
        username="developer",
        full_name="DeployHub Developer",
        hashed_password=hash_password("DevPassword123!"),
        role="user",
        is_active=True,
        is_verified=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_admin(db_session) -> User:
    """Create and return an admin test user."""
    admin = User(
        email="admin@deployhub.dev",
        username="admin",
        full_name="DeployHub Admin",
        hashed_password=hash_password("AdminPassword123!"),
        role="admin",
        is_active=True,
        is_verified=True,
        is_superuser=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
def user_headers(test_user) -> dict:
    """Return authorization headers for test user."""
    token = create_access_token({
        "sub": str(test_user.id),
        "email": test_user.email,
        "username": test_user.username,
        "role": test_user.role
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(test_admin) -> dict:
    """Return authorization headers for admin user."""
    token = create_access_token({
        "sub": str(test_admin.id),
        "email": test_admin.email,
        "username": test_admin.username,
        "role": test_admin.role
    })
    return {"Authorization": f"Bearer {token}"}
