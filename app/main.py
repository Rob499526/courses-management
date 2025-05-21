import asyncio
from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routers import auth, users, courses
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
#livespan
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
