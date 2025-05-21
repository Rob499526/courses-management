from fastapi import APIRouter, Depends
from app.models import Course, Role
from app.schemas import CourseCreate, CourseRead
from app.database import AsyncSessionLocal
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, require_role

router = APIRouter()

# READ - Everyone
@router.get("/", response_model=list[CourseRead])
async def list_courses(session: AsyncSession = Depends(AsyncSessionLocal)):
    result = await session.execute(select(Course))
    return result.scalars().all()

# CREATE - Manager and Admin
@router.post("/", response_model=CourseRead)
async def create_course(
    course: CourseCreate,
    session: AsyncSession = Depends(AsyncSessionLocal),
    user=Depends(require_role(Role.MANAGER, Role.ADMIN)),
):
    new_course = Course(**course.dict())
    session.add(new_course)
    await session.commit()
    await session.refresh(new_course)
    return new_course

# DELETE - Admin only
@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    session: AsyncSession = Depends(AsyncSessionLocal),
    user=Depends(require_role(Role.ADMIN)),
):
    result = await session.execute(select(Course).where(Course.id == course_id))
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    await session.delete(course)
    await session.commit()
    return {"message": "Course deleted"}
