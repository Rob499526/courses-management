import os
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile, File, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.dependencies import require_role, get_current_user
from app.models import User, Role
from app.database import get_async_session, AsyncSessionLocal
from app.schemas import UserUpdateForm

router = APIRouter()

@router.get("/me")
async def read_current_user(user: User = Depends(get_current_user)):
    return user


@router.post("/me", response_model=None, status_code=status.HTTP_200_OK)
async def update_self(
    user_update: UserUpdateForm = Depends(UserUpdateForm.as_form()),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(select(User).where(User.id == current_user.id))
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)

    if user_update.avatar:
        content = await user_update.avatar.read()
        if not user_update.avatar.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type")
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large")

        filename = f"{uuid4().hex}_{user_update.avatar.filename}"
        avatar_dir = os.getenv("AVATAR_DIR", "avatars")
        os.makedirs(avatar_dir, exist_ok=True)
        avatar_path = os.path.join(avatar_dir, filename)

        with open(avatar_path, "wb") as f:
            f.write(content)

        update_data["avatar"] = avatar_path

    for field, value in update_data.items():
        setattr(db_user, field, value)

    await db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Profile updated successfully"})

@router.get("/users")
async def list_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: None = Depends(require_role(Role.ADMIN)),
    db: AsyncSession = Depends(get_async_session),
):
    total_query = await db.execute(select(func.count()).select_from(User))
    total = total_query.scalar()

    users_query = await db.execute(
        select(User).offset(offset).limit(limit)
    )
    users = users_query.scalars().all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "users": users
    }