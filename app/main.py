from fastapi import FastAPI
from app.database import engine
from app.middlewares.cors import add_cors_middleware
from app.middlewares.execution_time import add_execution_time_middleware
from app.models import Base
from app.routers import auth, users, courses, websockets
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
app = FastAPI(lifespan=lifespan)

add_cors_middleware(app)
add_execution_time_middleware(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(courses.router, prefix="/courses", tags=["courses"])
app.include_router(websockets.router)