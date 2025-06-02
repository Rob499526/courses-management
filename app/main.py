from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routers import auth, users, courses
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()
app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
app = FastAPI(lifespan=lifespan)