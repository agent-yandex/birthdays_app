"""
Provides utilities for handling asynchronous database sessions.

This module initializes an asynchronous database engine and session maker
using SQLAlchemy's async capabilities. It also defines a function `get_async_session`
that yields an asynchronous session when called.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.utils.config import PG_DBNAME, PG_HOST, PG_PASSWORD, PG_PORT, PG_USER

DB_URL = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DBNAME}"

engine = create_async_engine(DB_URL)
async_session_maker = async_sessionmaker(engine)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous generator that yields an SQLAlchemy AsyncSession.

    This function asynchronously creates a session using the async_session_maker
    context manager. It yields the created session once it is acquired.

    Yields:
        AsyncSession: An SQLAlchemy AsyncSession object.
    """
    async with async_session_maker() as session:
        yield session
