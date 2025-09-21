"""FastAPI API routes for interacting with bot data."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_session

router = APIRouter()


class UserRead(BaseModel):
    """Response schema representing a stored bot user."""

    id: int
    telegram_id: int
    username: Optional[str]

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    """Payload schema for creating a new user."""

    telegram_id: int
    username: Optional[str] = None


async def get_db_session() -> AsyncSession:
    async with get_session() as session:
        yield session


@router.get("/users", response_model=List[UserRead])
async def list_users(session: AsyncSession = Depends(get_db_session)) -> List[UserRead]:
    """Return all users known to the bot."""

    result = await session.execute(select(User))
    users = result.scalars().all()
    return [UserRead.model_validate(user) for user in users]


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate, session: AsyncSession = Depends(get_db_session)
) -> UserRead:
    """Create a new user or return the existing one if present."""

    result = await session.execute(select(User).where(User.telegram_id == payload.telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=payload.telegram_id, username=payload.username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return UserRead.model_validate(user)


@router.get("/users/{telegram_id}", response_model=UserRead)
async def get_user(telegram_id: int, session: AsyncSession = Depends(get_db_session)) -> UserRead:
    """Retrieve a user by their Telegram identifier."""

    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead.model_validate(user)
