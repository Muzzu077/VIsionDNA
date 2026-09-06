"""
Pytest configuration and async test fixtures for VisionDNA.
"""

import asyncio
import os
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_visiondna.db"
os.environ["DEMO_MODE"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key-1234567890123456"

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.database import get_db
from app.main import app
from app.models.models import (
    User,
    UserRole,
    Environment,
    Camera,
    CameraSourceType,
    CameraStatus,
    Zone,
    ZoneType,
    MonitoredObject,
)

test_engine = create_async_engine("sqlite+aiosqlite:///./test_visiondna.db", connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create all tables before testing, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
    if os.path.exists("./test_visiondna.db"):
        try:
            os.remove("./test_visiondna.db")
        except Exception:
            pass


@pytest_asyncio.fixture
async def db_session():
    """Yield a database session for an individual test."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """FastAPI AsyncClient with database session override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    """Create and return an admin user and access token."""
    user = User(
        name="Admin Test",
        email=f"admin_{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("adminpass"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}


@pytest_asyncio.fixture
async def operator_user(db_session: AsyncSession):
    """Create and return an operator user and access token."""
    user = User(
        name="Operator Test",
        email=f"op_{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("operatorpass"),
        role=UserRole.OPERATOR,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}


@pytest_asyncio.fixture
async def viewer_user(db_session: AsyncSession):
    """Create and return a viewer user and access token."""
    user = User(
        name="Viewer Test",
        email=f"viewer_{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("viewerpass"),
        role=UserRole.VIEWER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}


@pytest_asyncio.fixture
async def sample_environment(db_session: AsyncSession):
    """Create a sample environment for test relationships."""
    env = Environment(
        name="Test Laboratory",
        description="Testing Environment",
        location="Sector 7G",
        configuration={"grid_w": 800, "grid_h": 600},
    )
    db_session.add(env)
    await db_session.commit()
    await db_session.refresh(env)
    return env
