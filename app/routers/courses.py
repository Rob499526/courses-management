from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Course, Role
from app.schemas import CourseCreate, CourseRead, CourseUpdate
from app.database import get_async_session
from app.dependencies import require_role

router = APIRouter()

@router.get("/", response_model=list[CourseRead])
async def list_courses(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Course))
    return result.scalars().all()

# GET course by ID - Public
@router.get("/{course_id}", response_model=CourseRead)
async def get_course(course_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Course).where(Course.id == course_id))
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    session: AsyncSession = Depends(get_async_session),
    _ = Depends(require_role(Role.MANAGER, Role.ADMIN)),
):
    new_course = Course(**course.dict())
    session.add(new_course)
    await session.commit()
    await session.refresh(new_course)
    return new_course

@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: int,
    updated_data: CourseUpdate,
    session: AsyncSession = Depends(get_async_session),
    _ = Depends(require_role(Role.MANAGER, Role.ADMIN)),
):
    result = await session.execute(select(Course).where(Course.id == course_id))
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(course, key, value)

    await session.commit()
    await session.refresh(course)
    return course

@router.delete("/{course_id}", status_code=status.HTTP_200_OK)
async def delete_course(
    course_id: int,
    session: AsyncSession = Depends(get_async_session),
    _ = Depends(require_role(Role.ADMIN)),
):
    result = await session.execute(select(Course).where(Course.id == course_id))
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    await session.delete(course)
    await session.commit()

    return {"message": f"Course with ID {course_id} has been deleted."}