from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)


def make_engine(dsn: str) -> AsyncEngine:
    """
    Creates and returns an asynchronous SQLAlchemy engine instance. This engine is
    configured to be future-proof with SQLAlchemy's latest async features, enabling
    efficient and safe database interactions. By default, it disables verbose SQL
    logging, enables pre-pinging to handle stale connections, and ensures asynchronous
    operations are managed properly.

    :param dsn: The database connection string that specifies the database location and
                credentials.
    :type dsn: str
    :return: An instance of AsyncEngine configured for asynchronous database interactions.
    :rtype: AsyncEngine
    """
    return create_async_engine(dsn, future=True, echo=False, pool_pre_ping=True)


def make_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Creates an `async_sessionmaker` configured with the provided engine and
    with `expire_on_commit` set to `False`.

    This function simplifies the setup of session makers for asynchronous
    database operations, ensuring that session state expiration on commit is
    disabled for the created sessions.

    :param engine: The asynchronous engine used to connect to the database.
    :type engine: AsyncEngine
    :return: A configured `async_sessionmaker` bound to the provided engine.
    :rtype: async_sessionmaker[AsyncSession]
    """
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def session_ctx(dsn: str) -> AsyncGenerator[AsyncSession, None]:
    """
    Create an asynchronous context manager that yields an asynchronous session
    connected to the specified database.

    This function initializes the necessary database engine and session maker,
    creates a session, and ensures proper resource cleanup.

    :param dsn: The database connection string.
    :return: An asynchronous generator that yields an AsyncSession instance.
    """
    engine = make_engine(dsn)
    sm = make_sessionmaker(engine)
    try:
        async with sm() as session:
            yield session
    finally:
        await engine.dispose()
