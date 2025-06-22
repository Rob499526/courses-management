import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import os
import sys
import pathlib
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
import jwt
from httpx import AsyncClient
from httpx import ASGITransport

from app.models import Course, Role
from app.schemas import CourseCreate, CourseUpdate
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from fastapi.testclient import TestClient
from pytest_asyncio import fixture as pytest_asyncio_fixture
from app.database import engine

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

@pytest.mark.asyncio
async def test_create_course(client, test_app, mock_auth):
    course_data = {
        "title": "New Course",
        "description": "A new course description"
    }

    response = await client.post("/courses/", json=course_data)
    assert response.status_code == 201
    created_course = response.json()
    assert created_course["title"] == course_data["title"]
    assert created_course["description"] == course_data["description"]

    response = await client.get(f"/courses/{created_course['id']}")
    assert response.status_code == 200
    retrieved_course = response.json()
    assert retrieved_course["title"] == course_data["title"]

    async with AsyncSession(test_app.state.engine) as session:
        result = await session.execute(select(Course).where(Course.id == created_course["id"]))
        course = result.scalars().first()
        assert course is not None

@pytest.mark.asyncio
async def test_create_course_validation(client, mock_auth):
    invalid_course_data = {
        "description": "A new course description"
    }

    response = await client.post("/courses/", json=invalid_course_data)
    assert response.status_code == 422

    # empty_title_data = {
    #     "title": "",
    #     "description": "A new course description"
    # }
    #
    # response = await client.post("/courses/", json=empty_title_data)
    # assert response.status_code == 422

#
# @pytest.mark.asyncio
# async def test_get_courses(client, test_course, mock_auth):
#     response = await client.get("/courses/")
#     assert response.status_code == 200
#     courses = response.json()
#     assert isinstance(courses, list)
#     assert any(course["title"] == test_course.title for course in courses)
#
#
# @pytest.mark.asyncio
# async def test_get_course(client, test_course, mock_auth):
#     response = await client.get(f"/courses/{test_course.id}")
#     assert response.status_code == 200
#     course = response.json()
#     assert course["id"] == test_course.id
#     assert course["title"] == test_course.title
#     assert course["description"] == test_course.description
#
#
# @pytest.mark.asyncio
# async def test_get_nonexistent_course(client, mock_auth):
#     response = await client.get("/courses/99999")
#     assert response.status_code == 404
#
#
# @pytest.mark.asyncio
# async def test_update_course(client, test_course, mock_auth):
#     update_data = {
#         "title": "Updated Course Title",
#         "description": "Updated course description"
#     }
#
#     response = await client.put(f"/courses/{test_course.id}", json=update_data)
#     assert response.status_code == 200
#     updated_course = response.json()
#     assert updated_course["title"] == update_data["title"]
#     assert updated_course["description"] == update_data["description"]
#
#
# @pytest.mark.asyncio
# async def test_update_nonexistent_course(client, mock_auth):
#     update_data = {
#         "title": "Updated Course Title",
#         "description": "Updated course description"
#     }
#
#     response = await client.put("/courses/99999", json=update_data)
#     assert response.status_code == 404
#
#
# @pytest.mark.asyncio
# async def test_delete_course(client, test_course, db_session, mock_auth):
#     response = await client.delete(f"/courses/{test_course.id}")
#     assert response.status_code == 200
#
#     # Verify course is deleted from database
#     result = await db_session.execute(select(Course).where(Course.id == test_course.id))
#     deleted_course = result.scalars().first()
#     assert deleted_course is None
#
#
# @pytest.mark.asyncio
# async def test_enroll_user(client, test_course, test_user, db_session, mock_auth):
#     response = await client.post(f"/courses/{test_course.id}/enroll/{test_user.id}")
#     assert response.status_code == 200
#
#     # Verify user is enrolled in course
#     result = await db_session.execute(
#         select(Course)
#         .where(Course.id == test_course.id)
#         .options(selectinload(Course.users))
#     )
#     course = result.scalars().first()
#     assert test_user in course.users
#
#
# @pytest.mark.asyncio
# async def test_enroll_user_already_enrolled(client, test_course, test_user, db_session, mock_auth):
#     # First enroll the user
#     response = await client.post(f"/courses/{test_course.id}/enroll/{test_user.id}")
#     assert response.status_code == 200
#
#     # Try to enroll again
#     response = await client.post(f"/courses/{test_course.id}/enroll/{test_user.id}")
#     assert response.status_code == 400
#     assert "already enrolled" in response.json()["detail"]