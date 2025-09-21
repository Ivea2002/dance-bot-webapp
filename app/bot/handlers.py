"""Telegram bot handlers powered by aiogram."""

from __future__ import annotations

from typing import Optional

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_session

router = Router(name="bot-handlers")


async def get_or_create_user(
    session: AsyncSession, telegram_id: int, username: Optional[str]
) -> User:
    """Retrieve a user by their Telegram identifier or create one if it does not exist."""

    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is not None:
        return user

    user = User(telegram_id=telegram_id, username=username)
    session.add(user)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one()
    else:
        await session.refresh(user)

    return user


@router.message(F.text)
async def echo_message(message: Message) -> None:
    """Basic echo handler that stores user metadata before responding."""

    if message.from_user is None:
        await message.answer("Hello! I couldn't determine your Telegram user data.")
        return

    async with get_session() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
        )

    greeting = (
        f"Hello {user.username or 'there'}! You said: {message.text}."
        " I have recorded your visit."
    )
    await message.answer(greeting)
