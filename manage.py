"""Utility script for running one-off management tasks."""

from __future__ import annotations

import asyncio

from app.db import Base
from app.db.session import engine


async def init_db() -> None:
    """Create database tables defined by the ORM models."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def main() -> None:
    """Entry point for management commands."""

    asyncio.run(init_db())


if __name__ == "__main__":
    main()
