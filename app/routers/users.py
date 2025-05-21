from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.dependencies import require_role, get_current_user
from app.models import User, Role
from app.database import get_async_session, AsyncSessionLocal
from app.schemas import UserUpdateForm

router = APIRouter()

@router.get("/me")
async def read_current_user(user: User = Depends(get_current_user)):
    return user

@router.patch("/me", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def update_self(
    user_update: UserUpdateForm = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(select(User).where(User.id == current_user.id))
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_user, field, value)

    await db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Profile updated successfully"})

# ToDo: with pagination
@router.get("/users")
async def list_users(_=Depends(require_role([Role.ADMIN]))):
    db = AsyncSessionLocal()
    return db.query(User).all()
