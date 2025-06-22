import sys
import pytest
from unittest.mock import patch


import pathlib

@pytest.fixture(autouse=True)
def patch_send_enrollment_email(monkeypatch):
    def fake_send_enrollment_email(email, course_title):
        return None
    monkeypatch.setattr("app.routers.courses.send_enrollment_email", fake_send_enrollment_email)


from datetime import datetime, timedelta, timezone
import pytest
import jwt
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from pytest_asyncio import fixture

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database import Base, get_async_session
from app.models import User, Course, Role
from app.dependencies import get_current_user, require_role
from app.routers import courses, users, auth





@fixture(scope="session")
async def test_db():
    # Use in-memory SQLite for tests
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", echo=False, future=True
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


import jwt
from httpx import AsyncClient, ASGITransport
import pytest_asyncio

@pytest_asyncio.fixture
async def client(test_app):
    token = jwt.encode(
        {
            "sub": "testuser",
            "email": "testuser@example.com",
            "roles": ["admin"],
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        },
        "test-secret-key",
        algorithm="HS256"
    )
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        async_client.headers.update({"Authorization": f"Bearer {token}"})
        yield async_client

import pytest_asyncio

@pytest_asyncio.fixture
async def db_session(test_db):
    test_engine = test_db
    TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

@fixture(scope="function")
async def test_user(db_session):
    user = User(
        username="testuser",
        email="testuser@example.com",
        role=Role.ADMIN,
        auth0_id="testuser"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


import pytest_asyncio

@pytest_asyncio.fixture
async def test_course(db_session):
    course = Course(
        title="Test Course",
        description="A test course description"
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    return course


@fixture(scope="function")
def mock_auth():
    async def override_get_current_user():
        return User(
            id=1,
            username="testuser",
            email="testuser@example.com",
            role=Role.ADMIN,
            auth0_id="testuser"
        )
    return override_get_current_user


@fixture(scope="function")
async def test_app(mock_auth, test_db):
    test_engine = test_db
    TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    app = FastAPI()
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(users.router, prefix="/users", tags=["users"])
    app.include_router(courses.router, prefix="/courses", tags=["courses"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.dependency_overrides[get_current_user] = mock_auth
    app.dependency_overrides[require_role] = lambda *args: lambda x: x

    async def get_test_session():
        async with TestSessionLocal() as session:
            yield session
    app.dependency_overrides[get_async_session] = get_test_session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    app.state.engine = test_engine
    yield app
    app.dependency_overrides.clear()