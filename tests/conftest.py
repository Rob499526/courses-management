import sys
import pathlib
from datetime import datetime, timedelta, timezone
import pytest
import jwt
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from pytest_asyncio import fixture

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from app.database import engine, Base, get_async_session
from app.models import User, Course, Role
from app.dependencies import get_current_user, require_role
from app.routers import courses, users, auth





@fixture(scope="session")
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    async with AsyncSession(engine) as session:
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


@fixture(scope="function")
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
async def test_app(mock_auth):
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
        async with AsyncSession(engine) as session:
            yield session

    app.dependency_overrides[get_async_session] = get_test_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    app.state.engine = engine
    yield app
    app.dependency_overrides.clear()