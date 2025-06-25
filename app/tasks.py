from app.celery_app import celery_app
from datetime import datetime, timedelta
from sqlalchemy import select, Date
from app.database import AsyncSessionLocal
from app.models import UserCourse
import asyncio

@celery_app.task(name='app.tasks.check_course_deadlines')
def check_course_deadlines():
    async def inner():
        async with AsyncSessionLocal() as session:
            today = datetime.utcnow().date()
            target_date = today - timedelta(days=7)
            print(target_date)
            stmt = select(UserCourse).where(
                UserCourse.created_at.cast(Date) == target_date
            )
            result = await session.execute(stmt)
            user_courses = result.scalars().all()

            for uc in user_courses:
                print(f"Checking deadline for user_course user_id={uc.user_id}, course_id={uc.course_id}")

    asyncio.run(inner())
